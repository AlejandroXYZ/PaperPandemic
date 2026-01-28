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
        onMenuClicked: opcionesDrawer.opened ? opcionesDrawer.close() : opcionesDrawer.open()
        
        // --- CONEXIÓN AL BACKEND ---
        // Cuando se hace clic en Play/Pause, llamamos a la función de Python
        onPlayPauseClicked: (isPlaying) => { 
            console.log("QML enviando señal de Play/Pause..."); // Log en QML
            backend.toggle_simulacion(isPlaying); // Llamada a Python
        }
        
        onResetClicked: { 
            console.log("QML enviando señal de Reinicio...");
            backend.reiniciar(); 
        }
    }

    // --- NUEVO: 2. BARRA INFERIOR DE ESTADO Y NOTICIAS ---
   footer: BarraInferior {
        id: barraInf
        
        dia: backend ? backend.dia : "1"
        sanos: backend ? backend.sanos : 0
        infectados: backend ? backend.infectados : 0
        recuperados: backend ? backend.recuperados : 0
        muertos: backend ? backend.muertos : 0
        paisesInfectados: backend ? backend.paisesInfectados : 0
        noticiaActual: backend ? backend.noticia : "Cargando..."
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
