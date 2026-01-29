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

    // Propiedad de estado: controla si vemos el "mapa" o el "grafico"
    property string vistaActual: "mapa"

    // 1. BARRA SUPERIOR
    header: BarraSuperior {
        visible: mainWindow.vistaActual === "mapa"
        onMenuClicked: opcionesDrawer.opened ? opcionesDrawer.close() : opcionesDrawer.open()

        // Conexión al Backend
        onPlayPauseClicked: (isPlaying) => {
            if(backend) backend.toggle_simulacion(isPlaying);
        }

        onResetClicked: {
            if(backend) backend.reiniciar();
        }
    }

    // 2. BARRA INFERIOR
    footer: BarraInferior {
        id: barraInf
        visible: mainWindow.vistaActual === "mapa"
        
        // Data Bindings seguros
        dia: backend ? backend.dia : "1"
        primerPaisNombre: backend ? backend.primerPais : "..."
        
        sanos: backend ? backend.sanos : 0
        infectados: backend ? backend.infectados : 0
        recuperados: backend ? backend.recuperados : 0
        muertos: backend ? backend.muertos : 0
        paisesInfectados: backend ? backend.paisesInfectados : 0
        noticiaActual: backend ? backend.noticia : "Cargando..."
    }

    // 3. MENÚ LATERAL (Drawer)
    MenuOpciones {
        id: opcionesDrawer
        y: header.height
        height: parent.height - header.height - footer.height
    }

    // 4. CONTENEDOR PRINCIPAL (Loader Dinámico)
    Item {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        
        // Efecto visual: El contenido se encoge cuando sale el menú
        anchors.leftMargin: opcionesDrawer.position * opcionesDrawer.width
        scale: vistaActual === "mapa" ? (1.0 - (opcionesDrawer.position * 0.15)) : 1.0

        // EL CEREBRO DE LA OPTIMIZACIÓN:
        // Carga y destruye componentes según se necesiten
        Loader {
            id: mainLoader
            anchors.fill: parent
            sourceComponent: mainWindow.vistaActual === "mapa" ? compMapa : compGrafico
        }
    }

    // --- COMPONENTES DINÁMICOS ---

    // A) El Mapa (Se destruye al ver gráficas para ahorrar CPU)
    Component {
        id: compMapa
        Mapa {
            anchors.fill: parent
        }
    }

    // B) El Gráfico Histórico
    Component {
        id: compGrafico
        VistaGrafica {
            anchors.fill: parent
            // Al volver, restauramos la vista del mapa
            onVolverClicked: {
                mainWindow.vistaActual = "mapa"
            }
        }
    }
}
