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
    property string dia: "1"
    property int paisesInfectados: 1
    property string noticiaActual: "Se reporta una misteriosa enfermedad respiratoria."

    property real sanos: 7800000000 
    property real infectados: 1
    property real recuperados: 0
    property real muertos: 0
    property string primerPaisNombre: "..."

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
            DatoSird { 
                icono: "☣️ Origen:"; 
                valor: root.primerPaisNombre; 
                colorAcento: "#ff5252" // Rojo alerta
                tooltipText: "País Paciente Cero"
            }
        }

        Item { Layout.fillWidth: true }

        // --- SECCIÓN DE NOTICIAS ---
        Rectangle {
            id: newsContainer
            Layout.fillWidth: true
            Layout.fillHeight: true
                
            // MÁRGENES: Para que el borde no toque los extremos de la pantalla
            Layout.topMargin: 10
            Layout.bottomMargin: 10
            Layout.rightMargin: 20 
                
            color: "#15ffffff" // Fondo blanco muy transparente (efecto cristal)
                
            // --- EL BORDE QUE PEDISTE ---
            border.color: "white"
            border.width: 1
            radius: 6 // Esquinas redondeadas para que se vea moderno
                
            clip: true // IMPORTANTE: Corta el texto que se sale
    
            Text {
                id: tickerText
                text: backend ? backend.noticia : "Esperando datos..."
                color: "#e0e0e0"
                font.pixelSize: 16
                font.bold: true
                font.family: "Courier New" 
                verticalAlignment: Text.AlignVCenter
                    
                x: parent.width 
                anchors.verticalCenter: parent.verticalCenter
    
                NumberAnimation on x {
                    from: parent.width 
                    to: -tickerText.width 
                    duration: 8000 
                    loops: Animation.Infinite
                    running: true
                }
                    
                onTextChanged: {
                    // Reinicio de animación
                }
            }
    
            // AREA CLICKEABLE CON EFECTO VISUAL
            MouseArea {
                id: newsMouse
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true // Para detectar cuando pasas el mouse
                    
                onClicked: {
                    if(backend) backend.pausar_simulacion()
                    mainWindow.vistaActual = "noticias"
                }
            }
                
            // EFECTO EXTRA: Iluminar el borde cuando pasas el mouse
            states: State {
                name: "hovered"
                when: newsMouse.containsMouse
                PropertyChanges { target: newsContainer; border.color: "#00cec9"; color: "#25ffffff" }
            }
            transitions: Transition {
                ColorAnimation { duration: 200 }
            }
        }
    }
}
