from keras import layers

from Src.Nodes import Node



class InputLayerNode(Node):
    '''
    Класс хранящий данные, для связи нода с слоём нейроной сети.
    '''
    logic: layers.Input