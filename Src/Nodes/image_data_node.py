import numpy as np
import keras

from Src.Nodes import ShapeNode



class ImageDataNode(ShapeNode):
    color = (255, 155, 0, 255)


    # TODO: 100% не работает, нужно будет починить
    @staticmethod
    def open_data(files: dict, *args, **kwargs):
        images = []
        for image_path in files:
            image = keras.utils.load_img(image_path, *args, **kwargs)
            images.append(image)

        return np.array(images)
