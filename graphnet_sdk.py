import argparse
import sys
import zipfile
from pathlib import Path


class GraphNetSDK:

    PROJECT_ROOT: Path = Path(__file__).resolve().parent

    INIT_PY_TEMPLATE: str = '''from Src.Config.node_annotation import NodeAnnotation
from .extension_config import {class_name}

EXTENSION_NAME = "{ext_name}"

EXTENSION_CONFIG = {{
    "{ext_name}": [
        NodeAnnotation(
            label="{class_name}",
            node_type={class_name},
            logic={class_name}.compute,
            annotations={{}},
            input=False,
            output=False
        )
    ]
}}
'''

    EXTENSION_CONFIG_TEMPLATE: str = '''from Src.Nodes import AbstractNode

class {class_name}(AbstractNode):
    def setup(self):
        pass

    def compute(self):
        pass
'''

    @classmethod
    def init_extension(cls, ext_name: str) -> None:
        target_dir: Path = Path.cwd() / ext_name

        if target_dir.exists():
            sys.exit(1)

        target_dir.mkdir(parents=True)
        
        class_name: str = ext_name.replace("-", "_").replace(" ", "_").title().replace("_", "") + "Node"
        
        init_content: str = cls.INIT_PY_TEMPLATE.format(
            class_name=class_name,
            ext_name=ext_name,
        )
        (target_dir / "__init__.py").write_text(init_content, encoding="utf-8")

        config_content: str = cls.EXTENSION_CONFIG_TEMPLATE.format(
            class_name=class_name
        )
        (target_dir / "extension_config.py").write_text(config_content, encoding="utf-8")


    @classmethod
    def compile_extension(cls, source_path: str, output_name: str = None) -> None:
        source_dir: Path = Path(source_path).resolve()

        if not source_dir.is_dir():
            sys.exit(1)

        required_files: list[str] = ["__init__.py", "extension_config.py"]
        missing: list[str] = [f for f in required_files if not (source_dir / f).exists()]
        
        if missing:
            sys.exit(1)

        final_output_name: str = output_name if output_name else f"{source_dir.name}.zip"
        output_path: Path = Path(final_output_name).resolve()

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_dir.rglob('*'):
                if '__pycache__' in file_path.parts or file_path.suffix == '.pyc':
                    continue
                arcname: str = f"{source_dir.name}/{file_path.relative_to(source_dir)}"
                zf.write(file_path, arcname)


    @classmethod
    def run_extension(cls, zip_file_path: str, overwrite: bool = False) -> None:
        zip_path: Path = Path(zip_file_path).resolve()

        if not zip_path.exists():
            sys.exit(1)

        if str(cls.PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(cls.PROJECT_ROOT))

        from Src.Managers.extension_manager import ExtensionManager
        from Src.Enums import ExtensionStatus

        manager = ExtensionManager()

        extension = manager.install_from_zip(zip_path, overwrite=overwrite)

        if extension.status != ExtensionStatus.DISCOVERED:
            sys.exit(1)

        manager.load_active_extensions([extension])

    @classmethod
    def execute(cls) -> None:
        parser = argparse.ArgumentParser(prog="graphnet_sdk")
        subparsers = parser.add_subparsers(dest="command")

        init_parser = subparsers.add_parser("init")
        init_parser.add_argument("name")

        compile_parser = subparsers.add_parser("compile")
        compile_parser.add_argument("path")
        compile_parser.add_argument("-o", "--output", default=None)

        run_parser = subparsers.add_parser("run")
        run_parser.add_argument("zip_file")
        run_parser.add_argument("--overwrite", action="store_true")

        args = parser.parse_args()

        if args.command is None:
            parser.print_help()
            sys.exit(0)

        commands = {
            "init": lambda: cls.init_extension(args.name),
            "compile": lambda: cls.compile_extension(args.path, args.output),
            "run": lambda: cls.run_extension(args.zip_file, args.overwrite)
        }

        commands[args.command]()

if __name__ == "__main__":
    GraphNetSDK.execute()