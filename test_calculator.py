import math

import pytest

import calculator as calc


class TestAdd:
    def test_add_positive_numbers(self):
        assert calc.add(2, 3) == 5

    def test_add_negative_numbers(self):
        assert calc.add(-2, -3) == -5

    def test_add_mixed_sign_numbers(self):
        assert calc.add(-5, 10) == 5

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
        # Based on implementation, when a <= b, it returns a + b
        assert calc.subtract(5, 10) == 15

    def test_subtract_a_equal_b_returns_sum(self):
        assert calc.subtract(5, 5) == 10

    def test_subtract_negative_numbers(self):
        assert calc.subtract(-5, -10) == 5

    def test_subtract_zero(self):
        assert calc.subtract(0, 0) == 0

    def test_subtract_floats(self):
        assert calc.subtract(5.5, 2.5) == 3.0


class TestMultiply:
    def test_multiply_positive_numbers(self):
        assert calc.multiply(3, 4) == 12

    def test_multiply_negative_numbers(self):
        assert calc.multiply(-3, -4) == 12

    def test_multiply_mixed_sign_numbers(self):
        assert calc.multiply(-3, 4) == -12

    def test_multiply_by_zero(self):
        assert calc.multiply(5, 0) == 0

    def test_multiply_floats(self):
        assert calc.multiply(2.5, 4) == 10.0

    def test_multiply_large_numbers(self):
        assert calc.multiply(10**5, 10**5) == 10**10


class TestDivide:
    def test_divide_positive_numbers(self):
        assert calc.divide(10, 2) == 5

    def test_divide_negative_numbers(self):
        assert calc.divide(-10, -2) == 5

    def test_divide_mixed_sign_numbers(self):
        assert calc.divide(-10, 2) == -5

    def test_divide_by_zero_returns_message(self):
        assert calc.divide(10, 0) == "divide by zero possible"

    def test_divide_zero_by_number(self):
        assert calc.divide(0, 5) == 0

    def test_divide_floats(self):
        assert calc.divide(7.5, 2.5) == 3.0

    def test_divide_result_is_float(self):
        result = calc.divide(10, 4)
        assert result == 2.5


class TestSquareRoot:
    def test_square_root_positive_number(self):
        assert calc.square_root(9) == 3.0

    def test_square_root_zero(self):
        assert calc.square_root(0) == 0.0

    def test_square_root_float(self):
        assert math.isclose(calc.square_root(2.25), 1.5)

    def test_square_root_large_number(self):
        assert calc.square_root(10000) == 100.0

    def test_square_root_negative_raises_error(self):
        with pytest.raises(ValueError):
            calc.square_root(-4)


class TestCubeRoot:
    def test_cube_root_positive_number(self):
        assert calc.cube_root(2) == 8

    def test_cube_root_zero(self):
        assert calc.cube_root(0) == 0

    def test_cube_root_negative_number(self):
        assert calc.cube_root(-3) == -27

    def test_cube_root_float(self):
        assert calc.cube_root(1.5) == 3.375

    def test_cube_root_one(self):
        assert calc.cube_root(1) == 1


class TestLinear:
    def test_linear_positive_values(self):
        assert calc.linear(2, 3, 4) == 10

    def test_linear_zero_slope(self):
        assert calc.linear(0, 5, 3) == 3

    def test_linear_zero_x(self):
        assert calc.linear(5, 0, 3) == 3

    def test_linear_zero_intercept(self):
        assert calc.linear(2, 3, 0) == 6

    def test_linear_negative_values(self):
        assert calc.linear(-2, 3, -4) == -10

    def test_linear_all_zeros(self):
        assert calc.linear(0, 0, 0) == 0

    def test_linear_floats(self):
        assert calc.linear(1.5, 2.0, 0.5) == 3.5


class TestMain:
    def test_main_executes_successfully(self, monkeypatch, capsys):
        inputs = iter(["4", "2", "3", "5", "1"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        calc.main()
        captured = capsys.readouterr()
        assert "Addition:" in captured.out
        assert "Subtraction:" in captured.out
        assert "Multiplication:" in captured.out
        assert "Division:" in captured.out
        assert "Square Root of first number:" in captured.out
        assert "Cube Root of second number:" in captured.out
        assert "Linear Equation Result:" in captured.out

    def test_main_with_zero_second_number_for_division(self, monkeypatch, capsys):
        inputs = iter(["10", "0", "1", "2", "3"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        calc.main()
        captured = capsys.readouterr()
        assert "divide by zero possible" in captured.out

    def test_main_with_negative_numbers(self, monkeypatch, capsys):
        inputs = iter(["-4", "-2", "3", "5", "1"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        with pytest.raises(ValueError):
            calc.main()
