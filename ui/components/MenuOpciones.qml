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
    
    // 0: Menú Principal, 1: Config, 2: Parámetros, 3: Estadísticas
    property int vistaActual: 0 

    onOpened: if(backend) backend.pausar_simulacion()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        // =========================================================
        // 1. CABECERA FIJA (Siempre visible)
        // =========================================================
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

        // =========================================================
        // 2. CONTENIDO CAMBIANTE (StackLayout)
        // =========================================================
        StackLayout {
            id: stackVistas
            currentIndex: rootDrawer.vistaActual
            Layout.fillWidth: true
            Layout.fillHeight: true

            // -----------------------------------------------------
            // ÍNDICE 0: MENÚ PRINCIPAL (Botones de navegación)
            // -----------------------------------------------------
            ColumnLayout {
                spacing: 15

                Text { text: "Menú Principal"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }

                // Botón 1: Configuración (Placeholder)
                Button {
                    Layout.fillWidth: true; height: 50
                    background: Rectangle { color: "#3a3f55"; radius: 8 }
                    contentItem: Text { text: "🔧 Configuración"; color: "white"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: rootDrawer.vistaActual = 1 // Ir a Config
                }

                // Botón 2: Parámetros (El que funciona)
                Button {
                    Layout.fillWidth: true; height: 50
                    background: Rectangle { color: "#3a3f55"; radius: 8 }
                    contentItem: Text { text: "⚙️ Parámetros"; color: "white"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: rootDrawer.vistaActual = 2 // Ir a Sliders
                }

                // Botón 3: Estadísticas (Placeholder)
                Button {
                    Layout.fillWidth: true; height: 50
                    background: Rectangle { color: "#3a3f55"; radius: 8 }
                    contentItem: Text { text: "📊 Estadísticas"; color: "white"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: rootDrawer.vistaActual = 3 // Ir a Stats
                }

                Item { Layout.fillHeight: true } // Espaciador


                Text { text: "Creado por: Alejandro Moncada"; color: "white"; font.pixelSize: 12; Layout.alignment: Qt.AlignHCenter}
            }

            // -----------------------------------------------------
            // ÍNDICE 1: CONFIGURACIÓN (Futuro)
            // -----------------------------------------------------
            ColumnLayout {
                Text { text: "Configuración"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }
                
                Text { 
                    text: "Próximamente...\nAquí podrás cambiar el idioma,\ntemas de color, etc." 
                    color: "#7f8c8d"; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true 
                }
                
                Item { Layout.fillHeight: true }
                
                Button {
                    Layout.fillWidth: true
                    flat: true
                    contentItem: Text { text: "⬅ Volver"; color: "#ff5252"; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                    onClicked: rootDrawer.vistaActual = 0
                }
            }

            // -----------------------------------------------------
            // ÍNDICE 2: PARÁMETROS (Tus sliders)
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
                            // No volvemos al menú automáticamente, dejamos al usuario aquí
                        }
                    }

                    Button {
                        Layout.fillWidth: true
                        flat: true
                        contentItem: Text { text: "⬅ Volver al Menú"; color: "#b2bec3"; horizontalAlignment: Text.AlignHCenter }
                        onClicked: rootDrawer.vistaActual = 0
                    }
                }
            }

            // -----------------------------------------------------
            // ÍNDICE 3: ESTADÍSTICAS (Futuro)
            // -----------------------------------------------------
            ColumnLayout {
                Text { text: "Estadísticas"; color: "white"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }
                
                Text { 
                    text: "Próximamente...\nGráficas en tiempo real\ny curvas SIRD." 
                    color: "#7f8c8d"; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true 
                }
                
                Item { Layout.fillHeight: true }
                
                Button {
                    Layout.fillWidth: true
                    flat: true
                    contentItem: Text { text: "⬅ Volver"; color: "#ff5252"; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                    onClicked: rootDrawer.vistaActual = 0
                }
            }
        }
    }

    // COMPONENTE SLIDER (Reutilizado)
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
            onMoved: parent.valorCambiado(value) // Usamos onMoved para tiempo real
        }
    }
}
