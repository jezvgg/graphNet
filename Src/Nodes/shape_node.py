from pathlib import Path
from abc import abstractmethod

import numpy as np
import keras
import librosa

from Src.Enums import Themes
from Src.Utils import Backfield
from Src.Nodes import DataNode



class ShapeNode(DataNode):
    '''
    Нода, которая содержит в себе данные. (файлы или табличные)
    '''
    shape: tuple[int] = Backfield()
    theme_name: Themes = Themes.SHAPE
    OUTPUT: np.ndarray


    def compile(self):
        status = super().compile()
        if not status or len(self.OUTPUT.shape) < 2: return False
        self.shape = self.OUTPUT.shape[1:]
        return status


    @staticmethod
    def open_table_data(files: str, *args, **kwargs):
        if not files: 
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")
        
        return np.genfromtxt(files, *args, **kwargs, ndmin=2)

    
    @staticmethod
    def open_image_data(files: str, *args, **kwargs):
        if not files: 
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")

        images = []
        for image_path in sorted(Path(files).iterdir()):
            image = keras.utils.load_img(image_path, *args, **kwargs)
            image = keras.utils.img_to_array(image)
            images.append(image)

        return np.array(images)
    

    @staticmethod
    def open_audio_data(files: str, NFFT: int = 1024, noverlap: int = 512, max_duration_sec: float = 5.0, *args, **kwargs):
        if not files:
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")
        
        audios = []
        extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        
        for audio_path in sorted(Path(files).iterdir()):
            if audio_path.is_file() and audio_path.suffix.lower() in extensions:
            
                data, sample_rate = librosa.load(str(audio_path), sr=None, mono=True, duration=max_duration_sec)
                    
                nfft = NFFT if NFFT else int(2 ** round(np.log2(sample_rate * 0.025)))
                noverlap = noverlap if noverlap else nfft // 2
                hop_length = nfft - noverlap 
                    
                stft_matrix = librosa.stft(data, n_fft=nfft, hop_length=hop_length)
                
                spectrum = np.abs(stft_matrix)**2
                
                spectrum = 10. * np.log10(spectrum + 1e-10)
                audios.append(spectrum)

        if not audios:
            return np.array([])

        return audios[0]