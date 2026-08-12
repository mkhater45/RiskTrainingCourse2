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
        
        #call the function being wrapped
        result = func(*args, **kwargs)
        
        #get the timestamp after the function call
        finish = time.time()
        
        #print the function name and how many seconds it took to execute
        duration = round(finish - start,5)
        
        print(f"Call to {func.__name__} took {duration} seconds")
        
        return result

    return wrapper


def log_call(func):
    """Print the function name on every call."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} has been logged!")
        return func(*args, **kwargs)

    return wrapper
