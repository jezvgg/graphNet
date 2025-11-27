# tests/test_file_scanner.py
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from file_manager.scanner import FileScanner, FileItem

# Фикстура pyfakefs автоматически активируется при импорте
@pytest.fixture(autouse=True)
def setup_fs(fs):
    """Автоматически создаёт базовую файловую структуру для всех тестов."""
    fs.create_dir("/test")
    fs.create_file("/test/file1.txt", contents="a" * 1024)  # 1KB
    fs.create_file("/test/.hidden", contents="secret")
    fs.create_dir("/test/folder")
    fs.create_file("/test/script.py", contents="x" * 2048)  # 2KB
    fs.create_file("/test/image.jpg", contents="y" * 3072)  # 3KB
    fs.create_file("/test/document.pdf", contents="z" * 4096)  # 4KB
    
    # Для тестов прав доступа
    fs.create_file("/test/locked.txt", contents="denied")
    fs.chmod("/test/locked.txt", 0o000)  # Запрещаем доступ
    
    # Для тестов сортировки
    fs.create_dir("/test/A_folder")
    fs.create_file("/test/B_file.txt")
    fs.create_dir("/test/Z_folder")
    
    return fs


class TestFileScannerInitialization:
    """Тесты инициализации сканера."""
    
    def test_init_defaults(self):
        scanner = FileScanner()
        assert scanner.show_hidden is False
        assert scanner.dirs_only is False

    def test_init_custom_params(self):
        scanner = FileScanner(show_hidden=True, dirs_only=True)
        assert scanner.show_hidden is True
        assert scanner.dirs_only is True


class TestScanningBasics:
    """Базовое сканирование без фильтров."""
    
    def test_scan_basic_directory(self):
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/test"))
        
        # Проверяем количество элементов (без скрытых файлов)
        assert len(items) == 7  # folder, A_folder, Z_folder, file1.txt, script.py, image.jpg, document.pdf
        
        # Проверяем порядок сортировки: сначала папки
        assert items[0].name == "A_folder"
        assert items[1].name == "Z_folder"
        assert items[2].name == "folder"
        assert items[3].name == "B_file.txt"  # файлы тоже сортируются по алфавиту
        
        # Проверяем форматирование размеров
        file1 = next(i for i in items if i.name == "file1.txt")
        assert file1.size_str == "1.0 KB"
        
        # Проверяем типы
        folder = next(i for i in items if i.name == "folder")
        assert folder.is_dir is True
        assert folder.type_str == "Folder"
        assert folder.icon_tag == "folder"
        
        script = next(i for i in items if i.name == "script.py")
        assert script.is_dir is False
        assert script.type_str == ".py"
        assert script.icon_tag == "python"

    def test_scan_with_hidden_files(self):
        scanner = FileScanner(show_hidden=True)
        items = scanner.scan_directory(Path("/test"))
        
        # Должен включать скрытый файл
        assert len(items) == 8
        hidden = next((i for i in items if i.name == ".hidden"), None)
        assert hidden is not None
        assert hidden.is_dir is False
        assert hidden.size_str == "6.0 B"  # len("secret") = 6


class TestFilters:
    """Тесты фильтрации файлов."""
    
    def test_dirs_only_filter(self):
        scanner = FileScanner(dirs_only=True)
        items = scanner.scan_directory(Path("/test"))
        
        # Только директории
        assert len(items) == 3
        assert all(i.is_dir for i in items)
        dir_names = {i.name for i in items}
        assert dir_names == {"A_folder", "Z_folder", "folder"}

    def test_search_query_filter(self):
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/test"), search_query="file")
        
        # Содержит "file" в названии
        assert len(items) == 2
        names = {i.name for i in items}
        assert names == {"B_file.txt", "file1.txt"}

    def test_file_extension_filter(self):
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/test"), file_filter=".py")
        
        # Только .py файлы + все папки
        assert len(items) == 4  # 3 папки + script.py
        py_files = [i for i in items if not i.is_dir]
        assert len(py_files) == 1
        assert py_files[0].name == "script.py"
        assert py_files[0].icon_tag == "python"

    def test_combined_filters(self):
        scanner = FileScanner(show_hidden=True)
        items = scanner.scan_directory(
            Path("/test"),
            search_query="doc",
            file_filter=".pdf"
        )
        
        # Должен найти только document.pdf
        assert len(items) == 1
        assert items[0].name == "document.pdf"
        assert items[0].type_str == ".pdf"


