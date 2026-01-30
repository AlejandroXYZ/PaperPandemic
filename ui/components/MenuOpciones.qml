import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Drawer {
    id: rootDrawer
    width: 300
    modal: false
    dim: false
    closePolicy: Popup.NoAutoClose
    background: Rectangle { color: "#1e1e2e" }
    
    // Control de navegación interna: 0=Menu, 1=Config, 2=Params, 3=Stats
    property int vistaActual: 0 

    // Al abrir el menú, pausamos para ahorrar recursos
    onOpened: if(backend) backend.pausar_simulacion()

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

            // -----------------------------------------------------
            // ÍNDICE 0: MENÚ PRINCIPAL
            // -----------------------------------------------------
            ColumnLayout {
                spacing: 15
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
            }

            // -----------------------------------------------------
            // ÍNDICE 1: CONFIGURACIÓN
            // -----------------------------------------------------
            ColumnLayout {
                Text { text: "Configuración"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }
                
                Text { 
                    text: "Próximamente...\nAquí podrás cambiar el idioma,\ntemas de color, etc." 
                    color: "#7f8c8d"; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true 
                }
                
                Item { Layout.fillHeight: true }
                
                Button {
                    Layout.fillWidth: true; flat: true
                    contentItem: Text { text: "⬅ Volver"; color: "#ff5252"; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                    onClicked: rootDrawer.vistaActual = 0
                }
            }

            // -----------------------------------------------------
            // ÍNDICE 2: PARÁMETROS (SLIDERS)
            // -----------------------------------------------------
            ScrollView {
                clip: true
                ColumnLayout {
                    width: parent.width
                    spacing: 20

                    Text { text: "Ajuste de Variables"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }

                    SliderControl {
                        titulo: "⏩ Velocidad Simulación"
                        valorInicial: 0.5; maximo: 2.0
                        onValorCambiado: (val) => { if(backend) backend.cambiar_velocidad(val) }
                    }
                    
                    SliderControl {
                        titulo: "Tasa de Contagio (β)"
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
                        contentItem: Text { text: "⚠️ APLICAR Y REINICIAR"; color: "white"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        onClicked: {
                            if(backend) backend.reiniciar_simulacion()
                            // Nos quedamos aquí para ver el cambio
                        }
                    }

                    Button {
                        Layout.fillWidth: true; flat: true
                        contentItem: Text { text: "⬅ Volver al Menú"; color: "#b2bec3"; horizontalAlignment: Text.AlignHCenter }
                        onClicked: rootDrawer.vistaActual = 0
                    }
                }
            }

            // -----------------------------------------------------
            // ÍNDICE 3: ESTADÍSTICAS
            // -----------------------------------------------------
            ColumnLayout {
                Text { text: "Estadísticas"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }
                
                Item { Layout.fillHeight: true; height: 20 }

                Button {
                    Layout.fillWidth: true; height: 60
                    background: Rectangle { 
                        color: "#e67e22" // Naranja (Diferente al verde de la gráfica)
                        radius: 8 
                    }
                    contentItem: RowLayout {
                        anchors.centerIn: parent
                        Text { text: "🏆"; font.pixelSize: 24 }
                        Text { text: "Ranking de Países"; color: "white"; font.bold: true; font.pixelSize: 16 }
                    }
                    
                    onClicked: {
                        if(backend) backend.pausar_simulacion()
                        mainWindow.vistaActual = "ranking" // Cambiamos a la nueva vista
                        rootDrawer.close()
                    }
                }

                // BOTÓN: VER CURVA HISTÓRICA
                Button {
                    Layout.fillWidth: true; height: 60
                    background: Rectangle { 
                        color: "#2ecc71" 
                        radius: 8 
                    }
                    contentItem: RowLayout {
                        anchors.centerIn: parent
                        Text { text: "📈"; font.pixelSize: 24 }
                        Text { text: "Ver Curva Histórica"; color: "white"; font.bold: true; font.pixelSize: 16 }
                    }
                    
                    onClicked: {
                        if(backend) backend.pausar_simulacion()
                        
                        // Cambiamos la vista principal en main.qml
                        mainWindow.vistaActual = "grafico"
                        
                        // Cerramos el menú
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
            onMoved: parent.valorCambiado(value) // Actualización en tiempo real
        }
    }
}
