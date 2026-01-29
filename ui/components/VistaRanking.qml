import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    anchors.fill: parent

    signal volverClicked()

    property var rankingData: [] 

    function cargarDatos() {
        if(backend) {
            rankingData = backend.obtener_ranking_global()
        }
    }

    Component.onCompleted: cargarDatos()

    // Fondo Oscuro
    Rectangle {
        anchors.fill: parent
        color: "#1e1e2e"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        // --- CABECERA ---
        RowLayout {
            Layout.fillWidth: true
            Button {
                text: "⬅ Volver"
                flat: true
                onClicked: root.volverClicked()
                contentItem: Text { text: parent.text; color: "#bdc3c7"; font.bold: true }
                background: Rectangle { color: "#3a3f55"; radius: 5 }
            }
            Item { Layout.fillWidth: true } 
            Text {
                text: "Ranking Global de Infección"
                color: "white"
                font.pixelSize: 22
                font.bold: true
                font.letterSpacing: 1
            }
            Item { Layout.fillWidth: true }
            Item { width: 80 } // Equilibrio
        }

        // --- ENCABEZADOS DE TABLA ---
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            Text { text: "#"; color: "#7f8c8d"; font.bold: true; width: 30 }
            Text { text: "PAÍS"; color: "#7f8c8d"; font.bold: true; Layout.fillWidth: true }
            Text { text: "INFECTADOS"; color: "#ff5252"; font.bold: true; width: 100; horizontalAlignment: Text.AlignRight }
            Text { text: "% POBLACIÓN"; color: "#DCE775"; font.bold: true; width: 100; horizontalAlignment: Text.AlignRight }
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#444" }

        // --- LISTA OPTIMIZADA (ListView) ---
        ListView {
            id: listaPaises
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: root.rankingData
            spacing: 8

            // Barra de desplazamiento personalizada
            ScrollBar.vertical: ScrollBar { 
                active: true
                policy: ScrollBar.AsNeeded
            }

            delegate: Item {
                width: listaPaises.width
                height: 50

                // Datos del modelo (proporcionados por el array de JS)
                readonly property var dato: modelData
                readonly property int posicion: index + 1
                readonly property real porcentaje: dato.ratio * 100

                // Fondo de la fila
                Rectangle {
                    anchors.fill: parent
                    color: "#2f3542"
                    radius: 5
                    
                    // BARRA DE PROGRESO DE FONDO
                    Rectangle {
                        width: parent.width * (dato.ratio) // Ancho basado en % infección
                        height: parent.height
                        color: "#33ff5252" // Rojo semitransparente
                        radius: 5
                        
                        // Animación suave al cargar
                        Behavior on width { NumberAnimation { duration: 600; easing.type: Easing.OutCubic } }
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 15
                    anchors.rightMargin: 15
                    spacing: 15

                    // 1. Posición
                    Text { 
                        text: posicion
                        color: posicion <= 3 ? "#ffb74d" : "white" // Top 3 en dorado
                        font.bold: true
                        font.pixelSize: 16
                        width: 30
                    }

                    // 2. Bandera (Círculo simple con código) y Nombre
                    Row {
                        Layout.fillWidth: true
                        spacing: 10
                        Rectangle {
                            width: 30; height: 20
                            color: "#444"; radius: 2
                            Text { 
                                anchors.centerIn: parent
                                text: dato.codigo
                                color: "#aaa"; font.pixelSize: 9
                            }
                        }
                        Text { 
                            text: dato.nombre
                            color: "white"
                            font.pixelSize: 14
                            font.bold: true
                            elide: Text.ElideRight
                            width: parent.width - 40
                        }
                    }

                    // 3. Cantidad Infectados
                    Text { 
                        text: Number(dato.infectados).toLocaleString(Qt.locale(), 'f', 0)
                        color: "#ff5252"
                        font.pixelSize: 14
                        font.bold: true
                        Layout.preferredWidth: 100
                        horizontalAlignment: Text.AlignRight
                    }

                    // 4. Porcentaje
                    Text { 
                        text: porcentaje.toFixed(2) + "%"
                        color: "#DCE775"
                        font.pixelSize: 14
                        font.bold: true
                        Layout.preferredWidth: 100
                        horizontalAlignment: Text.AlignRight
                    }
                }
            }
        }
        
        // Mensaje si está vacío
        Text {
            visible: root.rankingData.length === 0
            text: "No hay datos de infección aún.\nEspera a que el virus se propague."
            color: "#777"
            font.italic: true
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