class TestErrorHandling:
    """Тесты обработки ошибок доступа."""
    
    def test_access_denied_file(self, mocker):
        scanner = FileScanner()
        
        # Имитируем ошибку доступа для locked.txt
        def mock_stat(path):
            if "locked.txt" in str(path):
                raise PermissionError("Access denied")
            return original_stat(path)
        
        original_stat = Path.stat
        mocker.patch("pathlib.Path.stat", side_effect=mock_stat)
        
        items = scanner.scan_directory(Path("/test"))
        
        # Проверяем, что файл с ошибкой присутствует с правильной иконкой
        locked = next((i for i in items if "locked" in i.name), None)
        assert locked is not None
        assert locked.icon_tag == "mini_error"
        assert locked.size_str == "N/A"  # В текущем коде будет "0.0 B", но в FileItem.size_str для ошибок не обрабатывается


class TestSorting:
    """Тесты сортировки результатов."""
    
    def test_sort_order_directories_first(self):
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/test"))
        
        # Первые элементы — директории
        dir_count = sum(1 for i in items if i.is_dir)
        assert all(i.is_dir for i in items[:dir_count])
        
        # Папки отсортированы по алфавиту
        dir_names = [i.name for i in items if i.is_dir]
        assert dir_names == sorted(dir_names)
        
        # Файлы отсортированы по алфавиту
        file_names = [i.name for i in items if not i.is_dir]
        assert file_names == sorted(file_names)

    def test_sort_case_insensitive(self):
        # Создаём файлы с разным регистром
        fs.create_file("/test/apple.txt")
        fs.create_file("/test/Banana.txt")
        fs.create_file("/test/cherry.txt")
        
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/test"))
        
        # Файлы должны быть в алфавитном порядке без учёта регистра
        file_names = [i.name for i in items if not i.is_dir and i.name.endswith(".txt")]
        # Ожидаем: apple.txt, Banana.txt, cherry.txt, file1.txt, B_file.txt
        expected_order = ["apple.txt", "Banana.txt", "cherry.txt", "B_file.txt", "file1.txt"]
        assert file_names[:5] == expected_order


class TestIcons:
    """Тесты определения иконок."""
    
    def test_icon_mapping(self):
        scanner = FileScanner()
        
        # Проверяем маппинг для известных расширений
        assert scanner._get_file_icon(Path("file.py")) == "python"
        assert scanner._get_file_icon(Path("image.jpg")) == "picture"
        assert scanner._get_file_icon(Path("archive.zip")) == "zip"
        
        # Неизвестное расширение → default
        assert scanner._get_file_icon(Path("unknown.xyz")) == "mini_document"
        
        # Директория → folder
        assert scanner._get_file_icon(Path("folder")) == "folder"  # Но в _create_file_item для директорий используется _FOLDER_ICON


class TestEdgeCases:
    """Тесты граничных случаев."""
    
    def test_empty_directory(self):
        fs.create_dir("/empty")
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/empty"))
        assert len(items) == 0

    def test_non_existent_directory(self):
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/nonexistent"))
        assert len(items) == 0  # В текущем коде ловится исключение и возвращается пустой список

    def test_file_as_path(self):
        # Передаём файл вместо директории
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/test/file1.txt"))
        assert len(items) == 0  # iterdir() на файле вызовет NotADirectoryError → пустой список

    def test_large_file_size_formatting(self):
        # Создаём файл размером 2.5 TB
        fs.create_file("/test/huge.bin", st_size=2.5 * 1024**4)
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/test"))
        huge = next(i for i in items if i.name == "huge.bin")
        assert huge.size_str == "2.5 TB"

    def test_special_characters_in_filenames(self):
        fs.create_file("/test/спецсимволы_#$%.txt")
        fs.create_file("/test/emoji_😊.jpg")
        
        scanner = FileScanner()
        items = scanner.scan_directory(Path("/test"))
        
        special = next(i for i in items if "спецсимволы" in i.name)
        emoji = next(i for i in items if "emoji" in i.name)
        
        assert special.name == "спецсимволы_#$%.txt"
        assert emoji.name == "emoji_😊.jpg"
        assert emoji.icon_tag == "picture"