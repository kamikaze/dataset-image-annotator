import argparse
import os
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle


def get_parsed_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--data-root', type=str)

    args, args_other = parser.parse_known_args()

    return args


def main():
    args = get_parsed_args()
    data_root_path = Path(args.data_root)

    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle('Fusion')
    engine = QQmlApplicationEngine()
    engine.load(os.fspath(Path(__file__).resolve().parent / 'main.qml'))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


main()
