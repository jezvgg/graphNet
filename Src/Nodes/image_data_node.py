import numpy as np
import keras

from Src.Nodes import DataNode



class ImageDataNode(DataNode):
    data: np.ndarray


    @staticmethod
    def open_data(files: dict, *args, **kwargs):
        images_paths = list(files['selections'].values())

        images = []
        for image_path in images_paths:
            image = keras.utils.load_img(image_path, *args, **kwargs)
            images.append(image)

        return np.array(images)
