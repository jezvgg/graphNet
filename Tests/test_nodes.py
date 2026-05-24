import unittest
from pathlib import Path

import numpy as np
import keras

from Src.Nodes.layer_node import LayerNode, LayerResult
from Src.Nodes.input_layer_node import InputLayerNode
from Src.Nodes.compile_node import CompileNode
from Src.Nodes.fit_node import FitNode
from Src.Nodes.predict_node import PredictNode
from Src.Nodes.shape_node import ShapeNode
from Src.Nodes.metric_node import MetricNode
from Src.Nodes.utils_node import UtilsNode


class test_nodes(unittest.TestCase):
    '''
    Покрытие статических функций узлов графа.
    DPG не нужен - все эти методы работают только с keras и numpy.
    '''

    #  LayerNode 

    def test_layer_factory_returns_callable(self):
        # LayerNode.layer() - фабрика: должна вернуть вызываемый объект
        # Принимает класс слоя (не инстанс), потому что compile_layer вызывает layer(**kwargs) как конструктор
        factory = LayerNode.layer(keras.layers.Dense)

        assert callable(factory)

    def test_compile_layer_returns_layer_result(self):
        # compile_layer создаёт слой через layer(**kwargs) и применяет его к входным данным
        input_layer = keras.layers.Input(shape=(4,))
        input_result = LayerResult(input_layer, {input_layer})

        result = LayerNode.compile_layer(keras.layers.Dense, input_result, units=2)

        assert isinstance(result, LayerResult)
        assert len(result.inputs) == 1

    #  InputLayerNode ─

    def test_create_input_returns_layer_result(self):
        # create_input должен вернуть LayerResult с одним входным слоем
        result = InputLayerNode.create_input(shape=(4,))

        assert isinstance(result, LayerResult)
        assert len(result.inputs) == 1

    #  CompileNode 

    def test_compile_model_returns_model(self):
        # compile_model должен собрать и скомпилировать keras-модель из LayerResult
        input_layer = keras.layers.Input(shape=(4,))
        dense = keras.layers.Dense(2)(input_layer)
        layer_result = LayerResult(dense, {input_layer})

        model = CompileNode.compile_model(layer_result, loss='mse')

        assert isinstance(model, keras.models.Model)

    #  FitNode 

    def test_fit_raises_on_zero_epochs(self):
        # fit должен поднять AttributeError если epochs == 0
        x = np.ones((5, 4))
        y = np.ones((5, 1))

        with self.assertRaises(AttributeError):
            FitNode.fit(None, x=x, y=y, epochs=0)

    def test_fit_raises_on_negative_epochs(self):
        # fit должен поднять AttributeError если epochs < 0
        x = np.ones((5, 4))
        y = np.ones((5, 1))

        with self.assertRaises(AttributeError):
            FitNode.fit(None, x=x, y=y, epochs=-3)

    def test_fit_raises_on_shape_mismatch(self):
        # fit должен поднять AttributeError если количество строк X и Y не совпадает
        x = np.ones((10, 4))
        y = np.ones((5, 1))

        with self.assertRaises(AttributeError):
            FitNode.fit(None, x=x, y=y, epochs=1)

    def test_fit_raises_on_nan_in_x(self):
        # fit должен поднять AttributeError если X содержит NaN
        x = np.array([[1.0, np.nan], [1.0, 1.0]])
        y = np.array([[1.0], [1.0]])

        with self.assertRaises(AttributeError):
            FitNode.fit(None, x=x, y=y, epochs=1)

    def test_fit_raises_on_nan_in_y(self):
        # fit должен поднять AttributeError если Y содержит NaN
        x = np.ones((2, 4))
        y = np.array([[np.nan], [1.0]])

        with self.assertRaises(AttributeError):
            FitNode.fit(None, x=x, y=y, epochs=1)

    #  PredictNode 

    def test_predict_returns_numpy_array(self):
        # predict должен вернуть numpy-массив правильной формы
        input_layer = keras.layers.Input(shape=(4,))
        dense = keras.layers.Dense(2)(input_layer)
        model = keras.models.Model(inputs=input_layer, outputs=dense)
        model.compile(loss='mse')

        result = PredictNode.predict(model, x=np.ones((5, 4)))

        assert isinstance(result, np.ndarray)
        assert result.shape == (5, 2)

    #  ShapeNode 

    def test_open_table_data_reads_file(self):
        # open_table_data должен прочитать файл и вернуть numpy-массив минимум 2D
        data = ShapeNode.open_table_data("Tests/X.txt")

        assert isinstance(data, np.ndarray)
        assert data.ndim >= 2

    def test_open_table_data_raises_on_empty_path(self):
        # open_table_data должен поднять AttributeError для пустого пути
        with self.assertRaises(AttributeError):
            ShapeNode.open_table_data("")

    def test_open_table_data_raises_on_none(self):
        # open_table_data должен поднять AttributeError для None
        with self.assertRaises(AttributeError):
            ShapeNode.open_table_data(None)

    #  MetricNode

    def test_calculate_returns_list_of_float(self):
        # calculate должен вернуть список с одним float-значением
        y_true = np.array([1, 0, 1, 0])
        y_pred = np.array([1, 0, 0, 0])
        result = MetricNode.calculate(y_true, y_pred, 'accuracy')

        assert isinstance(result, list)
        assert isinstance(result[0], float)

    def test_calculate_perfect_accuracy(self):
        # При совпадающих метках точность должна быть 1.0
        y_true = np.array([1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0])
        result = MetricNode.calculate(y_true, y_pred, 'accuracy')

        self.assertAlmostEqual(result[0], 1.0, places=5)

    #  UtilsNode 

    def test_to_json_creates_file(self):
        # to_json должен создать файл с JSON-конфигурацией модели
        input_layer = keras.layers.Input(shape=(4,))
        output_layer = keras.layers.Dense(2)(input_layer)
        model = keras.models.Model(inputs=input_layer, outputs=output_layer)

        filename = "test_model_output.json"
        UtilsNode.to_json(model, filename)

        assert Path(filename).exists()
        Path(filename).unlink()
