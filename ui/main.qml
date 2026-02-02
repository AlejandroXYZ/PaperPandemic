import QtQuick
import QtQuick.Controls
import components
import themes

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1200
    height: 720
    title: "Simulador SIRD - Dashboard"
    color: theme.appBackground

    ThemeManager {
            id: theme
    }
    

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
        themeManager: theme
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
            sourceComponent: {
                        if (mainWindow.vistaActual === "grafico") return compGrafico;
                        if (mainWindow.vistaActual === "ranking") return compRanking;
                        if (mainWindow.vistaActual === "noticias") return compNoticias;
                        return compMapa;
            }
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

    Component {
        id: compRanking
        VistaRanking {
            anchors.fill: parent
            onVolverClicked: mainWindow.vistaActual = "mapa"
        }
    }

    Component {
            id: compNoticias
            VistaNoticias { anchors.fill: parent }
    }

    // ... (después de Component id: compRanking) ...
    
    GameOverModal {
        id: gameOverPopup
    
        onReiniciarClicked: {
            gameOverPopup.visible = false
            if(backend) backend.reiniciar()
        }
    
        onVerGraficaClicked: {
            mainWindow.vistaActual = "grafico"
        }
    
        onVerRankingClicked: {
            mainWindow.vistaActual = "ranking"
        }
    }
    
    // CONEXIÓN SEÑAL BACKEND -> MODAL
    Connections {
        target: backend
        function onGameOver(datos) {
            gameOverPopup.abrir(datos)
        }
    }

    Shortcut {
        sequence: "k"  // La tecla que activa el truco
        onActivated: {
            console.log("😈 Tecla K detectada -> Activando Cheat...")
            if(backend) backend.activar_cheat_fin()
        }
    }
}
