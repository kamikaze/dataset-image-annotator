import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    width: 640
    height: 480
    visible: true

    menuBar: MenuBar {
        Menu {
            title: "&File"
            MenuItem {
                text: "&Quit"
//                shortcut: "ctrl+q"
                onTriggered: Qt.quit()
            }
        }
    }

    Browser {
        id: browser
        dir: HOME_PATH
        // `HOME_PATH` registered in main.cpp
    }

//    statusBar: Status {
//        activePath: browser.activePath
//    }
}