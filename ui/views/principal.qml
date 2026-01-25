import QtQuick
import QtQuick.Controls
import Qt5Compat.GraphicalEffects


Page {
    title: "Menú Principal"
    property bool playing : false
    
    header: ToolBar{
        Button {
            anchors.horizontalCenter: parent.horizontalCenter
            id: play_button
            text: playing ? "pausa" : "play"

            onClicked: {
                playing = !playing
            }
        }
    }


    footer: TabBar {
        id: barraPestañas
        TabButton {text: "Botón1"}
        TabButton { text: "Botón2"}
        TabButton { text: "Botón3"}
        TabButton { text: "Botón4"}
    }

    Item {
        id: worldContainer
        anchors.fill: parent
        anchors.centerIn: parent
    
        Image {
            id: worldOriginal
            source: "../../assets/world.svg"
            anchors.fill: parent
            sourceSize: Qt.size(parent.width, parent.height)
            fillMode: Image.PreserveAspectFit
            visible: false 
        }
    
        ColorOverlay {
            anchors.fill: worldOriginal
            source: worldOriginal
            color: "white" 
        }
    }
    

}
