import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    anchors.fill: parent

    signal volverClicked()

    property var rankingData: [] 
    
    // Filtro actual: "I" (Infectados), "M" (Muertos), "R" (Recuperados), "S" (Sanos)
    property string currentFilter: "I" 

    // Colores Dinámicos
    property color cTop1: "#ff5252"
    property color cTop2: "#ff7b7b"
    property color cTop3: "#ffbaba"
    property color cRest: "#555555"
    property string labelValor: "Infectados"

    function cargarDatos() {
        if(backend) {
            rankingData = backend.obtener_ranking_global(root.currentFilter)
            actualizarPaleta()
        }
    }

    function actualizarPaleta() {
        switch(currentFilter) {
            case "I": // INFECTADOS
                cTop1 = "#d32f2f"; cTop2 = "#f44336"; cTop3 = "#ff9800"; cRest = "#3a3f55";
                labelValor = "Infectados";
                break;
            case "M": // MUERTOS
                cTop1 = "#000000"; cTop2 = "#424242"; cTop3 = "#757575"; cRest = "#9e9e9e";
                labelValor = "Fallecidos";
                break;
            case "R": // RECUPERADOS
                cTop1 = "#0288d1"; cTop2 = "#03a9f4"; cTop3 = "#4dd0e1"; cRest = "#3a3f55";
                labelValor = "Recuperados";
                break;
            case "S": // SANOS
                cTop1 = "#2980b9"; cTop2 = "#8e44ad"; cTop3 = "#e91e63"; cRest = "#c0392b";
                labelValor = "Sanos";
                break;
        }
    }

    onCurrentFilterChanged: cargarDatos()
    Component.onCompleted: cargarDatos()

    Rectangle {
        anchors.fill: parent
        color: "#1e1e2e"
    }

    ColumnLayout {
        anchors.fill: parent
        // Márgenes grandes
        anchors.leftMargin: 80
        anchors.rightMargin: 80
        anchors.topMargin: 20
        anchors.bottomMargin: 20
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
                text: "Ranking Global: " + labelValor
                color: "white"
                font.pixelSize: 22
                font.bold: true
            }
            Item { Layout.fillWidth: true }
            Item { width: 80 }
        }

        // --- BOTONES DE FILTRO ---
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 10
            
            component FilterBtn: Button {
                property string filterCode: "I"
                property string emoji: "🤒"
                property string label: "Infectados"
                property color activeColor: "#ff5252"
                
                background: Rectangle {
                    color: root.currentFilter === filterCode ? activeColor : "#2f3542"
                    radius: 20
                    border.width: root.currentFilter === filterCode ? 2 : 0
                    border.color: "white"
                    Behavior on color { ColorAnimation { duration: 200 } }
                }
                contentItem: Row {
                    spacing: 5
                    anchors.centerIn: parent
                    Text { text: emoji; font.pixelSize: 16 }
                    Text { 
                        text: label; 
                        color: root.currentFilter === filterCode ? "white" : "#bdc3c7"
                        font.bold: true 
                    }
                }
                onClicked: root.currentFilter = filterCode
            }

            FilterBtn { filterCode: "I"; emoji: "🤒"; label: "Infectados"; activeColor: "#d32f2f" }
            FilterBtn { filterCode: "M"; emoji: "💀"; label: "Muertos"; activeColor: "#424242" }
            FilterBtn { filterCode: "R"; emoji: "💚"; label: "Recuperados"; activeColor: "#03a9f4" }
            FilterBtn { filterCode: "S"; emoji: "🛡️"; label: "Sanos"; activeColor: "#8e44ad" }
        }

        // --- ENCABEZADOS ---
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            Text { text: "#"; color: "#7f8c8d"; font.bold: true; width: 40; horizontalAlignment: Text.AlignHCenter }
            Text { text: "PAÍS"; color: "#7f8c8d"; font.bold: true; Layout.fillWidth: true }
            
            Text { text: root.labelValor.toUpperCase(); color: "white"; font.bold: true; width: 120; horizontalAlignment: Text.AlignRight }
            Text { text: "% RELATIVO"; color: "#aaa"; font.bold: true; width: 80; horizontalAlignment: Text.AlignRight }
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#444" }

        // --- LISTA ---
        ListView {
            id: listaPaises
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: root.rankingData
            spacing: 6

            ScrollBar.vertical: ScrollBar { active: true }

            delegate: Item {
                id: filaDelegate
                width: listaPaises.width
                height: 55

                readonly property var dato: modelData
                readonly property int posicion: index + 1
                readonly property real porcentaje: dato.ratio * 100
                
                property color rowColor: {
                    if (posicion === 1) return root.cTop1;
                    if (posicion === 2) return root.cTop2;
                    if (posicion === 3) return root.cTop3;
                    return root.cRest;
                }

                MouseArea {
                    id: mouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                }

                // Fondo de la fila
                Rectangle {
                    anchors.fill: parent
                    color: mouseArea.containsMouse ? "#40ffffff" : "#2f3542"
                    radius: 5
                    border.color: mouseArea.containsMouse ? "white" : "transparent"
                    border.width: 1

                    // Barra de progreso
                    Rectangle {
                        width: parent.width * (dato.ratio)
                        height: parent.height
                        color: filaDelegate.rowColor
                        opacity: mouseArea.containsMouse ? 0.6 : 0.3
                        radius: 5
                        
                        Behavior on width { NumberAnimation { duration: 600; easing.type: Easing.OutCubic } }
                        Behavior on color { ColorAnimation { duration: 400 } }
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 15
                    anchors.rightMargin: 15
                    spacing: 15

                    // 1. Posición
                    Rectangle {
                        width: 32; height: 32; radius: 16
                        color: filaDelegate.rowColor
                        Text { 
                            anchors.centerIn: parent
                            text: posicion
                            color: "white"
                            font.bold: true
                        }
                    }

                    // 2. Nombre
                    Column {
                        Layout.fillWidth: true
                        Text { 
                            text: dato.nombre
                            color: "white"
                            font.pixelSize: 16
                            font.bold: true
                            elide: Text.ElideRight
                            width: parent.width
                        }
                        Text { 
                            text: "Pob: " + Number(dato.poblacion).toLocaleString(Qt.locale(), 'f', 0)
                            color: "#aaa"; font.pixelSize: 11
                        }
                    }

                    // 3. Valor Principal
                    Text { 
                        text: Number(dato.valor).toLocaleString(Qt.locale(), 'f', 0)
                        color: filaDelegate.rowColor
                        font.pixelSize: 18
                        font.bold: true
                        Layout.preferredWidth: 120
                        horizontalAlignment: Text.AlignRight
                        
                        // CORRECCIÓN: Eliminado Behavior on text { FadeAnimation {} }
                        // QML no soporta animación directa de texto de esa forma.
                    }

                    // 4. Porcentaje
                    Text { 
                        text: porcentaje.toFixed(1) + "%"
                        color: "#ddd"
                        font.pixelSize: 14
                        font.bold: true
                        Layout.preferredWidth: 80
                        horizontalAlignment: Text.AlignRight
                    }
                }
            }
        }
    }
}
