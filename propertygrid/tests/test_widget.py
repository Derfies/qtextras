from types import SimpleNamespace
from unittest import TestCase

from PySide6.QtWidgets import QApplication

from propertygrid.widget import Widget


class Dummy: pass


class WidgetTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.app = QApplication()

    # @parameterized.expand(
    #     (
    #         (
    #             export_shaders.Colour,
    #             (0, 1000, ),
    #             {'r': 0.3, 'g': 0.6, 'b': 0.9},
    #             shaders.colour,
    #             1000,
    #             [0.3, 0.6, 0.9],
    #             'fff',
    #             12,
    #             [0.6, 0.3, 0.9],
    #         ),
    #     )
    # )
    def test__get_multi_object(self):

        # foo = {}
        # print(foo)
        # print(foo.__dict__)

        #widget = Widget()


        foo = Dummy()
        foo.one = 1
        foo.two = 2
        foo.common = 3

        bar = Dummy()
        bar.three = 3
        bar.four = 4
        bar.common = 3

        print(vars(foo))
        print(vars(bar))

        mobj = Widget._get_multi_object((foo, bar))
        print(mobj)
        print(mobj.one)
        mobj.one = 1
        #print

        print(vars(mobj))
        # for d in dir(mobj):
        #     print(d)