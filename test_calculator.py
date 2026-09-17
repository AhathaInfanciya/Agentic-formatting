import math

import pytest

import calculator as calc

# ---------- add ----------


def test_add_positive_numbers():
    assert calc.add(2, 3) == 5


def test_add_negative_numbers():
    assert calc.add(-2, -3) == -5


def test_add_positive_and_negative():
    assert calc.add(-2, 3) == 1


def test_add_zero():
    assert calc.add(0, 0) == 0


def test_add_floats():
    assert calc.add(2.5, 3.5) == 6.0


# ---------- subtract ----------
# Note: subtract has unusual logic:
# if a > b: return a - b else return a + b


def test_subtract_a_greater_than_b():
    assert calc.subtract(5, 3) == 2


def test_subtract_a_less_than_b():
    assert calc.subtract(3, 5) == 8


def test_subtract_a_equal_b():
    assert calc.subtract(5, 5) == 10


def test_subtract_negative_numbers():
    assert calc.subtract(-5, -3) == -8


def test_subtract_zero_case():
    assert calc.subtract(0, 0) == 0


# ---------- multiply ----------


def test_multiply_positive_numbers():
    assert calc.multiply(3, 4) == 12


def test_multiply_negative_numbers():
    assert calc.multiply(-3, -4) == 12


def test_multiply_positive_and_negative():
    assert calc.multiply(-3, 4) == -12


def test_multiply_by_zero():
    assert calc.multiply(5, 0) == 0


def test_multiply_floats():
    assert calc.multiply(2.5, 2) == 5.0


# ---------- divide ----------


def test_divide_positive_numbers():
    assert calc.divide(10, 2) == 5


def test_divide_negative_numbers():
    assert calc.divide(-10, -2) == 5


def test_divide_positive_and_negative():
    assert calc.divide(-10, 2) == -5


def test_divide_by_zero_returns_message():
    assert calc.divide(10, 0) == "divide by zero possible"


def test_divide_zero_by_number():
    assert calc.divide(0, 5) == 0


def test_divide_floats():
    assert calc.divide(5.0, 2.0) == 2.5


# ---------- square_root ----------


def test_square_root_positive_number():
    assert calc.square_root(16) == 4.0


def test_square_root_zero():
    assert calc.square_root(0) == 0.0


def test_square_root_negative_number():
    assert calc.square_root(-4) == "neagative number has no sqrt value"


def test_square_root_non_perfect_square():
    assert math.isclose(calc.square_root(2), math.sqrt(2))


def test_square_root_float_input():
    assert math.isclose(calc.square_root(6.25), 2.5)


# ---------- cube_root ----------
# Note: cube_root actually computes cube (b**3), not cube root.


def test_cube_root_positive_number():
    assert calc.cube_root(3) == 27


def test_cube_root_negative_number():
    assert calc.cube_root(-3) == -27


def test_cube_root_zero():
    assert calc.cube_root(0) == 0


def test_cube_root_float_input():
    assert calc.cube_root(2.5) == 15.625


def test_cube_root_one():
    assert calc.cube_root(1) == 1


# ---------- edge cases / exception scenarios ----------


def test_add_with_invalid_type_raises_typeerror():
    with pytest.raises(TypeError):
        calc.add("a", 2)


def test_subtract_with_invalid_type_raises_typeerror():
    with pytest.raises(TypeError):
        calc.subtract("a", 2)


def test_multiply_with_invalid_type_raises_typeerror():
    with pytest.raises(TypeError):
        calc.multiply("a", 2)


def test_divide_with_invalid_type_raises_typeerror():
    with pytest.raises(TypeError):
        calc.divide("a", 2)


def test_square_root_with_invalid_type_raises_typeerror():
    with pytest.raises(TypeError):
        calc.square_root("a")


def test_cube_root_with_invalid_type_raises_typeerror():
    with pytest.raises(TypeError):
        calc.cube_root("a")
