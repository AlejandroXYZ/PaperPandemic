import QtQuick 2.15
import QtCore

Item {
    id: root
    visible: false

    // --- PROPIEDADES GENERALES ---
    property color appBackground: "#121212"
    property color panelBackground: "#1e1e2e"
    property color textColor: "#ffffff"
    property color accentColor: "#ff5252"
    
    // --- PROPIEDADES DEL MAPA ---
    property color mapBackground: "#1e1e2e"
    property color mapStroke: "white"
    property var currentGradient: ["#A2B2F3", "#9C27B0", "#E91E63", "#D50000", "#640000"]

    // --- NUEVO: COLORES DE LA GRÁFICA DE PASTEL (S, I, R, M) ---
    property color pieS: "#DCE775" // Sanos
    property color pieI: "#ff5252" // Infectados
    property color pieR: "#4fc3f7" // Recuperados
    property color pieM: "#95a5a6" // Muertos

    property string currentThemeName: "Default (Dark)"

    Settings {
        id: themeSettings
        category: "Visuals"
        property alias themeName: root.currentThemeName
    }

    Component.onCompleted: setTheme(currentThemeName)
    onCurrentThemeNameChanged: setTheme(currentThemeName)

    // --- DEFINICIÓN DE TEMAS ---
    property var themes: {
        "Default (Dark)": {
            bg: "#121212", panel: "#1e1e2e", text: "#ffffff", accent: "#ff5252",
            mapBg: "#121212", stroke: "white",
            grad: ["#A2B2F3", "#9C27B0", "#E91E63", "#D50000", "#640000"],
            // Colores Estándar
            pS: "#DCE775", pI: "#ff5252", pR: "#4fc3f7", pM: "#95a5a6"
        },
        "Nuclear (Radioactive)": {
            bg: "#050f00", panel: "#0a1f00", text: "#00ff41", accent: "#39ff14",
            mapBg: "#000000", stroke: "#003300",
            grad: ["#0f2e0f", "#1b5e20", "#4caf50", "#c6ff00", "#ffffff"],
            // Todo en tonos verdes tóxicos
            pS: "#1b5e20", pI: "#c6ff00", pR: "#4caf50", pM: "#000000"
        },
        "Sangre (Apocalypse)": {
            bg: "#1a0505", panel: "#2b0909", text: "#ffcccc", accent: "#e74c3c",
            mapBg: "#000000", stroke: "#440000",
            grad: ["#2c2c2c", "#5c0000", "#b71c1c", "#ff5722", "#ffeb3b"],
            // Tonos rojos y carne
            pS: "#5c0000", pI: "#ff0000", pR: "#e67e22", pM: "#1a1a1a"
        },
        "Pergamino (Paper)": {
            bg: "#f3e5ab", panel: "#f5f5dc", text: "#3e2723", accent: "#795548",
            mapBg: "#d4c59a", stroke: "#5d4037",
            grad: ["#fff8e1", "#d7ccc8", "#8d6e63", "#4e342e", "#000000"],
            // Tonos tinta, sepia y papel
            pS: "#d7ccc8", pI: "#bf360c", pR: "#795548", pM: "#3e2723"
        },
        "Térmico (Predator)": {
            bg: "#000814", panel: "#001d3d", text: "#caf0f8", accent: "#00b4d8",
            mapBg: "#000010", stroke: "#003566",
            grad: ["#0000ff", "#00ffff", "#00ff00", "#ffff00", "#ff0000"],
            // Colores de cámara térmica
            pS: "#0000ff", pI: "#ffff00", pR: "#00ffff", pM: "#000055"
        },
        "Cyberpunk (Neon)": {
            bg: "#0b0014", panel: "#180029", text: "#e0aaff", accent: "#d000ff",
            mapBg: "#10001a", stroke: "#5a189a",
            grad: ["#240046", "#3c096c", "#7b2cbf", "#ff00ff", "#ffffff"],
            // Neones saturados
            pS: "#7b2cbf", pI: "#ff00ff", pR: "#00e5ff", pM: "#ffffff"
        }
    }

    function setTheme(name) {
        if (themes[name]) {
            var t = themes[name]
            appBackground = t.bg
            panelBackground = t.panel
            textColor = t.text
            accentColor = t.accent
            mapBackground = t.mapBg
            mapStroke = t.stroke
            currentGradient = t.grad
            
            // Asignamos colores del pastel
            pieS = t.pS
            pieI = t.pI
            pieR = t.pR
            pieM = t.pM
            
            currentThemeName = name
        }
    }
    
    property var themeNames: ["Default (Dark)", "Nuclear (Radioactive)", "Sangre (Apocalypse)", "Pergamino (Paper)", "Térmico (Predator)", "Cyberpunk (Neon)"]
}
