import keras

from Src.Nodes import AbstractNode, LayerResult



class CompileNode(AbstractNode):
    logic: keras.models.Model.compile
    color = (0, 150, 0, 255)


    # TODO: Настроить правильные аннотации от logic
    @staticmethod
    def compile_model(*args: LayerResult, **kwargs):
        inputs = tuple(set().union(*[arg.inputs for arg in args]))
        outputs = tuple(arg.layer for arg in args)
        if len(inputs) == 1: inputs = inputs[0]
        if len(outputs) == 1: outputs = outputs[0]
        model = keras.models.Model(inputs=inputs, outputs=outputs)
        model.compile(**kwargs)
        return model
