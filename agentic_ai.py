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


def clean_llm_code(text):
    text = text.strip()

    text = re.sub(
        r"^```(?:python)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    return text.strip()


def call_claude(prompt):
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    output = ""

    for block in response.content:
        if hasattr(block, "text"):
            output += block.text

    return clean_llm_code(output)


def analyze_failure(error_output, source_code):
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

Provide:

Classification:
Root Cause:
Suggested Fix:

Return plain text only.
"""

    return call_claude(prompt)


python_files = []

for python_file in Path(".").glob("*.py"):
    if python_file.name.startswith("test_"):
        continue

    if python_file.name in [
        "agentic_ai.py",
    ]:
        continue

    python_files.append(python_file)

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

        generated_test_code = generated_test_code.replace(
            "from module_under_test import",
            f"from {module_name} import",
        )

        generated_test_code = generated_test_code.replace(
            "from source import",
            f"from {module_name} import",
        )

        generated_test_code = generated_test_code.replace(
            "from app import",
            f"from {module_name} import",
        )

        generated_test_code = clean_llm_code(generated_test_code)

        test_file.write_text(
            generated_test_code,
            encoding="utf-8",
        )

        print(f"Generated {test_file.name}")

    else:
        print(f"Using existing {test_file.name}")

    print("\nRunning pytest...")

    pytest_result = subprocess.run(
        ["pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
        check=False
    )

    print(pytest_result.stdout)

    if pytest_result.returncode != 0:
     print("Generated tests failed")

     error_output = (
        pytest_result.stdout
        + "\n"
        + pytest_result.stderr
    )

     analysis = analyze_failure(
        error_output,
        source_code,
    )

     print("\nFailure Analysis:")
     print(analysis)

     with open(
        f"pytest_failure_{module_name}.log",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(error_output)
        f.write("\n\n")
        f.write(analysis)

     results.append(
        f"{python_file.name}: FAIL"
    )

     continue

    print("\nCalculating coverage...")

    coverage_result = subprocess.run(
    [
        "pytest",
        str(test_file),
        f"--cov={module_name}",
        "--cov-report=json",
        "--cov-report=term-missing",
    ],
    capture_output=True,
    text=True,
    check=True,
)

    print(coverage_result.stdout)


    with open(
        "coverage.json",
        "r",
        encoding="utf-8",
    ) as f:
        report = json.load(f)

    coverage = report["totals"]["percent_covered"]

    file_key = None
    for key in report["files"]:
        if key.endswith(python_file.name):
            file_key = key
            break

    if file_key is None:
        raise Exception(f"Coverage entry not found for {python_file.name}")

    missing_lines = report["files"][file_key]["missing_lines"]

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

        additional_tests = clean_llm_code(additional_tests)

        if additional_tests.strip():
            with open(
                test_file,
                "a",
                encoding="utf-8",
            ) as f:
                f.write("\n\n")
                f.write(additional_tests)

            print("Additional tests appended")

        pytest_retry = subprocess.run(
            [
                "pytest",
                str(test_file),
                "-v",
            ],
            capture_output=True,
            text=True,
            check=False
        )

        print(pytest_retry.stdout)

        if pytest_retry.returncode != 0:
            error_output = (
                pytest_retry.stdout
                + "\n"
                + pytest_retry.stderr
            )

            analysis = analyze_failure(
                error_output,
                source_code,
            )

            print("\nFailure Analysis:")
            print(analysis)

            with open(
                f"pytest_failure_{module_name}.log",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(error_output)
                f.write("\n\n")
                f.write(analysis)

            status = "FAIL"
            print("Generated tests failed")
            break

        coverage_result = subprocess.run(
    [
        "pytest",
        str(test_file),
        f"--cov={module_name}",
        "--cov-report=json",
    ],
    capture_output=True,
    text=True,
    check=True,
)

        print(coverage_result.stdout)

        with open(
            "coverage.json",
            "r",
            encoding="utf-8",
        ) as f:
            report = json.load(f)

        coverage = report["totals"]["percent_covered"]

        missing_lines = report["files"][file_key]["missing_lines"]

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

subprocess.run(
    ["black", "."],
    check=False,
)



print("\nRunning Ruff...")

ruff_result = subprocess.run(
    [
        "ruff",
        "check",
        ".",
        "--fix",
    ],
    capture_output=True,
    text=True,
    check=False,
)




summary_lines = "\n".join(results)

report_content = f"""# Code Quality Report

Coverage Threshold: {COVERAGE_THRESHOLD}%

Results:

{summary_lines}
"""

Path("quality_report.md").write_text(
    report_content,
    encoding="utf-8",
)

print("\n✅ quality_report.md generated")
print("\n✅ Agent Execution Completed")
