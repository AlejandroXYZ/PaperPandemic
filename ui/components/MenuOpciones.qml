import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 6.3 // IMPORTANTE: Para abrir el gestor de archivos nativo

Drawer {
    id: rootDrawer
    width: 320 // Aumentamos un poco el ancho para evitar cortes en Linux/Gnome
    modal: false
    dim: false
    closePolicy: Popup.NoAutoClose
    background: Rectangle { color: "#1e1e2e" }
    
    // Propiedad para evitar que los elementos se salgan visualmente
    clip: true 

    property int vistaActual: 0 
    property var themeManager: null
    
    onOpened: if(backend) backend.pausar_simulacion()

    // --- COMPONENTE DE DIÁLOGO NATIVO ---
    FileDialog {
        id: fileDialog
        title: "Exportar Datos de la Simulación"
        nameFilters: ["Archivos CSV (*.csv)", "Todos los archivos (*)"]
        // Por defecto sugiere un nombre, pero deja al usuario cambiarlo y elegir carpeta
        currentFile: "Reporte_Pandemia_" + Qt.formatDateTime(new Date(), "yyyy-MM-dd") + ".csv"
        fileMode: FileDialog.SaveFile
        
        onAccepted: {
            // Pasamos la ruta elegida (selectedFile) al backend
            if(backend) backend.exportar_datos_excel(selectedFile)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        // CABECERA
        Text {
            text: "Paper-Pandemic"
            color: "#bdc3c7"
            font.bold: true
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
        }
        
        Rectangle { 
            Layout.fillWidth: true; height: 2; color: "#ff5252" 
        }

        // CONTENIDO CAMBIANTE
        StackLayout {
            id: stackVistas
            currentIndex: rootDrawer.vistaActual
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            // FIX DE DESBORDAMIENTO:
            // Aseguramos que el StackLayout respete los márgenes del padre
            clip: true 

            // -----------------------------------------------------
            // ÍNDICE 0: MENÚ PRINCIPAL
            // -----------------------------------------------------
            ColumnLayout {
                spacing: 15
                // Layout.fillWidth asegura que los hijos se estiren al ancho disponible
                Layout.fillWidth: true 

                Text { text: "Menú Principal"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }

                Button {
                    Layout.fillWidth: true; height: 50
                    background: Rectangle { color: "#3a3f55"; radius: 8 }
                    contentItem: Text { text: "🔧 Configuración"; color: "white"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: rootDrawer.vistaActual = 1
                }

                Button {
                    Layout.fillWidth: true; height: 50
                    background: Rectangle { color: "#3a3f55"; radius: 8 }
                    contentItem: Text { text: "⚙️ Parámetros"; color: "white"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: rootDrawer.vistaActual = 2
                }

                Button {
                    Layout.fillWidth: true; height: 50
                    background: Rectangle { color: "#3a3f55"; radius: 8 }
                    contentItem: Text { text: "📊 Estadísticas"; color: "white"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: rootDrawer.vistaActual = 3
                }

                Item { Layout.fillHeight: true }

                Text { text: "Creado por Alejandro Moncada"; font.pixelSize: 12; font.bold: true; color: "white"; Layout.alignment: Qt.AlignHCenter}
            }

            // -----------------------------------------------------
            // ÍNDICE 1: CONFIGURACIÓN (Con Exportar Mejorado)
            // -----------------------------------------------------
            ColumnLayout {
                spacing: 20
                Layout.fillWidth: true

                Text { text: "Configuración"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }
                

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    Text { text: "🎨 Tema Visual"; color: "#bdc3c7"; font.bold: true }
                    
                    ComboBox {
                        id: comboTema
                        Layout.fillWidth: true
                        // Obtenemos la lista del ThemeManager
                        model: rootDrawer.themeManager ? rootDrawer.themeManager.themeNames : []
                        
                        // Seleccionar el actual al inicio
                        Component.onCompleted: currentIndex = find("Default (Dark)")

                        delegate: ItemDelegate {
                            width: comboTema.width
                            contentItem: Text { text: modelData; color: "white"; font.pixelSize: 14 }
                            background: Rectangle { color: hovered ? "#3a3f55" : "#1e1e2e" }
                        }
                        contentItem: Text { 
                            text: comboTema.displayText; color: "white"; leftPadding: 10; verticalAlignment: Text.AlignVCenter 
                        }
                        background: Rectangle { color: "#2f3542"; radius: 5; border.color: "#555" }

                        onActivated: {
                            if(rootDrawer.themeManager) {
                                // 1. Cambiar colores de la UI (QML)
                                rootDrawer.themeManager.setTheme(currentText)
                                
                                // 2. Cambiar lógica de colores del Mapa (Python)
                                if(backend) {
                                    var nuevaPaleta = rootDrawer.themeManager.currentGradient
                                    backend.cambiar_tema_mapa(nuevaPaleta)
                                }
                            }
                        }
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: "#444" }




                // 1. NOMBRE VIRUS
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    Text { text: "🏷️ Nombre del Virus"; color: "#bdc3c7"; font.bold: true }
                    TextField {
                        Layout.fillWidth: true
                        placeholderText: "Ej: Paper-20"
                        text: backend ? backend.config.NOMBRE_VIRUS : ""
                        color: "white"
                        background: Rectangle { color: "#2f3542"; radius: 5; border.color: parent.activeFocus ? "#00cec9" : "#555" }
                        onTextEdited: if(backend) backend.config.NOMBRE_VIRUS = text
                    }
                }

                // 2. PAÍS INICIO
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    Text { text: "📍 Zona Cero (Origen)"; color: "#bdc3c7"; font.bold: true }
                    ComboBox {
                        id: comboPais
                        Layout.fillWidth: true
                        model: backend ? backend.listaNombresPaises : []
                        Component.onCompleted: {
                            if(backend) {
                                var idx = find(backend.config.PAIS_INICIO)
                                if (idx !== -1) currentIndex = idx
                            }
                        }
                        delegate: ItemDelegate {
                            width: comboPais.width
                            contentItem: Text { text: modelData; color: "white"; font.pixelSize: 14 }
                            background: Rectangle { color: hovered ? "#3a3f55" : "#1e1e2e" }
                        }
                        contentItem: Text { 
                            text: comboPais.displayText; color: "white"; leftPadding: 10; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight 
                        }
                        background: Rectangle { color: "#2f3542"; radius: 5; border.color: "#555" }
                        onActivated: if(backend) backend.config.PAIS_INICIO = currentText
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: "#444" }

                // 4. EXPORTAR DATOS (AHORA ABRE DIÁLOGO)
                Button {
                    Layout.fillWidth: true; height: 50
                    background: Rectangle { color: "#27ae60"; radius: 8 }
                    contentItem: RowLayout {
                        anchors.centerIn: parent
                        Text { text: "💾"; font.pixelSize: 20 }
                        Text { text: "Exportar (.csv)"; color: "white"; font.bold: true }
                    }
                    // AQUÍ ESTÁ EL CAMBIO: Abrimos el diálogo, no llamamos al backend directo
                    onClicked: fileDialog.open()
                }

                Item { Layout.fillHeight: true }
                
                Button {
                    Layout.fillWidth: true; flat: true
                    contentItem: Text { 
                        text: "⬅ Volver y Aplicar"; // Cambié el texto para que sea obvio
                        color: "#ff5252"; 
                        font.bold: true; 
                        horizontalAlignment: Text.AlignHCenter 
                    }
                    onClicked: {
                        // 1. REINICIAMOS LA SIMULACIÓN
                        if(backend) backend.reiniciar_simulacion()
                        
                        // 2. VOLVEMOS AL MENÚ PRINCIPAL
                        rootDrawer.vistaActual = 0
                        
                        // Opcional: Cerrar el menú automáticamente
                        // rootDrawer.close() 
                    }
                }
            }

            // -----------------------------------------------------
            // ÍNDICE 2: PARÁMETROS
            // -----------------------------------------------------
            ScrollView {
                clip: true // Evita que el scroll se salga
                Layout.fillWidth: true 
                Layout.fillHeight: true

                ColumnLayout {
                    width: parent.width // Forzamos ancho del contenido al del padre
                    spacing: 20

                    Text { text: "Ajuste de Variables"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }

                    SliderControl {
                        titulo: "⏩ Velocidad"
                        valorInicial: 0.5; maximo: 2.0
                        onValorCambiado: (val) => { if(backend) backend.cambiar_velocidad(val) }
                    }
                    
                    SliderControl {
                        titulo: "Tasa Contagio (β)"
                        valorInicial: backend ? backend.config.beta : 0.5; maximo: 1.0
                        onValorCambiado: (val) => { if(backend) backend.config.beta = val }
                    }

                    SliderControl {
                        titulo: "Recuperación (γ)"
                        valorInicial: backend ? backend.config.gamma : 0.1; maximo: 0.5
                        onValorCambiado: (val) => { if(backend) backend.config.gamma = val }
                    }

                    SliderControl {
                        titulo: "Mortalidad (μ)"
                        valorInicial: backend ? backend.config.mu : 0.01; maximo: 0.1
                        onValorCambiado: (val) => { if(backend) backend.config.mu = val }
                    }

                    SliderControl {
                        titulo: "Prob. Frontera"
                        valorInicial: backend ? backend.config.p_frontera : 1.0; maximo: 1.0
                        onValorCambiado: (val) => { if(backend) backend.config.p_frontera = val }
                    }

                    Item { Layout.fillHeight: true; height: 20 }

                    Button {
                        Layout.fillWidth: true; height: 50
                        background: Rectangle { color: "#e74c3c"; radius: 8 }
                        contentItem: Text { text: "⚠️ APLICAR Y REINICIAR"; color: "white"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 14 }
                        onClicked: if(backend) backend.reiniciar_simulacion()
                    }

                    Button {
                        Layout.fillWidth: true; flat: true
                        contentItem: Text { text: "⬅ Volver"; color: "#b2bec3"; horizontalAlignment: Text.AlignHCenter }
                        onClicked: rootDrawer.vistaActual = 0
                    }
                }
            }

            // -----------------------------------------------------
            // ÍNDICE 3: ESTADÍSTICAS
            // -----------------------------------------------------
            ColumnLayout {
                spacing: 15
                Layout.fillWidth: true
                Text { text: "Estadísticas"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }
                
                Item { Layout.fillHeight: true; height: 20 }

                Button {
                    Layout.fillWidth: true; height: 60
                    background: Rectangle { color: "#e67e22"; radius: 8 }
                    contentItem: RowLayout {
                        anchors.centerIn: parent
                        Text { text: "🏆"; font.pixelSize: 24 }
                        Text { text: "Ranking Global"; color: "white"; font.bold: true; font.pixelSize: 16 }
                    }
                    onClicked: {
                        if(backend) backend.pausar_simulacion()
                        mainWindow.vistaActual = "ranking"
                        rootDrawer.close()
                    }
                }

                Button {
                    Layout.fillWidth: true; height: 60
                    background: Rectangle { color: "#2ecc71"; radius: 8 }
                    contentItem: RowLayout {
                        anchors.centerIn: parent
                        Text { text: "📈"; font.pixelSize: 24 }
                        Text { text: "Curva Histórica"; color: "white"; font.bold: true; font.pixelSize: 16 }
                    }
                    onClicked: {
                        if(backend) backend.pausar_simulacion()
                        mainWindow.vistaActual = "grafico"
                        rootDrawer.close()
                    }
                }

                Item { Layout.fillHeight: true }
                
                Button {
                    Layout.fillWidth: true; flat: true
                    contentItem: Text { text: "⬅ Volver"; color: "#ff5252"; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                    onClicked: rootDrawer.vistaActual = 0
                }
            }
        }
    }

    // COMPONENTE SLIDER REUTILIZABLE
    component SliderControl : ColumnLayout {
        property string titulo: ""
        property real valorInicial: 0
        property real maximo: 1.0
        signal valorCambiado(real val)

        Layout.fillWidth: true
        spacing: 5
        RowLayout {
            Layout.fillWidth: true
            Text { text: titulo; color: "#bdc3c7"; font.bold: true; Layout.fillWidth: true }
            Text { text: slider.value.toFixed(3); color: "#00cec9"; font.bold: true }
        }
        Slider {
            id: slider
            Layout.fillWidth: true
            from: 0.0; to: maximo; value: valorInicial; stepSize: 0.001
            onMoved: parent.valorCambiado(value) 
        }
    }
}
