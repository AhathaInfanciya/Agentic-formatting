import math

import pytest

import calculator as calc


class TestAdd:
    def test_add_positive_numbers(self):
        assert calc.add(2, 3) == 5

    def test_add_negative_numbers(self):
        assert calc.add(-2, -3) == -5

    def test_add_positive_and_negative(self):
        assert calc.add(5, -3) == 2

    def test_add_zero(self):
        assert calc.add(0, 0) == 0

    def test_add_floats(self):
        assert calc.add(2.5, 3.5) == 6.0

    def test_add_large_numbers(self):
        assert calc.add(10**10, 10**10) == 2 * 10**10


class TestSubtract:
    def test_subtract_a_greater_than_b(self):
        assert calc.subtract(10, 5) == 5

    def test_subtract_a_less_than_b_returns_sum(self):
        # Based on implementation, if a <= b, it adds instead
        assert calc.subtract(5, 10) == 15

    def test_subtract_a_equal_b_returns_sum(self):
        assert calc.subtract(5, 5) == 10

    def test_subtract_negative_numbers(self):
        assert calc.subtract(-5, -10) == 5

    def test_subtract_zero(self):
        assert calc.subtract(0, 0) == 0

    def test_subtract_floats(self):
        assert calc.subtract(10.5, 5.5) == 5.0


class TestMultiply:
    def test_multiply_positive_numbers(self):
        assert calc.multiply(3, 4) == 12

    def test_multiply_negative_numbers(self):
        assert calc.multiply(-3, -4) == 12

    def test_multiply_positive_and_negative(self):
        assert calc.multiply(3, -4) == -12

    def test_multiply_by_zero(self):
        assert calc.multiply(5, 0) == 0

    def test_multiply_floats(self):
        assert calc.multiply(2.5, 4) == 10.0

    def test_multiply_by_one(self):
        assert calc.multiply(7, 1) == 7


class TestDivide:
    def test_divide_positive_numbers(self):
        assert calc.divide(10, 2) == 5

    def test_divide_negative_numbers(self):
        assert calc.divide(-10, -2) == 5

    def test_divide_positive_and_negative(self):
        assert calc.divide(10, -2) == -5

    def test_divide_by_zero_returns_message(self):
        assert calc.divide(10, 0) == "divide by zero possible"

    def test_divide_zero_by_zero_returns_message(self):
        assert calc.divide(0, 0) == "divide by zero possible"

    def test_divide_zero_by_number(self):
        assert calc.divide(0, 5) == 0

    def test_divide_floats(self):
        assert calc.divide(10.5, 2) == 5.25

    def test_divide_result_is_float(self):
        result = calc.divide(10, 3)
        assert isinstance(result, float)


class TestSquareRoot:
    def test_square_root_positive_number(self):
        assert calc.square_root(4) == 2.0

    def test_square_root_zero(self):
        assert calc.square_root(0) == 0.0

    def test_square_root_perfect_square(self):
        assert calc.square_root(9) == 3.0

    def test_square_root_non_perfect_square(self):
        result = calc.square_root(2)
        assert math.isclose(result, 1.4142135623730951)

    def test_square_root_float(self):
        assert calc.square_root(2.25) == 1.5

    def test_square_root_negative_raises_error(self):
        with pytest.raises(ValueError):
            calc.square_root(-4)

    def test_square_root_large_number(self):
        assert calc.square_root(1000000) == 1000.0


class TestCubeRoot:
    def test_cube_root_positive_number(self):
        assert calc.cube_root(3) == 27

    def test_cube_root_zero(self):
        assert calc.cube_root(0) == 0

    def test_cube_root_negative_number(self):
        assert calc.cube_root(-3) == -27

    def test_cube_root_one(self):
        assert calc.cube_root(1) == 1

    def test_cube_root_float(self):
        assert calc.cube_root(2.0) == 8.0

    def test_cube_root_fraction(self):
        assert calc.cube_root(0.5) == 0.125


class TestLinear:
    def test_linear_positive_values(self):
        assert calc.linear(2, 3, 4) == 10

    def test_linear_zero_slope(self):
        assert calc.linear(0, 5, 10) == 10

    def test_linear_zero_intercept(self):
        assert calc.linear(3, 4, 0) == 12

    def test_linear_negative_values(self):
        assert calc.linear(-2, 3, 4) == -2

    def test_linear_all_zero(self):
        assert calc.linear(0, 0, 0) == 0

    def test_linear_float_values(self):
        assert calc.linear(1.5, 2.0, 0.5) == 3.5

    def test_linear_negative_x(self):
        assert calc.linear(2, -3, 4) == -2

    def test_linear_negative_c(self):
        assert calc.linear(2, 3, -4) == 2


class TestEdgeCasesAndExceptions:
    def test_add_with_strings_raises_type_error(self):
        with pytest.raises(TypeError):
            calc.add("a", 1)

    def test_multiply_with_none_raises_type_error(self):
        with pytest.raises(TypeError):
            calc.multiply(None, 5)

    def test_divide_with_string_raises_type_error(self):
        with pytest.raises(TypeError):
            calc.divide("10", 2)

    def test_square_root_with_string_raises_type_error(self):
        with pytest.raises(TypeError):
            calc.square_root("4")

    def test_cube_root_with_string_raises_type_error(self):
        with pytest.raises(TypeError):
            calc.cube_root("2")

    def test_linear_with_missing_argument_raises_type_error(self):
        with pytest.raises(TypeError):
            calc.linear(2, 3)

    def test_subtract_with_none_raises_type_error(self):
        with pytest.raises(TypeError):
            calc.subtract(None, 5)

    def test_add_extra_argument_raises_type_error(self):
        with pytest.raises(TypeError):
            calc.add(1, 2, 3)


from unittest.mock import patch


def test_main_basic_execution(capsys):
    inputs = iter(["10", "5", "2", "3", "1"])  # a  # b  # m  # x  # c

    with patch("builtins.input", lambda prompt="": next(inputs)):
        calc.main()

    captured = capsys.readouterr()
    output = captured.out

    assert "Addition: 15.0" in output
    assert "Subtraction: 5.0" in output
    assert "Multiplication: 50.0" in output
    assert "Division: 2.0" in output
    assert "Square Root of first number:" in output
    assert "Cube Root of second number:" in output
    assert "Linear Equation Result: 7.0" in output


def test_main_division_by_zero(capsys):
    inputs = iter(["10", "0", "1", "1", "1"])  # a  # b  # m  # x  # c

    with patch("builtins.input", lambda prompt="": next(inputs)):
        calc.main()

    captured = capsys.readouterr()
    output = captured.out

    assert "Division: divide by zero possible" in output


def test_main_subtract_less_than(capsys):
    inputs = iter(["2", "10", "1", "1", "1"])  # a  # b  # m  # x  # c

    with patch("builtins.input", lambda prompt="": next(inputs)):
        calc.main()

    captured = capsys.readouterr()
    output = captured.out

    assert "Subtraction: 12.0" in output


def test_main_negative_numbers(capsys):
    inputs = iter(["-4", "-2", "3", "2", "-1"])  # a  # b  # m  # x  # c

    with patch("builtins.input", lambda prompt="": next(inputs)):
        calc.main()

    captured = capsys.readouterr()
    output = captured.out

    assert "Addition: -6.0" in output
    assert "Multiplication: 8.0" in output
    assert "Linear Equation Result: 5.0" in output
