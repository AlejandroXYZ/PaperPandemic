import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Drawer {
    id: rootDrawer
    width: 300
    modal: false; dim: false; closePolicy: Popup.NoAutoClose
    background: Rectangle { color: "#1e1e2e" }
    
    property bool editandoConfig: false

    onOpened: if(backend) backend.pausar_simulacion()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        Text {
            text: rootDrawer.editandoConfig ? "Configurar" : "Opciones SIRD"
            color: "white"
            font.bold: true
            font.pixelSize: 22
            Layout.alignment: Qt.AlignHCenter
        }
        
        Rectangle { Layout.fillWidth: true; height: 1; color: "#444" }

        // VISTA PRINCIPAL
        ColumnLayout {
            visible: !rootDrawer.editandoConfig
            Layout.fillWidth: true
            
            Button {
                Layout.fillWidth: true; height: 50
                background: Rectangle { color: "#3a3f55"; radius: 8 }
                contentItem: Text { text: "⚙️ Parámetros"; color: "white"; font.pixelSize: 16; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: rootDrawer.editandoConfig = true
            }
        }

        // VISTA SLIDERS
        ScrollView {
            visible: rootDrawer.editandoConfig
            Layout.fillWidth: true; Layout.fillHeight: true; clip: true

            ColumnLayout {
                width: parent.width; spacing: 20

                // === SOLUCIÓN: Usar backend.config ===
                // Verifica que backend y config existan antes de pintar
                
                SliderControl {
                    titulo: "Tasa de Contagio (β)"
                    // Usamos backend.config
                    valorInicial: backend ? backend.config.beta : 0.5
                    maximo: 1.0
                    onValorCambiado: (val) => { if(backend) backend.config.beta = val }
                }

                SliderControl {
                    titulo: "Recuperación (γ)"
                    valorInicial: backend ? backend.config.gamma : 0.1
                    maximo: 0.5
                    onValorCambiado: (val) => { if(backend) backend.config.gamma = val }
                }

                SliderControl {
                    titulo: "Mortalidad (μ)"
                    valorInicial: backend ? backend.config.mu : 0.01
                    maximo: 0.1
                    onValorCambiado: (val) => { if(backend) backend.config.mu = val }
                }

                SliderControl {
                    titulo: "Prob. Frontera"
                    valorInicial: backend ? backend.config.p_frontera : 1.0
                    maximo: 1.0
                    onValorCambiado: (val) => { if(backend) backend.config.p_frontera = val }
                }

                Item { Layout.fillHeight: true; height: 20 }

                Button {
                    Layout.fillWidth: true; height: 50
                    background: Rectangle { color: "#e74c3c"; radius: 8 }
                    contentItem: Text { text: "⚠️ APLICAR Y REINICIAR"; color: "white"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: {
                        if(backend) backend.reiniciar_simulacion()
                        rootDrawer.editandoConfig = false
                    }
                }

                Button {
                    Layout.fillWidth: true; flat: true
                    contentItem: Text { text: "Volver"; color: "#b2bec3"; horizontalAlignment: Text.AlignHCenter }
                    onClicked: rootDrawer.editandoConfig = false
                }
            }
        }
    }

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
            onPressedChanged: { if (!pressed) parent.valorCambiado(value) }
        }
    }
}
