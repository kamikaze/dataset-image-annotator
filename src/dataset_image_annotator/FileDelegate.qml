import QtQuick
import QtQuick.Controls

/*
 * FileDelegate
 * displays a single file/directory icon etc.
 *
 */

Item {
        id: root
        signal open();

        property string path: {
                if (fileName === ".") {
                        return filePath.slice(0, -1)
                } else if (fileName === "..") {
                        return filePath.split("/").slice(0, -2).join("/") + "/"
                } else if (isDir) {
                        return filePath + "/"
                } else {
                        return filePath
                }
        }

        property bool isImage: {
                switch (fileSuffix) {
                case "png":
                case "jpg":
                case "jpeg":
                case "gif":
                        return true
                default:
                        return false
                }
        }

        property bool isDir: fileIsDir

        Rectangle {
                clip: true

                // hover effect
                color: mouse.containsMouse ? "gray" : "transparent"

                width: Math.floor(browser.width / browser.columns)
                height: width + text.height

                Item {
                        anchors.fill: parent
                        anchors.margins: 10

                        Image {
                                x: 0
                                y: 0
                                width: parent.width
                                height: width
                                fillMode: Image.PreserveAspectFit
                                asynchronous: true
                                source: {
                                        if (isDir) {
                                                "qrc:/icons/folder.png"
                                        } else if (isImage) {
                                                "file://" + filePath
                                        } else {
                                                "qrc:/icons/file.png"
                                        }
                                }
                        }

                        Text {
                                id: text
                                anchors.bottom: parent.bottom
                                x: 10
                                width: parent.width - 20
                                color: "white"
                                text: fileName
                                elide: Text.ElideRight
                        }
                }

                MouseArea {
                        id: mouse
                        anchors.fill: parent
                        acceptedButtons: Qt.LeftButton | Qt.RightButton
                        onClicked: {
                                if (mouse.button === Qt.RightButton) {
                                        if (!fileIsDir && !isImage)
                                                return;
                                        // just open the context menu
                                        contextMenu.x = mouseX
                                        contextMenu.y = mouseY
                                        contextMenu.open()
                                } else {
                                        open()
                                }
                        }
                        hoverEnabled: true

                        // context menu
                        // dunno what to put there, but whatever
                        Menu {
                                id: contextMenu
                                Action {
                                        text: "&Open"
                                        onTriggered: open()
                                }
                        }
                }

        }
}
