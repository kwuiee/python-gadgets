"""
A simple example of validating function parameters with decorator, featuring type, value options.
"""
# pylint: disable=W0622,E0611,C0112
import inspect
import re
import sys

# py3, py2 compatible import
_PY3 = sys.version_info >= (3,)
if _PY3:
    from collections.abc import Iterable
else:
    from collections import Iterable


class _Null:
    pass


class InvalidOption(Exception):
    pass


class Schema:
    def __init__(self):
        self._type = _Null()
        self._option = _Null()
        self._f = _Null()

    def type(self, v):
        """
        Set value type.
        """
        self._type = v
        return self

    def option(self, v):
        """
        Set value option.
        """
        assert isinstance(v, Iterable), "A iterable value is required."
        self._option = v
        return self

    def func(self, v):
        """
        Set value validation function.
        """
        assert callable(v), "A callable function is required."
        spec = inspect.getargspec(v)
        assert len(spec.args) >= 1, "Validation function should at least accept one argument."
        assert (
            len(spec.args) - len(spec.defaults or []) <= 1
        ), "Validate function should at most accept one required argument."
        self._f = v
        return self

    def validate(self, v):
        if not isinstance(self._type, _Null) and not isinstance(v, self._type):
            raise TypeError("Expecting type {} found `{}`.".format(self._type, type(v)))

        if not isinstance(self._option, _Null) and not v in self._option:
            raise InvalidOption("Value `{}` is not in option `{}`.".format(v, self._option))

        if not isinstance(self._f, _Null) and not self._f(v):
            raise InvalidOption("Value `{}` is not accepted by validate function `{}`.".format(v, self._f.__name__))
        return


class InputWrapper:
    def __init__(self, f, **kwargs):
        self.f = f
        assert all(map(lambda x: isinstance(x, Schema), kwargs.values()))
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        argspec = inspect.getargspec(self.f)
        argsmap = dict(zip(argspec.args, args))
        # validate positional arguments
        for i, j in argsmap.items():
            schema = self.kwargs.get(i, _Null())
            if not isinstance(schema, _Null):
                schema.validate(j)
        # validate keyword arguments
        for i, j in kwargs.items():
            schema = self.kwargs.get(i, _Null())
            if not isinstance(schema, _Null):
                schema.validate(j)
        return self.f(*args, **kwargs)


def input(**kwargs):
    def inner(func):
        iw = InputWrapper(func, **kwargs)
        return iw

    return inner


def validate_chr_name(v):
    return bool(re.match(r"(?i)^(?:chr|)(\d+|X|Y|MT)$", v))


# @input(x=Schema().type(int).option([1, 2, 10]), y=Schema().type(str))
@input(x=Schema().type(int).option(range(0, 10)), y=Schema().type(str).func(validate_chr_name))
def main(x, y):
    return "Accepted: {}, {}".format(x, y)


if __name__ == "__main__":
    # pass
    # print(main(2, "chrX"))
    # Invalid option error
    # print(main(11, "1"))
    # Type error
    # print(main(2, 11))
    # Invalid option, not accepted by validation function.
    print(main(2, "chr1_dafwfif"))
