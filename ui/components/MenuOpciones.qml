import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Drawer {
    id: root
    width: 300
    // modal: false y dim: false convierten el Drawer en un panel lateral fijo
    modal: false 
    dim: false   
    closePolicy: Popup.NoAutoClose
    background: Rectangle { color: "#1e1e2e" }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        Text {
            text: "Opciones SIRD"
            color: "white"
            font.pixelSize: 22
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        // --- Tus controles futuros irían aquí ---
        Label { text: "Tasa de Contagio (β):"; color: "#bbbbbb" }
        Slider { Layout.fillWidth: true; value: 0.3 }

        Label { text: "Tasa de Recuperación (γ):"; color: "#bbbbbb" }
        Slider { Layout.fillWidth: true; value: 0.1 }

        Item { Layout.fillHeight: true } // Espaciador para empujar todo hacia arriba
    }
}
