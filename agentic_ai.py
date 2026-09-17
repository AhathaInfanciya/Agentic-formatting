import json
import os
import re
import subprocess
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ConfigurationError(Exception):
    pass


api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ConfigurationError("ANTHROPIC_API_KEY not found")


client = Anthropic(api_key=api_key)

COVERAGE_THRESHOLD = 80.0
MAX_RETRIES = 3

FIXED_TEST_START = "<<<FIXED_TEST_START>>>"
FIXED_TEST_END = "<<<FIXED_TEST_END>>>"


def clean_llm_code(text):
    text = text.strip()
    text = re.sub(r"^```(?:python)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def call_claude(prompt):
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    output = ""
    for block in response.content:
        if hasattr(block, "text"):
            output += block.text

    return clean_llm_code(output)


def fix_module_imports(test_code, module_name):
    """Replace any placeholder import with the real module import."""
    for placeholder in ("module_under_test", "source", "app"):
        test_code = test_code.replace(
            f"from {placeholder} import", f"from {module_name} import"
        )
    return test_code


def run_pytest(test_file, extra_args=None):
    cmd = ["pytest", str(test_file), "-v"] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print(result.stdout)
    return result


def run_coverage(test_file, module_name, term_missing=False):
    cmd = [
        "pytest",
        str(test_file),
        f"--cov={module_name}",
        "--cov-report=json",
    ]
    if term_missing:
        cmd.append("--cov-report=term-missing")

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print(result.stdout)

    with open("coverage.json", "r", encoding="utf-8") as f:
        report = json.load(f)

    coverage = report["totals"]["percent_covered"]

    file_key = next(
        (k for k in report["files"] if k.endswith(f"{module_name}.py")), None
    )
    if file_key is None:
        raise Exception(f"Coverage entry not found for {module_name}.py")

    missing_lines = report["files"][file_key]["missing_lines"]
    return coverage, missing_lines


def write_failure_log(module_name, error_output, analysis):
    with open(f"pytest_failure_{module_name}.log", "w", encoding="utf-8") as f:
        f.write(error_output)
        f.write("\n\n")
        f.write(analysis)


def analyze_failure(error_output, source_code, module_name):
    """
    Single call that both diagnoses the failure AND, if it's a Test Bug,
    returns a corrected test file in the same response — avoids a second
    round trip to regenerate the test separately.
    """
    prompt = f"""
The generated test failed.

Error:
{error_output}

Source Code:
{source_code}

Determine whether the failure is:

1. Code Bug
2. Test Bug
3. Requirement Ambiguity

Respond in exactly this format:

Classification: <Code Bug | Test Bug | Requirement Ambiguity>
Root Cause: <text>
Suggested Fix: <text>

If Classification is "Test Bug", after the above, ALSO include a corrected
pytest test file, wrapped EXACTLY like this (no markdown fences):

{FIXED_TEST_START}
import {module_name} as calc
...corrected full test file...
{FIXED_TEST_END}
"""
    return call_claude(prompt)


def extract_fixed_test(analysis):
    """Pull the corrected test code out of an analyze_failure response, if present."""
    match = re.search(
        rf"{re.escape(FIXED_TEST_START)}(.*?){re.escape(FIXED_TEST_END)}",
        analysis,
        flags=re.DOTALL,
    )
    return clean_llm_code(match.group(1)) if match else None


python_files = [
    p
    for p in Path(".").glob("*.py")
    if not p.name.startswith("test_") and p.name != "agentic_ai.py"
]

if not python_files:
    raise ConfigurationError("No source Python files found.")

results = []

for python_file in python_files:
    module_name = python_file.stem
    source_code = python_file.read_text(encoding="utf-8")
    test_file = Path(f"test_{module_name}.py")

    print(f"\nProcessing: {python_file.name}")

    if not test_file.exists():
        prompt = f"""
Generate pytest unit tests for {python_file.name}.

IMPORTANT:

Use:

import {module_name} as calc

Do not use:

module_under_test
source
app
your_module

Requirements:

1. Cover all functions
2. Cover positive scenarios
3. Cover negative scenarios
4. Cover edge cases
5. Cover exception scenarios
6. Use pytest
7. Return ONLY Python code

8. Do not include markdown code fences

Source Code:

{source_code}
"""
        generated_test_code = call_claude(prompt)
        generated_test_code = fix_module_imports(generated_test_code, module_name)
        test_file.write_text(generated_test_code, encoding="utf-8")
        print(f"Generated {test_file.name}")
    else:
        print(f"Using existing {test_file.name}")

    print("\nRunning pytest...")
    pytest_result = run_pytest(test_file)

    if pytest_result.returncode != 0:
            print("Generated tests failed")

            error_output = pytest_result.stdout + "\n" + pytest_result.stderr
            analysis = analyze_failure(error_output, source_code, module_name)

            if "test bug" in analysis.lower():
                print("Detected Test Bug. Applying corrected test...")

                fixed_test_code = extract_fixed_test(analysis)

                if fixed_test_code:
                    test_file.write_text(
                        fixed_test_code,
                        encoding="utf-8",
                    )

                    pytest_result = run_pytest(test_file)

                    if pytest_result.returncode == 0:
                        print("Regenerated test passed")

                        print("\nCalculating coverage...")
                        coverage, missing_lines = run_coverage(
                            test_file,
                            module_name,
                            term_missing=True,
                        )

                        retry_count = 0
                        status = None

                        # continue normal flow
                    else:
                        print("Corrected test still failed")

            print("\nFailure Analysis:")
            print(analysis)

            write_failure_log(
                module_name,
                error_output,
                analysis,
            )

            results.append(
                f"{python_file.name}: FAIL"
            )

            continue

    print("\nCalculating coverage...")
    coverage, missing_lines = run_coverage(test_file, module_name, term_missing=True)

    retry_count = 0
    status = None

    while coverage < COVERAGE_THRESHOLD and retry_count < MAX_RETRIES:
        print(f"\nCoverage {coverage:.2f}% is below {COVERAGE_THRESHOLD}%")

        extra_prompt = f"""
Current coverage is {coverage:.2f}%.

Missing lines:

{missing_lines}

Source Code:

{source_code}

Generate ADDITIONAL pytest test cases.

If uncovered lines are inside main():

1. Mock builtins.input
2. Call main()
3. Capture console output

Use:

import {module_name} as calc

Return ONLY executable Python code.
"""
        additional_tests = call_claude(extra_prompt)

        if additional_tests.strip():
            with open(test_file, "a", encoding="utf-8") as f:
                f.write("\n\n")
                f.write(additional_tests)
            print("Additional tests appended")

        pytest_retry = run_pytest(test_file)

        if pytest_retry.returncode != 0:
            error_output = pytest_retry.stdout + "\n" + pytest_retry.stderr
            analysis = analyze_failure(error_output, source_code, module_name)

            if "test bug" in analysis.lower():
                print("Detected Test Bug. Applying corrected test...")
                fixed_test_code = extract_fixed_test(analysis)

                if fixed_test_code:
                    test_file.write_text(fixed_test_code, encoding="utf-8")
                    pytest_result = run_pytest(test_file)

                    if pytest_result.returncode == 0:
                        print("Regenerated test passed")
                        coverage, missing_lines = run_coverage(test_file, module_name)
                        retry_count += 1
                        continue

            print("\nFailure Analysis:")
            print(analysis)
            write_failure_log(module_name, error_output, analysis)

            status = "FAIL"
            print("Generated tests failed")
            break

        coverage, missing_lines = run_coverage(test_file, module_name)
        retry_count += 1

    if status is None:
        if coverage >= COVERAGE_THRESHOLD:
            status = "PASS"
            print(f"\n✅ Coverage: {coverage:.2f}%")
        else:
            status = "FAIL"
            print("\n❌ Coverage threshold not achieved")

    results.append(f"{python_file.name}: {status} | Coverage={coverage:.2f}%")

print("\nRunning Black...")
subprocess.run(["black", "."], check=False)

print("\nRunning Ruff...")
subprocess.run(["ruff", "check", ".", "--fix"], capture_output=True, text=True, check=False)

summary_lines = "\n".join(results)
report_content = f"""# Code Quality Report

Coverage Threshold: {COVERAGE_THRESHOLD}%

Results:

{summary_lines}
"""

Path("quality_report.md").write_text(report_content, encoding="utf-8")

print("\n✅ quality_report.md generated")
print("\n✅ Agent Execution Completed")