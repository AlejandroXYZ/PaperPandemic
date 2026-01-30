import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    anchors.fill: parent

    property var modeloNoticias: []

    // Conectar señal para actualizar lista en vivo
    Connections {
        target: backend
        function onNoticiasActualizadas() {
            root.cargarNoticias()
        }
    }

    function cargarNoticias() {
        if(backend) {
            modeloNoticias = backend.obtener_historial_noticias()
        }
    }

    Component.onCompleted: cargarNoticias()

    // Fondo oscuro
    Rectangle { anchors.fill: parent; color: "#1e1e2e" }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 40
        spacing: 20

        // CABECERA
        RowLayout {
            Layout.fillWidth: true
            Button {
                text: "⬅ Volver al Mapa"
                flat: true
                background: Rectangle { color: "#3a3f55"; radius: 5 }
                contentItem: Text { text: parent.text; color: "#ccc"; font.bold: true }
                onClicked: mainWindow.vistaActual = "mapa"
            }
            
            Item { Layout.fillWidth: true }
            
            Text {
                text: "📡 NOTICIAS MUNDIALES"
                color: "white"
                font.bold: true
                font.pixelSize: 28
                font.letterSpacing: 2
            }
            
            Item { Layout.fillWidth: true }
            Item { width: 100 }
        }

        Rectangle { Layout.fillWidth: true; height: 2; color: "#444" }

        // LISTA DE NOTICIAS
        ListView {
            id: lista
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: root.modeloNoticias
            spacing: 8

            delegate: Rectangle {
                id: card
                width: lista.width
                height: 60
                radius: 6
                
                // Lógica de colores según tipo
                color: {
                    if (modelData.tipo === "INFECT") return "#2c0b0e" // Rojo muy oscuro
                    if (modelData.tipo === "CURE") return "#0b1a2c"   // Azul muy oscuro
                    if (modelData.tipo === "DEATH") return "#1a1a1a"  // Gris casi negro
                    return "#2f3542" // Gris estándar
                }

                // Borde izquierdo de color para identificar rápido
                Rectangle {
                    width: 5; height: parent.height
                    color: {
                        if (modelData.tipo === "INFECT") return "#ff5252"
                        if (modelData.tipo === "CURE") return "#4fc3f7"
                        if (modelData.tipo === "DEATH") return "#7f8c8d"
                        return "#bdc3c7"
                    }
                    anchors.left: parent.left
                }

                // Efecto Hover (Iluminación)
                MouseArea {
                    id: ma
                    anchors.fill: parent
                    hoverEnabled: true
                }
                
                border.color: ma.containsMouse ? "#ffffff" : "transparent"
                border.width: 1
                opacity: ma.containsMouse ? 1.0 : 0.8

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20
                    spacing: 20

                    // DÍA
                    Rectangle {
                        width: 60; height: 30
                        color: "#444"; radius: 4
                        Text {
                            anchors.centerIn: parent
                            text: "Día " + modelData.dia
                            color: "#fff"; font.bold: true; font.pixelSize: 12
                        }
                    }

                    // MENSAJE
                    Text {
                        Layout.fillWidth: true
                        text: modelData.mensaje
                        color: "white"
                        font.pixelSize: 16
                        font.family: "Segoe UI"
                        wrapMode: Text.WordWrap
                    }
                    
                    // ICONO
                    Text {
                        text: {
                            if (modelData.tipo === "INFECT") return "☣️"
                            if (modelData.tipo === "CURE") return "💉"
                            if (modelData.tipo === "DEATH") return "💀"
                            return "ℹ️"
                        }
                        font.pixelSize: 20
                    }
                }
            }
        }
    }
}
