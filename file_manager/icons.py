import dearpygui.dearpygui as dpg
import os
from pathlib import Path
from typing import Dict, Any

class IconManager:
    def __init__(self, image_dir: Path):
        self.image_dir = image_dir
        self.icons: Dict[str, Any] = {}

    def load_and_register_textures(self):
        """Загружает и регистрирует все иконки."""
        with dpg.texture_registry():
            placeholder_data = [255, 255, 255, 255] * 16  # 2x2 белый квадрат
            icon_names = [
                "add_file", "add_folder", "app", "back", "big_picture", 
                 "c", "desktop", "document", "documents", "downloads", 
                 "folder", "gears", "hd", "home", "iso", "link", 
                 "mini_document", "mini_error", "mini_folder", 
                 "music_note", "music", "note", "object", 
                 "picture_folder", "picture", "python", 
                 "refresh", "script", "search", "url", "vector", 
                 "video", "videos", "zip"
            ]
            for name in icon_names:
                file_path = self.image_dir.joinpath(f'{name}.png')
                
                width, height, data = 16, 16, placeholder_data
                
                if file_path.exists():
                    width, height, _, data = dpg.load_image(file_path.as_posix())
                    
                dpg.add_static_texture(width=width, height=height, default_value=data, tag=name)
                self.icons[name] = name
                
                
                
        