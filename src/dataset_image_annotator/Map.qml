import QtQuick

/*
 * This object displays a "map" of the image as it is currently viewed
 * ona can click/drag the inner rectangle to navigate through the image being viewed
 *
 * `outer` represents the image (and should have appropriate aspect ratio)
 * `inner` represents the viewing screen (-//-)
 */

Rectangle {
    id: outer

    required property Flickable container

    // position and size the map
    anchors.bottom: parent.bottom
    anchors.right: parent.right
    anchors.bottomMargin: 10
    anchors.rightMargin: 10
    height: container.height / 5
    width: height * container.imageAspectRatio

    // some theming
    radius: 8
    color: "#aa444444"

    states: [
            State {
                    name: "hover"
                    when: mouse.containsMouse || mouse.pressed
                    PropertyChanges {
                            target: outer
                            color: "#dd444444"
                    }
            }
    ]

    transitions: [
            Transition {
                    to: "*"
                    ColorAnimation { target: outer; duration: 100 }
            }

    ]

    // </theming>

    Rectangle {
            id: inner
            color: "#bb777777"
            radius: 8

            // mafs
            x: parent.width * container.contentX / container.contentWidth
            width: Math.min(parent.width * container.width / container.contentWidth, parent.width)
            y: parent.height * container.contentY / container.contentHeight
            height: Math.min(parent.height * container.height / container.contentHeight, parent.height)
            onXChanged: container.contentX = x * container.contentWidth  / parent.width
            onYChanged: container.contentY = y * container.contentHeight / parent.height
    }

    MouseArea {
            id: mouse
            anchors.fill: parent
            hoverEnabled: true

            // dragging is annoying
            // this works just with clicking and/or holding:
            onMouseXChanged: {
                    if (!pressed) return

                    let tmp = (mouseX - inner.width / 2) / outer.width * container.contentWidth

                    if (tmp < 0)
                            tmp = 0
                    else if (tmp > container.contentWidth - container.width)
                            tmp = container.contentWidth - container.width

                    container.contentX = tmp
            }
            onMouseYChanged: {
                    if (!pressed) return

                    let tmp = (mouseY - inner.height / 2) / outer.height * container.contentHeight

                    if (tmp < 0)
                            tmp = 0
                    else if (tmp > container.contentHeight - container.height)
                            tmp = container.contentHeight - container.height

                    container.contentY = tmp
            }
    }

}