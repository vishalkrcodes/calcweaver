from unittest import TestCase
from calcweaver import Knot, knot, Weave, context


class Dummy(Weave):
    D = Knot(20)

    @knot
    def A(self):
        return 10

    @knot
    def B(self):
        return self.A() ** 2

    @knot
    def C(self):
        return self.A() + self.B() + self.D()


class BasicFunctionalityTests(TestCase):
    def test_basic(self):
        dummy = Dummy()
        self.assertEqual(dummy.C(), 130)
        with context(name="Test context"):
            dummy.D.tweak(10)
            self.assertEqual(dummy.C(), 120)
            dummy.B.tweak(5)
            self.assertEqual(dummy.C(), 25)
            dummy.A.tweak(3)
            self.assertEqual(dummy.C(), 22)
