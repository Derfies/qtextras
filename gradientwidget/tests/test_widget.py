import copy
from unittest import TestCase

from gradientwidget.widget import Gradient


class GradientTestCase(TestCase):

    def test_deepcopy(self):
        """
        Default deep copy behaviour seems to crash python. My guess is that deep
        copying a python wrapper around a C++ object is a no-no.

        """
        # Set up test data.
        g = Gradient()

        # Start test.
        deep_copied_g = copy.deepcopy(g)

        # Assert results.
        self.assertIsNot(g[0].colour, deep_copied_g[0].colour)
