import time
import sys
import io

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

class SuppressStdout:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout