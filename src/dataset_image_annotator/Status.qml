import QtQuick
import QtQuick.Controls

StatusBar {
        id: statusbar
        property alias activePath: text.text

        // just display the active path, idk what else
        Text {
            id: text
        }
}
