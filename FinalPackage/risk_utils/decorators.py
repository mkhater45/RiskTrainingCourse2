"""Generic decorators: @timer and @log_call.

Introduced on Day 2 as the first payoff of "functions are just values" -
apply the same logic (timing, logging) to any function with one line.
"""

import time
from functools import wraps


def timer(func):
    """Print how long func took to run."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.4f}s")
        return result

    return wrapper


def log_call(func):
    """Print the function name and arguments on every call."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with {args}")
        return func(*args, **kwargs)

    return wrapper
