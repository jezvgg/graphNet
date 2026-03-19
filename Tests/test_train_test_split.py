import unittest
import numpy as np
from Src.Nodes.train_test_split_node import TrainTestSplitNode

class TestTrainTestSplitNode(unittest.TestCase):
    def test_split_deterministic(self):
        x = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([0, 1, 0, 1])

        X_train, X_test, y_train, y_test = TrainTestSplitNode.split(
            x, y, test_size=0.5, random_state=42
        )
        print("X_train:", X_train)
        print("X_test:", X_test)
        print("y_train:", y_train)
        print("y_test:", y_test)
        np.testing.assert_array_equal(X_train, [[7, 8], [5, 6]])
        np.testing.assert_array_equal(X_test,  [[3, 4], [1, 2]])
        np.testing.assert_array_equal(y_train, [1, 0])
        np.testing.assert_array_equal(y_test,  [1, 0])
    def test_mismatched_lengths(self):
        x = np.array([[1,2],[3,4],[5,9]])
        y = np.array([0])
        with self.assertRaises(ValueError) as e:
            
            TrainTestSplitNode.split(x,y,test_size=0.25,random_state=42)
        print(e.exception)
if __name__ == "__main__":
    unittest.main()
