from Src.Nodes import AbstractNode
from Src.Nodes.dataset_node import Dataset
from sklearn.preprocessing import StandardScaler

class ExtSklearnnodeNode(AbstractNode):
    def setup(self):
        pass

    def compute(self, dataset: Dataset):
        if not dataset:
            return None
        scaler = StandardScaler()
        # Scale train and test sets
        # reshaping might be needed depending on dataset shape, but standard scaler expects 2D
        # For images (e.g. MNIST), we might need to reshape to 2D
        X_train = dataset.X_train
        X_test = dataset.X_test
        
        orig_shape_train = X_train.shape
        orig_shape_test = X_test.shape
        
        if len(orig_shape_train) > 2:
            X_train = X_train.reshape(X_train.shape[0], -1)
            X_test = X_test.reshape(X_test.shape[0], -1)
            
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        if len(orig_shape_train) > 2:
            X_train_scaled = X_train_scaled.reshape(orig_shape_train)
            X_test_scaled = X_test_scaled.reshape(orig_shape_test)

        return Dataset(
            X_train=X_train_scaled,
            y_train=dataset.y_train,
            X_test=X_test_scaled,
            y_test=dataset.y_test,
            shape=orig_shape_train
        )
        
    def compile(self, kwargs: dict = None) -> bool:
        status = super().compile(kwargs)
        if not status:
            return False
            
        # AbstractNode.compile sets self.OUTPUT to the result of self.logic
        return status
