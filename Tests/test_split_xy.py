import numpy as np
import unittest
from pathlib import Path
import sys

# Добавляем корень проекта в sys.path, чтобы импортировать Src.*
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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

    def test_split_xy_from_csv(self):
        # sample_data.csv лежит в корне проекта
        data = np.genfromtxt("sample_data.csv", delimiter=",", skip_header=1)
        print("CSV data shape:", data.shape)
        print("CSV first rows:", data[:2])
        X, y = DatasetNode.split_Xy(data)
        print("X shape:", X.shape, "y shape:", y.shape)
        print("y:", y)
        # Проверяем форму: 5 строк, последние данные - цель
        self.assertEqual(X.shape[1] + 1, data.shape[1])
        self.assertEqual(X.shape[0], y.shape[0])
