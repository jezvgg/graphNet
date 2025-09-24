import dearpygui.dearpygui as dpg
import os
from .core import FileDialogCore
from .config import FileDialogConfig, get_shortcuts_config
from .icons import IconManager
from pathlib import Path

class FileDialogUI:
    def __init__(self, core: FileDialogCore, config: FileDialogConfig):
        self.core = core
        self.config = config
        self.icon_manager = IconManager(Path("file_manager") / "images")

        self.window_tag = f"{config.tag}_window"
        self.PAYLOAD_TYPE = f'ws_{config.tag}'

        self.setup_ui()
        self.core.refresh_directory()

    def setup_ui(self):
        self.icon_manager.load_and_register_textures()
        
        with dpg.window(
            label=self.config.title,
            tag=self.window_tag,
            no_resize=self.config.no_resize,
            show=False,
            modal=self.config.modal,
            width=self.config.width,
            height=self.config.height,
            min_size=self.config.min_size,
            no_collapse=True,
            pos=(50, 50)
        ):
            with dpg.group(horizontal=True):
                if self.config.show_shortcuts_menu:
                    with dpg.child_window(tag="shortcut_menu", width=200, height=-50):
                        self._build_shortcuts_menu()
                else:
                    dpg.add_spacer(width=10)

                with dpg.child_window(height=-50):
                    self._build_toolbar()
                    self._build_table()

            self._build_footer()
            
        
    def _build_shortcuts_menu(self):
        """Строит боковое меню ярлыков."""
        config = get_shortcuts_config() 
        
        for item in config.items:
            with dpg.group(horizontal=True):
                dpg.add_image(item.icon_tag)
                dpg.add_menu_item(
                    label=item.label,
                    user_data={'path': item.path},
                    callback=self._on_shortcut_click
                )

    def _on_shortcut_click(self, sender, app_data, user_data):
        self.core.state.current_path = user_data['path']
        self.core.refresh_directory()

    def _build_toolbar(self):
        """Панель инструментов: обновить, назад, поиск."""
        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_image_button("refresh", callback=self.core.refresh_directory)
                dpg.add_image_button("back", callback=self.core.go_back)
                dpg.add_input_text(
                    hint="Path",
                    on_enter=True,
                    callback=self.core.on_path_enter,
                    default_value=self.core.state.current_path,
                    width=-1,
                    tag="ex_path_input"
                )
                
                
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    hint="Search files",
                    callback=self.core.on_search,
                    tag="ex_search",
                    width=-1
                )

    def _build_table(self):
        """Таблица файлов."""
        with dpg.table(
            tag='explorer',
            height=-1,
            width=-1,
            resizable=True,
            policy=dpg.mvTable_SizingStretchProp,
            borders_innerV=True,
            reorderable=True,
            hideable=True,
            sortable=True,
            scrollX=True,
            scrollY=True,
        ):
            dpg.add_table_column(label='Name', init_width_or_weight=100, tag="ex_name")
            dpg.add_table_column(label='Date', init_width_or_weight=50, tag="ex_date")
            dpg.add_table_column(label='Type', init_width_or_weight=10, tag="ex_type")
            dpg.add_table_column(label='Size', init_width_or_weight=10, tag="ex_size")

    def _build_footer(self):
        """Нижняя панель с фильтром и кнопками."""
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=480)
            dpg.add_text('File type filter')
            dpg.add_combo(
                items=self.config.filter_list,
                callback=self.core.on_filter_change,
                default_value=self.config.file_filter,
                width=-1
            )

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=630)
            dpg.add_button(label="   OK   ", callback=self.core.on_ok)
            dpg.add_button(label=" Cancel ", callback=self.core.on_cancel)

    def show(self):
        dpg.show_item(self.window_tag)
        
        