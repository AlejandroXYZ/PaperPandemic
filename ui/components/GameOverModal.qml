import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    anchors.fill: parent
    color: "#cc000000" // Fondo negro semitransparente (Bloquea clicks)
    visible: false
    z: 20000 // Por encima de TODO (incluso del PieChartPopup que tiene z:10000)

    // Propiedades de datos
    property string tituloFin: "Virus Erradicado"
    property string diaFin: "0"
    property double totalS: 0
    property double totalR: 0
    property double totalM: 0
    property double paisesInf: 0

    // Estado interno: "RESUMEN" o "STATS"
    property string estadoActual: "RESUMEN"

    signal reiniciarClicked()
    signal verGraficaClicked()
    signal verRankingClicked()

    // MouseArea gigante para atrapar clicks y que no pasen al mapa
    MouseArea { anchors.fill: parent }

    function abrir(datos) {
        tituloFin = datos.titulo
        diaFin = datos.dia
        totalS = datos.sanos
        totalR = datos.recuperados
        totalM = datos.muertos
        paisesInf = datos.paises_afectados
        estadoActual = "RESUMEN" // Siempre empezar en resumen
        root.visible = true
    }

    // CONTENEDOR CENTRAL
    Rectangle {
        width: 450
        height: estadoActual === "RESUMEN" ? 500 : 350
        anchors.centerIn: parent
        color: "#1e1e2e"
        radius: 15
        border.color: "#444"
        border.width: 1

        // Animación suave al cambiar de altura
        Behavior on height { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 30
            spacing: 20

            // ------------------------------------------------
            // VISTA 1: RESUMEN DE PARTIDA
            // ------------------------------------------------
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: root.estadoActual === "RESUMEN"

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 15

                    // Icono y Título
                    Text { 
                        text: "🏁"
                        font.pixelSize: 50
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text { 
                        text: root.tituloFin
                        color: "white"
                        font.bold: true
                        font.pixelSize: 28
                        Layout.alignment: Qt.AlignHCenter
                    }
                    Text { 
                        text: "La simulación ha terminado."
                        color: "#aaa"
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: "#444"; Layout.margins: 10 }

                    // Grid de Datos
                    GridLayout {
                        columns: 2
                        Layout.alignment: Qt.AlignHCenter
                        rowSpacing: 15
                        columnSpacing: 30

                        Text { text: "📅 Duración:"; color: "#ccc"; font.bold: true }
                        Text { text: root.diaFin + " Días"; color: "white"; font.bold: true; horizontalAlignment: Text.AlignRight }

                        Text { text: "🌍 Países Afectados:"; color: "#ffb74d"; font.bold: true }
                        Text { text: root.paisesInf + "/250"; color: "white"; font.bold: true; horizontalAlignment: Text.AlignRight }

                        Text { text: "💀 Total Muertos:"; color: "#ff5252"; font.bold: true }
                        Text { text: Number(root.totalM).toLocaleString(Qt.locale(), 'f', 0); color: "white"; font.bold: true; horizontalAlignment: Text.AlignRight }

                        Text { text: "💚 Total Recuperados:"; color: "#4fc3f7"; font.bold: true }
                        Text { text: Number(root.totalR).toLocaleString(Qt.locale(), 'f', 0); color: "white"; font.bold: true; horizontalAlignment: Text.AlignRight }

                        Text { text: "🛡️ Sobrevivientes Sanos:"; color: "#DCE775"; font.bold: true }
                        Text { text: Number(root.totalS).toLocaleString(Qt.locale(), 'f', 0); color: "white"; font.bold: true; horizontalAlignment: Text.AlignRight }
                    }

                    Item { Layout.fillHeight: true }

                    // Botones Principales
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 15
                        
                        Button {
                            Layout.fillWidth: true; height: 50
                            background: Rectangle { color: "#e74c3c"; radius: 8 }
                            contentItem: Text { text: "⟲ REINICIAR"; color: "white"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                            onClicked: root.reiniciarClicked()
                        }
                        
                        Button {
                            Layout.fillWidth: true; height: 50
                            background: Rectangle { color: "#3a3f55"; radius: 8 }
                            contentItem: Text { text: "📊 ESTADÍSTICAS"; color: "white"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                            onClicked: root.estadoActual = "STATS" // Cambia la vista
                        }
                    }
                }
            }

            // ------------------------------------------------
            // VISTA 2: MENÚ DE ESTADÍSTICAS (Transformada)
            // ------------------------------------------------
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: root.estadoActual === "STATS"

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 15

                    Text { 
                        text: "Análisis Post-Pandemia"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 22
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Item { Layout.fillHeight: true }

                    // Botón Gráfica
                    Button {
                        Layout.fillWidth: true; height: 55
                        background: Rectangle { color: "#2ecc71"; radius: 8 }
                        contentItem: Row {
                            anchors.centerIn: parent; spacing: 10
                            Text { text: "📈"; font.pixelSize: 20 }
                            Text { text: "Ver Curva Histórica"; color: "white"; font.bold: true; font.pixelSize: 16 }
                        }
                        onClicked: { root.visible = false; root.verGraficaClicked() }
                    }

                    // Botón Ranking
                    Button {
                        Layout.fillWidth: true; height: 55
                        background: Rectangle { color: "#e67e22"; radius: 8 }
                        contentItem: Row {
                            anchors.centerIn: parent; spacing: 10
                            Text { text: "🏆"; font.pixelSize: 20 }
                            Text { text: "Ver Ranking Global"; color: "white"; font.bold: true; font.pixelSize: 16 }
                        }
                        onClicked: { root.visible = false; root.verRankingClicked() }
                    }

                    Item { Layout.fillHeight: true }

                    // Volver al resumen
                    Button {
                        Layout.fillWidth: true; flat: true
                        contentItem: Text { text: "⬅ Volver al Resumen"; color: "#aaa"; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                        onClicked: root.estadoActual = "RESUMEN"
                    }
                }
            }
        }
    }
}
