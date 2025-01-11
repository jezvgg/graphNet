import dearpygui.dearpygui as dpg

# Контекст, он просто нужен
dpg.create_context()
# Viewport - окно создаваемое операционкой
dpg.create_viewport(title='Custom Title')

dpg.show_debug()
dpg.show_about()
dpg.show_metrics()
dpg.show_font_manager()
dpg.show_item_registry()

# Окно создаваемое приложением
with dpg.window(tag="Prime"):
    dpg.add_text("Hello, world")
    dpg.add_button(label="Save", callback=lambda: print("Hello world"))
    b0 = dpg.add_input_text(tag="String_input", label="string", default_value="Quick brown fox")
    b1 = dpg.add_slider_float(label="float", default_value=0.273, max_value=1)

print(b0)
print(b1)
print(dpg.get_value("String_input"))

dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_primary_window("Prime", True)

dpg.start_dearpygui()
dpg.destroy_context()