from Tests.DPG_test import DPGUnitTest
from Src.Managers.theme_manager import ThemeManager


class DPGUnitTestWithReset(DPGUnitTest):
    '''
    Расширение DPGUnitTest со сбросом кэша тем.
    Нужен когда тестовый класс пересоздаёт DPG контекст —
    старые ID тем становятся невалидны, кэш необходимо очистить.
    '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Сбрасываем кэш тем — DPG контекст пересоздаётся между тестовыми классами,
        # старые ID тем из предыдущего контекста становятся невалидны
        ThemeManager._created_themes = {}
        ThemeManager._item_themes = {}