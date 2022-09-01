import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from dataset_image_annotator.main_window import MainWindow


def get_parsed_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--data-root', type=str)

    args, args_other = parser.parse_known_args()

    return args


def main():
    args = get_parsed_args()
    data_root_path = Path(args.data_root)

    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())


main()
