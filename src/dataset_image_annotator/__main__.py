import argparse
import sys
from pathlib import Path
from typing import Sequence, Union

import rawpy
from PySide6.QtCore import QFile, QIODevice, QDir, QFileInfo, QModelIndex
from PySide6.QtGui import QPixmap, QScreen, QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication, QGraphicsScene, QFileDialog, QFileSystemModel, QListView, QFileIconProvider
)


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


def get_raw_thumbnail(path: Union[str, Path]):
    with rawpy.imread(str(path)) as raw:
        try:
            thumb = raw.extract_thumb()
        except rawpy.LibRawNoThumbnailError:
            print('no thumbnail found')
        except rawpy.LibRawUnsupportedThumbnailError:
            print('unsupported thumbnail')
        else:
            return thumb


class RawIconProvider(QFileIconProvider):
    def icon(self, file_info: QFileInfo) -> QIcon:
        if isinstance(file_info, QFileInfo):
            file_path = file_info.absoluteFilePath()
            file_name = file_info.fileName().lower()

            if file_name.endswith('.arw'):
                thumbnail_dir_path = Path(f'{Path(file_path).parent}/.thumbs')

                thumbnail_dir_path.mkdir(exist_ok=True)
                thumbnail_path = Path(f'{thumbnail_dir_path}/{file_name}.png')
                thumb_pixmap = QPixmap()

                if thumbnail_path.exists():
                    thumb_pixmap.load(str(thumbnail_path))
                else:
                    thumbnail = get_raw_thumbnail(file_path)
                    thumb_pixmap.loadFromData(thumbnail.data)
                    thumb_pixmap = thumb_pixmap.scaledToWidth(80)

                    f = QFile(thumbnail_path)
                    f.open(QIODevice.OpenModeFlag.WriteOnly)
                    thumb_pixmap.save(f, 'PNG')

                return QIcon(thumb_pixmap)

            return super().icon(self.IconType.File)


class MainWindow:
    def __init__(self, data_root_path: Path):
        self.data_root_path = data_root_path
        ui_file_name = 'main_window.ui'
        ui_file = QFile(Path(__file__).resolve().parent / ui_file_name)

        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            print(f'Cannot open {ui_file_name}: {ui_file.errorString()}')
            sys.exit(-1)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.set_data_root_path(str(data_root_path))
        self.window.path_browser_button.clicked.connect(self.browse_directory)
        self.window.path_edit.textChanged.connect(self.load_images)

        if self.data_root_path:
            self.load_images()

        if not self.window:
            print(loader.errorString())
            sys.exit(-1)

        self.window.thumbnail_list_view.clicked.connect(self.on_file_selected)
        self.window.showMaximized()

    def browse_directory(self):
        path = QFileDialog.getExistingDirectory(self.window, 'Select dataset directory', str(self.data_root_path),
                                                options=QFileDialog.Option.ShowDirsOnly)
        self.set_data_root_path(path)

    def on_file_selected(self, index: QModelIndex):
        file_name = index.data()
        file_path = Path(self.data_root_path, file_name)

        thumb = get_raw_thumbnail(file_path)
        thumb_pixmap = QPixmap()
        thumb_pixmap.loadFromData(thumb.data)

        scene = QGraphicsScene()
        scene.addPixmap(thumb_pixmap)
        self.window.photo_view.setScene(scene)

    def set_data_root_path(self, path: str):
        self.window.path_edit.setText(path)
        self.data_root_path = Path(path)

    def load_images(self):
        image_file_paths = list_dir_images(self.data_root_path)

        if image_file_paths:
            model = QFileSystemModel()
            model.setFilter(QDir.Filter.Files)
            model.setNameFilters(('*.arw',))
            model.setNameFilterDisables(False)
            model.setRootPath(QDir.rootPath())
            model.setIconProvider(RawIconProvider())
            self.window.thumbnail_list_view.setViewMode(QListView.ViewMode.IconMode)
            self.window.thumbnail_list_view.setLayoutMode(QListView.LayoutMode.Batched)
            self.window.thumbnail_list_view.setBatchSize(20)
            self.window.thumbnail_list_view.setModel(model)
            self.window.thumbnail_list_view.setRootIndex(model.index(str(self.data_root_path)))


def main():
    args = get_parsed_args()
    data_root_path = Path(args.data_root).expanduser()

    app = QApplication(sys.argv)
    mainwindow = MainWindow(data_root_path)

    sys.exit(app.exec())


main()
