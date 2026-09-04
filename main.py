from app import App

if __name__ == "__main__":
    my_app = App(
        title="GraphNet",
        logger_config_path="Assets/logger_config.json",
        font_path="Assets/fonts_config.json",
        themes_path="Assets/themes.json",
    )

    my_app.run()
