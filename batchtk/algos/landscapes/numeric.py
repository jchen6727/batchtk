import numpy


def quadratic(x, a=1, b=0, c=0):
    """Quadratic function.
    minima occurs at x = -b/(2a)

    Args:
        x (float or np.ndarray): Input value(s).
        a (float): Coefficient of x^2. Default is 1.
        b (float): Coefficient of x. Default is 0.
        c (float): Constant term. Default is 0.

    Returns:
        float or np.ndarray: Output value(s) of the quadratic function.
    """
    return a * x**2 + b * x + c

def rosenbrock(x, A=1, B=100):
    """Vectorized implementation of the n-dimensional Rosenbrock function.
    minima occurs when x[i] = A and x[i+1] = A**2 for all i

    Parameters:
    - x: numpy.ndarray, input array of n values.
    - A: float, default is 1.
    - B: float, default is 100.

    Returns:
    - float, the computed Rosenbrock function value.
    """
    return numpy.sum(B * (x[1:] - x[:-1] ** 2) ** 2 + (A - x[:-1]) ** 2)

def rastrigin(x):
    """Vectorized implementation of the n-dimensional Rastrigin function.
    minima occurs when x[i] = 0 for all i

    Parameters:
    - x: numpy.ndarray, input array of n values.

    Returns:
    - float, the computed Rastrigin function value.
    """
    n = len(x)
    return 10 * n + numpy.sum(x**2 - 10 * numpy.cos(2 * numpy.pi * x))