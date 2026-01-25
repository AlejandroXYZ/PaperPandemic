import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ToolBar {
    id: root
    height: 60
    background: Rectangle { color: "#1e1e2e" }

    // ========================================================
    // PROPIEDADES 
    // ========================================================
    property int dia: 1
    property int paisesInfectados: 1
    property string noticiaActual: "Se reporta una misteriosa enfermedad respiratoria."

    property double sanos: 7800000000 
    property double infectados: 1
    property double recuperados: 0
    property double muertos: 0

    // ========================================================
    // COMPONENTE DATO CORREGIDO (Sin conflictos de anclaje)
    // ========================================================
    component DatoSird: Item {
        id: datoControl
        property string icono: ""
        property string valor: ""
        property color colorAcento: "white"
        property string tooltipText: "" 

        // El tamaño del Item se ajusta automáticamente al tamaño del texto
        implicitWidth: contentRow.implicitWidth
        implicitHeight: contentRow.implicitHeight

        // 1. La fila que acomoda el icono y el texto
        Row {
            id: contentRow
            spacing: 5
            anchors.verticalCenter: parent.verticalCenter

            Text { text: datoControl.icono; color: datoControl.colorAcento; font.pixelSize: 18; font.bold: true }
            Text { text: datoControl.valor; color: "white"; font.pixelSize: 16; font.bold: true }
        }

        // 2. El área táctil que cubre TODO el componente, independiente de la fila
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true

            ToolTip {
                id: infoTooltip
                visible: mouseArea.containsMouse
                text: datoControl.tooltipText
                delay: 150
                x: mouseArea.mouseX
                y: mouseArea.mouseY - height - 10 

                background: Rectangle {
                    color: "#2f3542"
                    radius: 4
                    border.color: "#747d8c"
                }
                contentItem: Text {
                    text: infoTooltip.text
                    color: "white"
                    font.pixelSize: 12
                }
            }
        }
    }

    // ========================================================
    // DISTRIBUCIÓN DE LA BARRA
    // ========================================================
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 10
        spacing: 20

        Row {
            Layout.alignment: Qt.AlignVCenter
            spacing: 25

            DatoSird { 
                icono: "📅 Día:"; 
                valor: root.dia; 
                colorAcento: "white"
                tooltipText: "Días transcurridos desde el paciente cero"
            }
            DatoSird { 
                icono: "🧍"; 
                valor: Number(root.sanos).toLocaleString(Qt.locale(), 'f', 0); 
                colorAcento: "#DCE775"
                tooltipText: "Población Sana (Susceptible)"
            }
            DatoSird { 
                icono: "🤒"; 
                valor: Number(root.infectados).toLocaleString(Qt.locale(), 'f', 0); 
                colorAcento: "#ffb8b8"
                tooltipText: "Personas Infectadas actualmente"
            }
            DatoSird { 
                icono: "💚"; 
                valor: Number(root.recuperados).toLocaleString(Qt.locale(), 'f', 0); 
                colorAcento: "#4fc3f7"
                tooltipText: "Personas Recuperadas (Inmunes)"
            }
            DatoSird { 
                icono: "💀"; 
                valor: Number(root.muertos).toLocaleString(Qt.locale(), 'f', 0); 
                colorAcento: "#747d8c"
                tooltipText: "Muertes confirmadas"
            }
            DatoSird { 
                icono: "🌍"; 
                valor: root.paisesInfectados + "/250"; 
                colorAcento: "#ffb74d" 
                tooltipText: "Países con al menos un infectado"
            }
        }

        Item { Layout.fillWidth: true }

        // --- SECCIÓN DE NOTICIAS ---
        Rectangle {
            Layout.preferredWidth: 350
            Layout.preferredHeight: 40
            Layout.alignment: Qt.AlignVCenter
            color: "#2f3542"
            radius: 5
            border.color: "#747d8c"
            clip: true 

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Rectangle {
                    Layout.preferredWidth: 80
                    Layout.preferredHeight: 20
                    color: "#ff3f34"
                    radius: 3
                    Text { 
                        anchors.centerIn: parent; text: "NOTICIA"; 
                        color: "white"; font.pixelSize: 10; font.bold: true 
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: root.noticiaActual
                    color: "white"
                    font.pixelSize: 13
                    font.italic: true
                    elide: Text.ElideRight 
                }
            }
        }
    }
}
