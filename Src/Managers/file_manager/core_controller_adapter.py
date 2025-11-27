
import dearpygui.dearpygui as dpg

from typing import List
from .file_dialog_controller import FileDialogController

from .state import FileDialogState
from .file_scanner import FileScanner, FileItem

class CoreAdapter:
    """Адаптер, имитирующий старый FileDialogCore для UI."""
    
    def __init__(self, controller: FileDialogController):
        self.controller = controller
        self.state = controller.state  # для совместимости
        self._table_tag = 'explorer'

    # === Старые методы, перенаправляющие в контроллер ===
    
    def refresh_directory(self):
        """Обновить директорию и вернуть данные в старом формате."""
        files = self.controller.refresh_directory()
        return self._convert_to_legacy_format(files)

    def _convert_to_legacy_format(self, files: List[FileItem]) -> List[dict]:
        """Конвертация FileItem → старый формат для UI."""
        return [{
            "name": f.name,
            "path": f.path,
            "is_dir": f.is_dir,
            "size": f.size_str,
            "date": f.date_str,
            "type": f.type_str,
            "icon": f.icon_tag,
        } for f in files]

    def go_back(self):
        self.controller.go_back()

    def on_path_enter(self, sender, app_data):
        self.controller.navigate_to(app_data.strip())

    def on_search(self, sender, app_data):
        self.controller.set_search_query(app_data)

    def on_filter_change(self, sender, app_data):
        self.controller.set_file_filter(app_data)

    def _on_file_click(self, sender, app_data):
        """Обработчик клика — получает события от UI."""
        user_data = dpg.get_item_user_data(sender)
        self.controller.select_file(
            user_data["path"],
            ctrl_pressed=dpg.is_key_down(dpg.mvKey_LControl),
            shift_pressed=dpg.is_key_down(dpg.mvKey_LShift)
        )

    def _on_file_double_click(self, sender, app_data):
        user_data = dpg.get_item_user_data(sender)
        self.controller.handle_double_click(user_data["path"])

    def on_ok(self):
        self.controller.confirm_selection()

    def on_cancel(self):
        self.controller.cancel_selection()

    def close(self):
        self.controller.close(confirm=False)
        dpg.hide_item(f"{self.controller.config.tag}_window")  # временно
        
    # === Старые методы для UI (временно!) ===
    def _update_table(self, file_infos: List[dict]):
        """Этот метод вызывается из старого кода — перенаправляем в UI."""
        # В будущем UI будет сам рисовать таблицу через controller.refresh_directory()
        pass
    
    def _sync_selection_state(self):
        """Синхронизация выделения — теперь делает UI через события."""
        pass