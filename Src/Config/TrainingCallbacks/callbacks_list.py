from keras import callbacks

from Src.Config.TrainingCallbacks.log2window import Log2Window


callbacks_list = {
        "EarlyStopping": {
            "class": callbacks.EarlyStopping,
            "kwargs": {
                "monitor": "loss"
            }
        },
        "ReduceLROnPlateau": {
            "class": callbacks.ReduceLROnPlateau,
            "kwargs": {
                "monitor": "loss"
            }
        },
        "TerminateOnNaN": {
            "class": callbacks.TerminateOnNaN,
            "kwargs": {}
        },
        "Log2Window": {
            "class": Log2Window,
            "kwargs": {}
        }
    }