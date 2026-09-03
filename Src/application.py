"""GraphNet application entry point."""
import argparse

from Src.resources import resource_path


def main():
    """Launch the editor, optionally exiting after three frames for smoke tests."""
    parser = argparse.ArgumentParser(description="GraphNet neural network constructor")
    parser.add_argument(
        "--smoke-test", action="store_true",
        help="initialize the editor, render three frames and exit",
    )
    args = parser.parse_args()

    import dearpygui.dearpygui as dpg
    from Src.Logging import logging
    from Src.Managers import ThemeManager
    from Src.node_editor import NodeEditor

    dpg.create_context()
    try:
        dpg.create_viewport(title="GraphNet")
        ThemeManager.load_themes(resource_path("themes.json"))
        node_editor = NodeEditor(
            minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_TopRight,
        )
        main_logger = logging()("main")
        with dpg.font_registry():
            with dpg.font(str(resource_path("notomono-regular.ttf")), 18,
                          default_font=True, tag="Default font"):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        dpg.bind_font("Default font")

        with dpg.window(tag="Prime"):
            node_editor.show("Prime")
            main_logger.warning("НАЧАЛИ")

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Prime", True)
        if args.smoke_test:
            for _ in range(3):
                dpg.render_dearpygui_frame()
        else:
            dpg.start_dearpygui()
    finally:
        dpg.destroy_context()
