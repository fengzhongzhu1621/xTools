# -*- coding: utf-8 -*-

import sys
import operator
import atexit
import itertools
import logging
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def _identity(x): return x


try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

try:
    callable
except NameError:
    def callable(object):
        return hasattr(object, '__call__')

try:
    callable
except NameError:
    def callable(object):
        return hasattr(object, '__call__')


# Python 3.x (and backports) use a modified iterator syntax
# This will allow 2.x to behave with 3.x iterators
if not hasattr(__builtins__, 'next'):
    def next(iter):
        try:
            # Try new style iterators
            return iter.__next__()
        except AttributeError:
            # Fallback in case of a "native" iterator
            return iter.next()
# Python < 2.5 does not have "any"
if not hasattr(__builtins__, 'any'):
    def any(iterator):
        for item in iterator:
            if item:
                return True
        return False


# inspect.getargspec() raises DeprecationWarnings in Python 3.5.
# The two functions have compatible interfaces for the parts we need.
if PY3:
    from inspect import getfullargspec as getargspec
else:
    from inspect import getargspec


if not PY2:
    import builtins
    import functools
    try:
        from collections.abc import Callable
    except ImportError:
        from collections import Callable

    def callable_(c): return isinstance(c, Callable)
    reduce = functools.reduce
    zip = builtins.zip
    xrange = builtins.range
    map = builtins.map
    get_self = operator.attrgetter('__self__')
    get_func = operator.attrgetter('__func__')
    text = str
    text_type = str
    bytes_type = bytes
    buffer_type = memoryview
    string_types = (str,)
    integer_types = (int, )
    basestring = str
    long = int
    unicode_type = str
    basestring_type = str
    print_ = getattr(builtins, 'print')
    izip_longest = itertools.zip_longest
    def iterkeys(d): return iter(d.keys())
    def itervalues(d): return iter(d.values())
    def iteritems(d): return iter(d.items())
    from io import StringIO

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
    implements_to_string = _identity
    xrange = range

else:
    import __builtin__
    import itertools
    builtins = __builtin__
    reduce = __builtin__.reduce
    zip = itertools.izip
    xrange = __builtin__.xrange
    map = itertools.imap
    get_self = operator.attrgetter('im_self')
    get_func = operator.attrgetter('im_func')
    text = (str, unicode)
    text_type = unicode
    bytes_type = str
    buffer_type = buffer
    string_types = (str, unicode)
    integer_types = (int, long)
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa
    izip_longest = itertools.izip_longest
    callable_ = callable
    def iterkeys(d): return d.iterkeys()
    def itervalues(d): return d.itervalues()
    def iteritems(d): return d.iteritems()
    from cStringIO import StringIO
    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')

    def print_(s):
        sys.stdout.write(s)
        sys.stdout.write('\n')

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls

    FileNotFoundError = EnvironmentError

try:
    import typing  # noqa
    from typing import cast
    _ObjectDictBase = typing.Dict[str, typing.Any]
except ImportError:
    _ObjectDictBase = dict

    def cast(typ, x):
        return x
else:
    # More imports that are only needed in type comments.
    import datetime  # noqa
    import types  # noqa
    from typing import Any, AnyStr, Union, Optional, Dict, Mapping  # noqa
    from typing import Tuple, Match, Callable  # noqa
    if PY3:
        _BaseString = str
    else:
        _BaseString = Union[bytes, unicode_type]

try:
    from sys import is_finalizing
except ImportError:
    # Emulate it
    def _get_emulated_is_finalizing():
        L = []
        atexit.register(lambda: L.append(None))

        def is_finalizing():
            # Not referencing any globals here
            return L != []
        return is_finalizing
    is_finalizing = _get_emulated_is_finalizing()


class ObjectDict(_ObjectDictBase):
    """Makes a dictionary behave like an object, with attribute-style access.
    """

    def __getattr__(self, name):
        # type: (str) -> Any
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        # type: (str, Any) -> None
        self[name] = value
# Stubs to make mypy happy (and later for actual type-checking).


def raise_exc_info(exc_info):
    # type: (Tuple[type, BaseException, types.TracebackType]) -> None
    pass


if PY3:
    exec("""
def raise_exc_info(exc_info):
    try:
        raise exc_info[1].with_traceback(exc_info[2])
    finally:
        exc_info = None
""")
else:
    exec("""
def raise_exc_info(exc_info):
    raise exc_info[0], exc_info[1], exc_info[2]
""")


def with_metaclass(meta, *bases):
    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass.  Because of internal type checks
    # we also need to make sure that we downgrade the custom metaclass
    # for one level to something closer to type (that's why __call__ and
    # __init__ comes back from type etc.).
    #
    # This has the advantage over six.with_metaclass in that it does not
    # introduce dummy classes into the final MRO.
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})