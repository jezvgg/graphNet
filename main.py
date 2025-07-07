from app import App

app_config = {
    "title": "GRN",

    # Конфигурация логирования
    "logger_config_path": "Src/Logging/logger_config.json",

    # Конфигурация размеров и шрифтов
    "font_path": "notomono-regular.ttf",
    "initial_app_font_size": 14,
    "initial_node_font_size": 14,
    "font_limits": (8, 28),

    # Конфигурация масштабирования
    "initial_global_scale": 1.0,
    "global_scale_limits": (0.5, 2.0)
}

my_app = App(**app_config)
my_app.run()
