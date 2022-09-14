import argparse
import sys
from pathlib import Path
from typing import Sequence

import rawpy
from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QLabel, QGraphicsScene


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


def main():
    args = get_parsed_args()
    data_root_path = Path(args.data_root)
    image_file_paths = list_dir_images(data_root_path)

    app = QApplication(sys.argv)

    if image_file_paths:
        thumb = get_raw_thumbnail(image_file_paths[0])
        thumb_pixmap = QPixmap()
        thumb_pixmap.loadFromData(thumb.data)

    ui_file_name = 'main_window.ui'
    ui_file = QFile(Path(__file__).resolve().parent / ui_file_name)

    if not ui_file.open(QIODevice.ReadOnly):
        print(f'Cannot open {ui_file_name}: {ui_file.errorString()}')
        sys.exit(-1)

    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()

    image_label = QLabel()
    image_label.setPixmap(thumb_pixmap)
    scene = QGraphicsScene()
    scene.addWidget(image_label)
    window.photo_view.setScene(scene)

    if not window:
        print(loader.errorString())
        sys.exit(-1)

    window.show()
    sys.exit(app.exec())


main()
