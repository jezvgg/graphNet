from pathlib import Path
from abc import abstractmethod

import numpy as np
import keras
import librosa

from Src.Enums import Themes, TextOutputMode, SplitMode
from Src.Utils import Backfield
from Src.Nodes import DataNode


class ShapeNode(DataNode):
    '''
    Нода, которая содержит в себе данные. (файлы или табличные)
    '''
    shape: tuple[int] = Backfield()
    theme_name: Themes = Themes.SHAPE
    OUTPUT: np.ndarray
    EXTENSIONS = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}

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
    def open_audio_data(files: str, NFFT: int = 1024, noverlap: int = 512, max_duration_sec: float = 5.0,sr: int = None, mono: bool = True):
        if not files:
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")
        
        audios = []
        
        for audio_path in sorted(Path(files).iterdir()):
            if not (audio_path.is_file() and audio_path.suffix.lower() in ShapeNode.EXTENSIONS):
                continue
            
            data, sample_rate = librosa.load((audio_path), sr=sr, mono=mono, duration=max_duration_sec)
                
            target_length = int(sample_rate * max_duration_sec)
            data = librosa.util.fix_length(data, size=target_length)
                    
            nfft = int(2 ** round(np.log2(sample_rate * 0.025)))
            hop_length = nfft // 2 

            stft_matrix = librosa.stft(data, n_fft=nfft, hop_length=hop_length)
            spectrum = np.abs(stft_matrix)**2
            spectrum = 10. * np.log10(spectrum + 1e-10)
                
            audios.append(spectrum.T)

        return np.array(audios)
    

    @staticmethod
    def open_text_data(files: str, output_mode: TextOutputMode = TextOutputMode.INT, max_tokens: int = 20000,split: SplitMode = SplitMode.WHITESPACE):
        if not files: 
            raise AttributeError("Вы не выбрали данные, которые нужно открыть!")
        
        texts = []
        for text_path in sorted(Path(files).glob('*.txt')):
            texts.append(text_path.read_text(encoding='utf-8'))

        vectorizer = keras.layers.TextVectorization(
            max_tokens=max_tokens,
            output_mode=output_mode,
            split=split
        )
        
        vectorizer.adapt(texts)
        vectorized_texts = vectorizer(texts)
        
        return np.array(vectorized_texts)