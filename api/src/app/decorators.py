from time import perf_counter
from functools import partial
from shutil import rmtree


def run_container():
    def _wrapper(func):
        def _inner(container, command, filename, run_id, *args, **kwargs):
            start = perf_counter()
            retval = func(container, command, filename,
                          run_id, *args, **kwargs)
            duration = perf_counter() - start
            return duration, retval
        return _inner
    return _wrapper
