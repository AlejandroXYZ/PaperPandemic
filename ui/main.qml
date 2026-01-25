import QtQuick
import QtQuick.Controls
import components 

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1200 
    height: 720
    title: "Simulador SIRD - Dashboard"
    color: "#121212"

    // 1. BARRA SUPERIOR
    header: BarraSuperior {
        id: barraSup
        onMenuClicked: opcionesDrawer.opened ? opcionesDrawer.close() : opcionesDrawer.open()
        onPlayPauseClicked: (isPlaying) => { console.log("Simulación: " + (isPlaying ? "PLAY" : "PAUSE")) }
        onResetClicked: { console.log("Simulación REINICIADA") }
    }

    // --- NUEVO: 2. BARRA INFERIOR DE ESTADO Y NOTICIAS ---
    footer: BarraInferior {
        id: barraInf
        // Aquí podrás enlazar datos de Python después. Ej:
        // infectados: modeloPython.totalInfectados
    }

    // 3. VENTANA LATERAL (Menú)
    MenuOpciones {
        id: opcionesDrawer
        y: header.height 
        // --- AJUSTE AQUÍ: Restamos el header y el footer para que encaje perfecto ---
        height: parent.height - header.height - footer.height 
    }

    // 4. MAPA INTERACTIVO
    Item {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.leftMargin: opcionesDrawer.position * opcionesDrawer.width
        scale: 1.0 - (opcionesDrawer.position * 0.15)

        Mapa {
            anchors.fill: parent
        }
    }
}
