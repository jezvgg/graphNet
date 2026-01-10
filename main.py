from app import App


if __name__ == '__main__':
    # Не работает SizeManager (да и вроде не используется вообще)
    # Нет настройки тем и темовый менеджер не синглтон
    my_app = App(title = 'GRN', 
                logger_config_path = 'Src/Logging/logger_config.json', 
                font_path = 'Assets/notomono-regular.ttf',
                initial_app_font_size = 14, 
                initial_node_font_size = 14, 
                font_limits = (8, 28), 
                initial_global_scale = 1.0,
                global_scale_limits = (0.5, 2.0))

    my_app.run()
