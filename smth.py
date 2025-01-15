import dearpygui.dearpygui as dpg

from threading import Timer

dpg.create_context()

with dpg.stage(tag="stage1"):
    dpg.add_text("hello, i was added from a stage", tag="text_tag")

def present_stage_items():
    dpg.move_item("text_tag", parent="main_win")


def test():
    with dpg.table_row(parent="Layout"):
        dpg.add_text('')
        dpg.add_text("Layout"*5)


with dpg.window(label="Tutorial", tag="main_win"):
    with dpg.table(header_row=False, borders_innerH=True, borders_innerV=True, tag="Layout"):
        dpg.add_table_column()
        dpg.add_table_column(width_fixed=True)

        with dpg.table_row():
            dpg.add_text('')
            dpg.add_text("True text")

        Timer(2, test, args=[]).start()



    dpg.add_button(label="present stages items", callback=present_stage_items)

dpg.show_item_registry()

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()