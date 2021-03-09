"""
A simple example of validating function parameters with decorator, featuring type, value options.
"""
# pylint: disable=W0622,E0611,C0112
import inspect
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

    def validate(self, v):
        if not isinstance(self._type, _Null) and not isinstance(v, self._type):
            raise TypeError("Expecting type {} found `{}`.".format(self._type, v))

        if not isinstance(self._option, _Null) and not v in self._option:
            raise InvalidOption("Value `{}` is not in option `{}`.".format(v, self._option))
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


# @input(x=Schema().type(int).option([1, 2, 10]), y=Schema().type(str))
@input(x=Schema().type(int).option(range(0, 10)), y=Schema().type(str))
def main(x, y):
    return "{}, {}".format(x, y)


if __name__ == "__main__":
    print(main(2, "Hello"))
    # Invalid option error
    print(main(11, "Hello"))
    # Type error
    print(main(2, 11))
