import abc
import testtools

from collections import Sequence


class C3TestType(abc.ABCMeta):
    """Base type for C3 test cases."""
    def __new__(meta, name, bases, attrs):
        scenarios = attrs.get("scenarios")
        if scenarios is not None:
            if not isinstance(scenarios, Sequence):
                scenarios = attrs["scenarios"] = tuple(scenarios)
            if len(scenarios) == 0:
                scenarios = attrs["scenarios"] = None
        return super(C3TestType, meta).__new__(
            meta, name, bases, attrs)


class C3TestCase(
        testtools.TestCase,
        metaclass=C3TestType):
    """Base `TestCase` for C3."""

    scenarios = ()

    def patch(
            self, obj, attribute=None, value=mock.sentinel.unset) -> MagicMock:
        if attribute is None:
            attribute = obj.__name__
            obj = import_module(obj.__module__)
        if value is mock.sentinel.unset:
            value = MagicMock(__name__=attribute)
        super(C3TestCase, self).patch(obj, attribute, value)
        return value


class TestFake(C3TestCase):

    def test_fake(self):
        pass

    def test_very_fake(self):
        pass
