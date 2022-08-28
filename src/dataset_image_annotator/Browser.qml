import QtQuick
import Qt.labs.folderlistmodel
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: root

    /*
     * `dir` holds directory being browsed
     * `activePath` holds currently opened dir **OR** file
     * `size` holds reference delegate width
     *        it is only reference as it will be adjusted to fit the total width of the browser
     * `columns` holds the number of grid columns (calculated from total width and icon width, see `size`)
     */

    property string dir
    property string activePath: dir
    property int    size: 100
    property int    columns: Math.round(width / size)

    anchors.fill: parent
    color: "black"

    FolderListModel {
        id: folder
        showDotAndDotDot: true
        showDirsFirst: true
        folder: "file://" + dir
    }

    Viewer {
        id: viewer
        onClosed: activePath = dir
    }

    ScrollView {
        anchors.fill: parent
        ScrollBar.vertical.policy: ScrollBar.AsNeeded
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        clip: true

        GridView {
            id: grid
            // list the entries
            anchors.fill: parent
            model: folder
            delegate: FileDelegate {
                onOpen: {
                    if (isImage) {
                        viewer.openFor(path)
                        activePath = path
                    } else if (isDir){
                        dir = path
                        grid.contentY = 0
                    } else {
                    }
                }
            }
            cellWidth: Math.floor(root.width / root.columns)
            cellHeight: cellWidth + 20
            boundsBehavior: Flickable.StopAtBounds
        }
    }

}
