import dearpygui.dearpygui as dpg

from Src.Nodes import Node, node_link, logger


class NodeEditor:
    '''
    Класс реализующий логику управления нодами.
    '''

    def __init__(self):
        pass


    def __call__(self, *args, **kwargs):
        '''
        Вызвать окно, для создания графа. 

        Args:
            *args, **kwargs - передаются в dpg.node_editor
        '''

        # Делим окно на 2, чтоб слева были блоки, а справа конструктор графа
        with dpg.group(horizontal=True, tag="NodeEditor_group"):

            # Rail справа, в котором находяться блоки
            with dpg.group(tag="nodes_group"):

                # Выпадающий список, в дальнейшем тут будет заменено на метод из node_builder
                with dpg.tree_node(label="Convoluion Layers", tag="tree_node_conv"):
                    dpg.add_button(label="Layer1", tag="Layer1", user_data={"sss":"ss"})
                    dpg.add_button(label="Layer2", tag="Layer2")

                    # Добавляем возможность Drag (перетягивать элемент)
                    with dpg.drag_payload(parent="Layer1", drag_data="Layer1"):
                        dpg.add_text("popup drag")

                    with dpg.drag_payload(parent="Layer2", drag_data="Layer2"):
                        dpg.add_text("popup drag")


            # Именно в группу задаём drop_callback, который создаёт ноду по перетягиванию её с окна справа
            with dpg.group(tag="editor_group", drop_callback=self.drop_callback):
                
                # Используем редактор нодов из DearPyGUI
                with dpg.node_editor(tag="node_editor", callback=self.link_callback, \
                                    delink_callback=self.delink_callback, *args, **kwargs):

                    # Заменить на метод из node_builder
                    node_tag = "node_input"
                    with dpg.node(label="Input Layer", pos=(0, 0), draggable=False,
                                   tag=node_tag, user_data=Node(node_tag)):
                        with dpg.node_attribute(label="INPUT_DUMMY", attribute_type=dpg.mvNode_Attr_Output):
                            dpg.add_text("INPUT")


    def drop_callback(self, sender: str | int, app_data: str | int):
        '''
        Функция, которая выполняется, при перетягивания блока в окно редакторования графа. Создаём новую ноду в окне.

        Args:
            sender: str | int - зачастую является окном редакторивания графа (dpg.node_editor)
            app_data: str | int - элемент, который перетащили.
        '''
        logger.debug(f"На вход пришло {sender}, {app_data}, {dpg.get_item_user_data(app_data)}")

        # Реализовать создание нода, через обычные координаты мыши не получится
        # потому что координаты в node_editor отличаются от координат мыши
        # поэтому координаты размещения нового нода рассчитываются относительно уже стоящего нода (input_node)
        pos = dpg.get_mouse_pos(local=False)
        ref_node = dpg.get_item_children("node_editor", slot=1)[0]
        ref_screen_pos = dpg.get_item_rect_min(ref_node)
        ref_grid_pos = dpg.get_item_pos(ref_node)

        NODE_PADDING = (8, 8)

        pos[0] = pos[0] - (ref_screen_pos[0] - NODE_PADDING[0]) + ref_grid_pos[0]
        pos[1] = pos[1] - (ref_screen_pos[1] - NODE_PADDING[1]) + ref_grid_pos[1]

        logger.info(f"Рассчитанная позиция - {pos}")

        # Заменить на метод из node_builder
        node_tag = "node_"+str(dpg.generate_uuid())
        
        with dpg.node(label=app_data, pos=pos, parent="node_editor", 
                      tag=node_tag, user_data=Node(node_tag)):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("Input")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text("Output")
                dpg.add_button(label="Delete", callback=lambda: self.delete_node(node_tag))


    def link_callback(self, sender: str | int, app_data: tuple[str | int, str | int]):
        '''
        Функция, которая вызывается, когда создаётся новая связь между нодами.

        Args:
            sender: int | str - зачастую является окном редакторивания графа (dpg.node_editor)
            app_data: tuple(str | int, str | int) - исходящий и приходящий нод.
        '''
        logger.debug(f"На вход пришло {app_data}")

        node_out: Node = dpg.get_item_user_data(dpg.get_item_parent(app_data[0]))
        node_in: Node = dpg.get_item_user_data(dpg.get_item_parent(app_data[1]))

        dpg.add_node_link(app_data[0], app_data[1], parent=sender, user_data=node_link(node_out, node_in))

        logger.debug(f"Связи до: {node_out} {node_in}")

        node_out.add_link(node_in)

        logger.debug(f"Связи после: {node_out} {node_in}")

        # Для дебага
        # Node.print_tree(dpg.get_item_user_data("node_input"))


    def delink_callback(self, sender: int | str, app_data: int | str):
        '''
        Функция, которая вызывается, когда создаётся убирается связь между нодами.

        Args:
            sender: int | str - зачастую является окном редакторивания графа (dpg.node_editor)
            app_data: str | int - связь между нодами (dpg.add_node_link)
        '''
        link: node_link = dpg.get_item_user_data(app_data)

        logger.debug(f"Связи до: {link.outcoming} {link.incoming}")

        link.outcoming.remove_link(link.incoming)

        logger.debug(f"Связи после: {link.outcoming} {link.incoming}")

        dpg.delete_item(app_data)


    def delete_node(self, node_id: str | int):
        '''
        Функция для удаления нода, вместе с его связями.

        Args:
            node_id: str | int - индетификатор нода, которого нужно удалить (dpg.node)
        '''
        node_data: Node = dpg.get_item_user_data(node_id)
        
        node_data.delete()

        dpg.delete_item(node_id)


# Объект класса, для импорта
node_editor = NodeEditor()

# Для дебаг запуска
if __name__ == "__main__":
    dpg.create_context()

    with dpg.window(tag="Prime"):
        node_editor(minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_TopRight)

    dpg.create_viewport(title='Custom Title')
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Prime", True)
    dpg.set_global_font_scale(2)
    dpg.start_dearpygui()
    dpg.destroy_context()