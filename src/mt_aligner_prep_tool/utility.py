import time
from functools import wraps


def execution_time(custom_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            name = custom_name if custom_name else func.__name__
            print(f"Total time taken for {name}: {end_time - start_time} seconds.")
            return result

        return wrapper

    return decorator
