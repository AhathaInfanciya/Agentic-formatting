import math
import json
def add(a, b):
    return a + b


def subtract(a, b):
    if a > b:
        return a - b
    else:
        return a + b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        return "divide by zero possible"
    else:
        return a / b


def square_root(a):
    return math.sqrt(a)


def cube_root(b):
    return b**3


def linear(m, x, c):
    a = m * x
    return a + c


def main():

    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))

    print("Addition:", add(a, b))
    print("Subtraction:", subtract(a, b))
    print("Multiplication:", multiply(a, b))
    print("Division:", divide(a, b))
    print("Square Root of first number:", square_root(a))
    print("Cube Root of second number:", cube_root(b))

    m = float(input("Enter m value for linear equation: "))
    x = float(input("Enter x value for linear equation: "))
    c = float(input("Enter c value for linear equation: "))

    print("Linear Equation Result:", linear(m, x, c))


if __name__ == "__main__":
    main()
