# -*- coding: utf-8 -*-

import time
import logging
from contextlib import contextmanager


def timethis(what):
    @contextmanager
    def benchmark():
        start = time.time()
        yield
        end = time.time()
        logging.info("%s : %0.3f seconds" % (what, end - start))
    if hasattr(what, "__call__"):
        def timed(*args, **kwargs):
            with benchmark():
                return what(*args, **kwargs)
        return timed
    else:
        return benchmark()
