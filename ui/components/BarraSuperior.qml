import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ToolBar {
    id: root
    height: 60
    background: Rectangle { color: "#1e1e2e" }

    // --- SEÑALES PARA COMUNICARSE CON EL EXTERIOR ---
    signal menuClicked()
    signal playPauseClicked(bool isPlaying)
    signal resetClicked()

    // Botón Menú (Izquierda)
    ToolButton {
        id: menuButton
        text: "☰"
        font.pixelSize: 24
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 10
        // Al hacer clic, emite la señal
        onClicked: root.menuClicked() 
    }

    // Botones de Simulación (Centrados)
    Row {
        anchors.centerIn: parent
        spacing: 15

        RoundButton {
            id: playPauseButton
            property bool isPlaying: false
            width: 45; height: 45
            
            background: Rectangle {
                color: playPauseButton.isPlaying ? "#ffb8b8" : "#DCE775"
                radius: width / 2 
            }
            contentItem: Text {
                text: playPauseButton.isPlaying ? "⏸" : "▶" 
                color: "#121212"
                font.pixelSize: 20
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: {
                isPlaying = !isPlaying
                root.playPauseClicked(isPlaying) // Emite la señal
            }
        }

        RoundButton {
            id: resetButton
            width: 45; height: 45
            
            background: Rectangle { color: "#747d8c"; radius: width / 2 }
            contentItem: Text {
                text: "⟲"
                color: "white"
                font.pixelSize: 24
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            onClicked: {
                playPauseButton.isPlaying = false
                root.resetClicked() // Emite la señal
            }
        }
    }
}
