import numpy as np
import unittest

from Src.Nodes.dataset_node import DatasetNode


class TestSplitXy(unittest.TestCase):

    def test_split_xy_basic(self):
        data = np.array([
            [1, 2, 0],
            [3, 4, 1],
            [5, 6, 0],
        ])

        X, y = DatasetNode.split_Xy(data)

        np.testing.assert_array_equal(X, np.array([[1, 2], [3, 4], [5, 6]]))
        np.testing.assert_array_equal(y, np.array([0, 1, 0]))


    def test_split_xy_invalid_shape(self):
        data = np.array([1, 2, 3])
        with self.assertRaises(ValueError):
            DatasetNode.split_Xy(data)
