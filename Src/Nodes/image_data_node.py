from pathlib import Path

import numpy as np
import keras

from Src.Enums import Themes
from Src.Nodes import ShapeNode



class ImageDataNode(ShapeNode):
    theme_name: Themes = Themes.IMAGE_DATA


    @staticmethod
    def open_data(files: str, *args, **kwargs):
        if not files: 
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")

        images = []
        for image_path in sorted(Path(files).iterdir()):
            image = keras.utils.load_img(image_path, *args, **kwargs)
            image = keras.utils.img_to_array(image)
            images.append(image)

        return np.array(images)
