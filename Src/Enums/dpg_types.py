from enum import Enum




class DPGType(Enum):
    """
        Enum для элементов dearpygui
    """
    # Основные элементы
    BUTTON = 'mvAppItemType::mvButton'
    INPUT_TEXT = 'mvAppItemType::mvInputText'
    INPUT_INT = 'mvAppItemType::mvInputInt'
    INPUT_FLOAT = 'mvAppItemType::mvInputFloat'
    CHECKBOX = 'mvAppItemType::mvCheckbox'
    RADIO_BUTTON = 'mvAppItemType::mvRadioButton'
    TEXT = 'mvAppItemType::mvText'
    COMBO = 'mvAppItemType::mvCombo'
    LISTBOX = 'mvAppItemType::mvListbox'
    SLIDER_INT = 'mvAppItemType::mvSliderInt'
    SLIDER_FLOAT = 'mvAppItemType::mvSliderFloat'
    IMAGE = 'mvAppItemType::mvImage'
    PROGRESS_BAR = 'mvAppItemType::mvProgressBar'
    COLOR_PICKER = 'mvAppItemType::mvColorPicker'

    # Контейнеры
    WINDOW_APP_ITEM = 'mvAppItemType::mvWindowAppItem'
    CHILD_WINDOW = 'mvAppItemType::mvChildWindow'
    GROUP = 'mvAppItemType::mvGroup'
    TAB_BAR = 'mvAppItemType::mvTabBar'
    MENU_BAR = 'mvAppItemType::mvMenuBar'
    TOOLTIP = 'mvAppItemType::mvTooltip'
    COLLAPSING_HEADER = 'mvAppItemType::mvCollapsingHeader'

    # Редактор узлов
    NODE_EDITOR = 'mvAppItemType::mvNodeEditor'
    NODE = 'mvAppItemType::mvNode'
    NODE_LINK = 'mvAppItemType::mvNodeLink'
    NODE_ATTRIBUTE = 'mvAppItemType::mvNodeAttribute'

    # Обработчики
    HANDLER_REGISTRY = 'mvAppItemType::mvHandlerRegistry'
    FONT_REGISTRY = 'mvAppItemType::mvFontRegistry'