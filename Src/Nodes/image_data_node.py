import numpy as np
import keras

from Src.Nodes import DataNode



class ImageDataNode(DataNode):

    @staticmethod
    def open_data(files: dict, *args, **kwargs):
        images = []
        for image_path in files:
            image = keras.utils.load_img(image_path, *args, **kwargs)
            images.append(image)

        return np.array(images)
