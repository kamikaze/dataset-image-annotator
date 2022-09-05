import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication


def get_parsed_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--data-root', type=str)

    args, args_other = parser.parse_known_args()

    return args


def main():
    args = get_parsed_args()
    data_root_path = Path(args.data_root)

    app = QApplication(sys.argv)

    ui_file_name = 'main_window.ui'
    ui_file = QFile(Path(__file__).resolve().parent / ui_file_name)

    if not ui_file.open(QIODevice.ReadOnly):
        print(f'Cannot open {ui_file_name}: {ui_file.errorString()}')
        sys.exit(-1)

    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()

    if not window:
        print(loader.errorString())
        sys.exit(-1)

    window.show()

    sys.exit(app.exec())


main()
