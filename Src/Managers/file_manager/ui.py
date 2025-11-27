import dearpygui.dearpygui as dpg

from .shortcuts import get_shortcuts_via_platform
from .icon_handler import IconHandler
from pathlib import Path
from .file_dialog_controller import FileDialogController
from typing import List, Tuple
from .file_scanner import FileItem
from .config import FileDialogConfig



class FileDialogUI:
    
    
    def __init__(
        self,
        controller: FileDialogController,
        *,
        title: str,
        tag: str,
        width: int,
        height: int,
        min_size: Tuple[int, int],
        show_shortcuts_menu: bool,
        no_resize: bool,
        modal: bool,
        icon_handler: IconHandler
    ):
        self.controller = controller
        self.title = title
        self.window_tag = f"{tag}_window"
        self.show_shortcuts_menu = show_shortcuts_menu
        self.icon_handler = icon_handler
        
        # Создание UI с параметрами
        self._setup_ui(
            width=width,
            height=height,
            min_size=min_size,
            no_resize=no_resize,
            modal=modal
        )
    
    # def __init__(self, controller: FileDialogController, config: FileDialogConfig):
    #     self.controller = controller
    #     self.config = config
    #     self.state = controller.state 
        
    #     self.icon_manager = IconHandler(Path("file_manager").parent.parent / "Assets" / "icons")
        
    #     self.window_tag = f"{config.tag}_window"
    #     self.PAYLOAD_TYPE = f'ws_{config.tag}'

    #     self.controller.state.add_observer(self._on_state_changed)
        
    #     self._table_tag = 'explorer'

    #     self._setup_ui()
    #     self._refresh_view()

    def _on_state_changed(self, event: str, payload: dict):
        """Реакция на изменения состояния."""
        if event == "current_path_changed":
            # Обновляем поле ввода пути
            dpg.set_value("ex_path_input", payload["path"])
            # Запускаем обновление директории АСИНХРОННО
            dpg.split_frame()
            self.controller.refresh_directory()
            
        elif event == "selection_changed":
            # Синхронизируем визуальное выделение
            self._sync_selection_state()
            
        elif event == "search_changed":
            # Применяем фильтр поиска
            self.controller.refresh_directory()

    def _refresh_view(self):
        """Обновить данные в UI через контроллер."""
        files = self.controller.refresh_directory()  # ← получаем FileItem[]
        self._update_table(files) 

    def _on_file_click(self, sender, app_data, user_data):
        """Обработчик клика — только передаёт данные в контроллер."""
        modifiers = {
            "ctrl_pressed": dpg.is_key_down(dpg.mvKey_LControl),
            "shift_pressed": dpg.is_key_down(dpg.mvKey_LShift),
        }
        self.controller.select_file(user_data["path"], **modifiers)

    def _on_file_double_click(self, sender, app_data, user_data):
        """Двойной клик — делегируем контроллеру."""
        self.controller.handle_double_click(user_data["path"])

    def _on_ok(self, sender, app_data):
        """Подтверждение выбора."""
        self.controller.confirm_selection()

    def _on_cancel(self, sender, app_data):
        """Отмена."""
        self.controller.cancel_selection()
    
    def _sync_selection_state(self):
        """Синхронизирует визуальное состояние selectables с self.state.selected_files."""
        import dearpygui.dearpygui as dpg

        rows = dpg.get_item_children(self._table_tag, slot=1)
        for row in rows:
            cells = dpg.get_item_children(row, slot=1)
            if not cells:
                continue
            group = dpg.get_item_children(cells[0], slot=1)
            if not group:
                continue
            for item_t in group:
                item = dpg.get_item_children(item_t, slot=1)[1]
                print(dpg.get_item_type(item))
                if dpg.get_item_type(item) == "mvAppItemType::mvSelectable":
                    user_data = dpg.get_item_user_data(item)
                    print(user_data)
                    if isinstance(user_data, dict) and "path" in user_data:
                        path = user_data["path"]
                        print(path in self.state.file_list_cache)
                        dpg.set_value(item, path in self.state.file_list_cache)

    def _update_table(self, files: List[FileItem]):
        """Полностью переписываем: рисуем таблицу из FileItem[]."""
        dpg.delete_item(self._table_tag, children_only=True)  # очищаем
        
        for idx, file in enumerate(files):
            with dpg.table_row(parent=self._table_tag):
                # Ячейка с иконкой и именем
                with dpg.table_cell():
                    with dpg.group(horizontal=True) as item:
                        dpg.add_image(
                            file.icon_tag, 
                            width=16, 
                            height=16,
                            tag=f"icon_{idx}"
                        )
                        # Selectable с user_data для кликов
                        dpg.add_selectable(
                            label=file.name,
                            tag=f"selectable_{idx}"
                        )
                
                        with dpg.item_handler_registry() as handler:
                            dpg.add_item_double_clicked_handler(callback=self._on_file_double_click, user_data={"path": file.path, "index": idx})
                            dpg.add_item_clicked_handler(callback=self._on_file_click, user_data={"path": file.path, "index": idx})

                        dpg.bind_item_handler_registry(item, handler)

                # Остальные ячейки
                with dpg.table_cell():
                    dpg.add_text(file.date_str)
                with dpg.table_cell():
                    dpg.add_text(file.type_str)
                with dpg.table_cell():
                    dpg.add_text(file.size_str)
        
        self._sync_selection_state()

    def _setup_ui(self):
        self.icon_manager.load_icons()
                
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
        config = get_shortcuts_via_platform() 
        
        for item in config.items:
            with dpg.group(horizontal=True):
                dpg.add_image(item.icon_tag)
                dpg.add_menu_item(
                    label=item.label,
                    user_data={'path': item.path},
                    callback=self._on_shortcut_click
                )

    def _on_shortcut_click(self, sender, app_data, user_data):
        self.state.current_path = user_data['path']
        self.controller.refresh_directory()

    def _build_toolbar(self):
        """Панель инструментов: обновить, назад, поиск."""
        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_image_button("refresh", callback=self.controller.refresh_directory)
                dpg.add_image_button("back", callback=self.controller.go_back)
                dpg.add_input_text(
                    hint="Path",
                    on_enter=True,
                    callback=self._on_state_changed,
                    default_value=self.state.current_path,
                    width=-1,
                    tag="ex_path_input"
                )
                
                
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    hint="Search files",
                    callback=self._on_state_changed,
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
                callback=self._on_state_changed,
                default_value=self.config.file_filter,
                width=-1
            )

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=630)
            dpg.add_button(label="   OK   ", user_data=self, callback=self._on_ok)
            dpg.add_button(label=" Cancel ", user_data=self, callback=self._on_cancel)

    def _on_ok(self, sender, user_data):
        user_data = dpg.get_item_user_data(sender)
        user_data.on_ok()

    def _on_cancel(self, sender, user_data):
        user_data = dpg.get_item_user_data(sender)
        user_data.on_cancel()

    def show(self):
        dpg.show_item(self.window_tag)
        
        