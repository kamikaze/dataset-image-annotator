import argparse
import sys
from pathlib import Path
from typing import Sequence

import rawpy
from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QLabel, QGraphicsScene, QFileDialog


def get_parsed_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--data-root', type=str)
    # parser.add_argument('--datasets', metavar='DS', type=str, nargs='+')

    args, args_other = parser.parse_known_args()

    return args


def list_dir_images(path: Path) -> Sequence[Path]:
    if path.is_dir():
        files = sorted(path.glob('*.ARW'))
    else:
        raise FileNotFoundError('Path must be directory')

    return files


def get_raw_thumbnail(path: Path):
    with rawpy.imread(str(path)) as raw:
        try:
            thumb = raw.extract_thumb()
        except rawpy.LibRawNoThumbnailError:
            print('no thumbnail found')
        except rawpy.LibRawUnsupportedThumbnailError:
            print('unsupported thumbnail')
        else:
            return thumb


class MainWindow:
    def __init__(self, data_root_path: Path):
        self.data_root_path = data_root_path
        ui_file_name = 'main_window.ui'
        ui_file = QFile(Path(__file__).resolve().parent / ui_file_name)

        if not ui_file.open(QIODevice.ReadOnly):
            print(f'Cannot open {ui_file_name}: {ui_file.errorString()}')
            sys.exit(-1)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.set_data_root_path(str(data_root_path))
        self.window.path_browser_button.clicked.connect(self.browse_directory)
        self.window.path_edit.textChanged.connect(self.load_images)

        if not self.window:
            print(loader.errorString())
            sys.exit(-1)

        self.window.show()

    def browse_directory(self):
        path = QFileDialog.getExistingDirectory(self.window, 'Select dataset directory', str(self.data_root_path),
                                                options=QFileDialog.Option.ShowDirsOnly)
        self.set_data_root_path(path)

    def set_data_root_path(self, path: str):
        self.window.path_edit.setText(path)
        self.data_root_path = Path(path)

    def load_images(self):
        image_file_paths = list_dir_images(self.data_root_path)

        if image_file_paths:
            thumb = get_raw_thumbnail(image_file_paths[0])
            thumb_pixmap = QPixmap()
            thumb_pixmap.loadFromData(thumb.data)

            image_label = QLabel()
            image_label.setPixmap(thumb_pixmap)
            scene = QGraphicsScene()
            scene.addWidget(image_label)
            self.window.photo_view.setScene(scene)


def main():
    args = get_parsed_args()
    data_root_path = Path(args.data_root)

    app = QApplication(sys.argv)
    window = MainWindow(data_root_path)

    sys.exit(app.exec())


main()
