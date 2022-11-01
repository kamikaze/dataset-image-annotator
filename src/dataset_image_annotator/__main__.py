import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, Union, Optional

import rawpy
from PySide6.QtCore import QFile, QIODevice, QDir, QFileInfo, QModelIndex, Qt, QStringListModel
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication, QGraphicsScene, QFileDialog, QFileSystemModel, QListView, QFileIconProvider, QCompleter
)


def get_parsed_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--data-root', type=str)
    # parser.add_argument('--datasets', metavar='DS', type=str, nargs='+')

    args, args_other = parser.parse_known_args()

    return args


def list_dir(path: Path, mask: str) -> Sequence[Path]:
    if path.is_dir():
        files = sorted(path.glob(mask))
    else:
        raise FileNotFoundError('Path must be directory')

    return files


def list_dir_images(path: Path) -> Sequence[Path]:
    return list_dir(path, '*.ARW')


def list_dir_metadata(path: Path) -> Optional[Sequence[Path]]:
    metadata_dir_path = Path(path, '.metadata')

    if metadata_dir_path.exists():
        return list_dir(metadata_dir_path, '*.json')

    return None


def load_metadata(data_root_path: Path):
    metadata_files = list_dir_metadata(data_root_path)

    if not metadata_files:
        return

    metadata = {}

    for metadata_file in metadata_files:
        try:
            with open(metadata_file, 'r') as f:
                metadata[metadata_file.name.lower()] = json.load(f)
        except FileNotFoundError:
            pass

    return metadata

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
        self.data_root_path = None
        self.metadata = {}
        self.types = set()
        self.makes = set()
        self.models = set()
        self.bodies = set()
        self.colors = set()

        ui_file_name = 'main_window.ui'
        ui_file = QFile(Path(__file__).resolve().parent / ui_file_name)

        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            print(f'Cannot open {ui_file_name}: {ui_file.errorString()}')
            sys.exit(-1)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.type_completer = QCompleter()
        self.type_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.type_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.type_completer.setWidget(self.window.type_combo_box)
        self.make_completer = QCompleter()
        self.make_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.make_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.make_completer.setWidget(self.window.make_combo_box)
        self.model_completer = QCompleter()
        self.model_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.model_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.model_completer.setWidget(self.window.model_combo_box)
        self.body_completer = QCompleter()
        self.body_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.body_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.body_completer.setWidget(self.window.body_combo_box)
        self.color_completer = QCompleter()
        self.color_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.color_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.color_completer.setWidget(self.window.color_combo_box)

        self.window.path_browser_button.clicked.connect(self.browse_directory)
        self.window.path_edit.textChanged.connect(self.on_data_root_path_changed)

        if data_root_path:
            self.window.path_edit.setText(str(data_root_path))

        if not self.window:
            print(loader.errorString())
            sys.exit(-1)

        self.window.thumbnail_list_view.clicked.connect(self.on_file_selected)
        self.window.showMaximized()

    def browse_directory(self):
        path = QFileDialog.getExistingDirectory(self.window, 'Select dataset directory', str(self.data_root_path),
                                                options=QFileDialog.Option.ShowDirsOnly)
        self.window.path_edit.setText(path)

    def on_file_selected(self, index: QModelIndex):
        file_name = index.data()
        file_path = Path(self.data_root_path, file_name)

        thumb = get_raw_thumbnail(file_path)
        thumb_pixmap = QPixmap()
        thumb_pixmap.loadFromData(thumb.data)

        scene = QGraphicsScene()
        scene.addPixmap(thumb_pixmap)
        self.window.photo_view.setScene(scene)

        self.window.type_combo_box.setEnabled(True)
        self.window.type_combo_box.setCompleter(self.type_completer)
        self.window.make_combo_box.setEnabled(True)
        self.window.make_combo_box.setCompleter(self.make_completer)
        self.window.model_combo_box.setEnabled(True)
        self.window.model_combo_box.setCompleter(self.model_completer)
        self.window.body_combo_box.setEnabled(True)
        self.window.body_combo_box.setCompleter(self.body_completer)
        self.window.color_combo_box.setEnabled(True)
        self.window.color_combo_box.setCompleter(self.color_completer)


    def on_data_root_path_changed(self):
        self.data_root_path = Path(self.window.path_edit.text())
        self.load_images(self.data_root_path)
        self.metadata = load_metadata(self.data_root_path)

        self.types = set()
        self.makes = set()
        self.models = set()
        self.bodies = set()
        self.colors = set()

        for item in self.metadata.values():
            if _type := item.get('type'):
                self.types.add(_type)

            if make := item.get('make'):
                self.makes.add(make)

            if model := item.get('model'):
                self.models.add(model)

            if body := item.get('body'):
                self.bodies.add(body)

            if color := item.get('color'):
                self.colors.add(color)

        self.window.type_combo_box.clear()
        self.window.type_combo_box.addItems(sorted(self.types))
        self.type_completer.setModel(QStringListModel(sorted(self.types)))

        self.window.make_combo_box.clear()
        self.window.make_combo_box.addItems(sorted(self.makes))
        self.make_completer.setModel(QStringListModel(sorted(self.makes)))

        self.window.model_combo_box.clear()
        self.window.model_combo_box.addItems(sorted(self.models))
        self.model_completer.setModel(QStringListModel(sorted(self.models)))

        self.window.body_combo_box.clear()
        self.window.body_combo_box.addItems(sorted(self.bodies))
        self.body_completer.setModel(QStringListModel(sorted(self.bodies)))

        self.window.color_combo_box.clear()
        self.window.color_combo_box.addItems(sorted(self.colors))
        self.color_completer.setModel(QStringListModel(sorted(self.colors)))

    def load_images(self, data_root_path: Path):
        image_file_paths = list_dir_images(data_root_path)

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
            self.window.thumbnail_list_view.setRootIndex(model.index(str(data_root_path)))


def main():
    args = get_parsed_args()
    data_root_path = Path(args.data_root).expanduser()

    app = QApplication(sys.argv)
    mainwindow = MainWindow(data_root_path)

    sys.exit(app.exec())


main()
