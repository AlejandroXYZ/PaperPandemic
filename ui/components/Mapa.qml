import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15

Item {
    id: mapRoot
    anchors.fill: parent
    clip: true

    // =========================================================
    // 1. VARIABLES DEL TOOLTIP MAESTRO (Globales)
    // =========================================================
    // Estas variables almacenan la info del país que se está tocando
    property string tooltipTexto: ""
    property bool tooltipVisible: false
    property real tooltipX: 0
    property real tooltipY: 0

    // =========================================================
    // 2. FUNCIONES
    // =========================================================
    function flyToCountry(clickX, clickY) {
        let targetScale = 5.0;
        let newX = (mapRoot.width / 2) - 500 - (clickX - 500) * targetScale;
        let newY = (mapRoot.height / 2) - 400 - (clickY - 400) * targetScale;
        mapContainer.scale = targetScale;
        mapContainer.x = newX;
        mapContainer.y = newY;
    }

    function setZoom(factor) {
        let newScale = mapContainer.scale * factor;
        mapContainer.scale = Math.max(0.5, Math.min(newScale, 20.0));
    }

    // =========================================================
    // 3. CONTENEDOR DEL MAPA
    // =========================================================
    Item {
        id: mapContainer
        width: 1010
        height: 660
        anchors.centerIn: parent
        scale: 0.8
        transformOrigin: Item.Center

        // Gestor de Arrastre (Más rápido que MouseArea para mover)
        DragHandler {
            id: mapDragHandler
            target: mapContainer
            acceptedButtons: Qt.LeftButton
        }

        // Gestor de Zoom con Rueda
        WheelHandler {
            id: mapWheelHandler
            target: mapContainer
            onWheel: (event) => {
                mapRoot.setZoom(event.angleDelta.y > 0 ? 1.15 : 0.85);
            }
        }

        // DIBUJADO DE LOS PAÍSES
        Repeater {
            // USAMOS TU NOMBRE ORIGINAL DEL MODELO
            model: mapa_modelo 

            Shape {
                id: countryShape
                // Usamos dimensiones fijas para que coincidan con el SVG
                width: 1010
                height: 660
                
                // Optimizamos la detección del mouse solo a la forma del país
                containsMode: Shape.FillContains

                ShapePath {
                    strokeWidth: 1 / mapContainer.scale // Mantiene el borde fino al hacer zoom
                    strokeColor: "#ffffff"
                    fillRule: ShapePath.WindingFill
                    
                    // Si el color viene vacío, usamos gris por seguridad
                    fillColor: (model.color_pais && model.color_pais !== "") ? model.color_pais : "#CFD8DC"
                    

                    PathSvg { path: model.path }
                }

                // DETECTOR DE MOUSE INDIVIDUAL
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    containmentMask: countryShape
                    cursorShape: Qt.PointingHandCursor

                    onDoubleClicked: (mouse) => mapRoot.flyToCountry(mouse.x, mouse.y)

                    // Cuando el mouse entra, actualizamos las variables globales
                    onEntered: {
                        // Llamamos a la función rápida de Python
                        mapRoot.tooltipTexto = mapa_modelo.get_datos_pais_html(model.codigo)
                        mapRoot.tooltipVisible = true
                        
                        // Calculamos la posición relativa a la ventana principal
                        var pos = mapToItem(mapRoot, mouseX, mouseY)
                        mapRoot.tooltipX = pos.x + 15
                        mapRoot.tooltipY = pos.y + 15
                    }

                    // Si mueves el mouse dentro del país, el tooltip te sigue
                    onPositionChanged: (mouse) => {
                        var pos = mapToItem(mapRoot, mouse.x, mouse.y)
                        mapRoot.tooltipX = pos.x + 15
                        mapRoot.tooltipY = pos.y + 15
                    }

                    onExited: {
                        mapRoot.tooltipVisible = false
                    }
                }
            }
        }
    }

    // =========================================================
    // 4. EL TOOLTIP MAESTRO (ÚNICO)
    // =========================================================
    // Está fuera del Repeater, por lo que solo se crea UNA vez.
    Rectangle {
        id: globalTooltip
        visible: mapRoot.tooltipVisible
        x: mapRoot.tooltipX
        y: mapRoot.tooltipY
        z: 9999 // Siempre encima de todo

        // El tamaño se adapta al texto
        width: infoText.contentWidth + 20
        height: infoText.contentHeight + 14
        
        color: "#2f3640" // Fondo oscuro
        radius: 4
        border.color: "white"
        border.width: 1

        Text {
            id: infoText
            anchors.centerIn: parent
            text: mapRoot.tooltipTexto
            color: "white"
            font.pixelSize: 13
            textFormat: Text.RichText // Permite usar <b> y <br>
        }
    }

    // =========================================================
    // 5. BOTONES DE ZOOM
    // =========================================================
    Column {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20
        spacing: 10

        RoundButton {
            width: 45; height: 45
            onClicked: mapRoot.setZoom(1.5)
            background: Rectangle {
                color: parent.pressed ? "#636e72" : "#2d3436"
                radius: width/2
                border.color: "#b2bec3"
            }
            contentItem: Text { text: "+"; color: "white"; font.pixelSize: 24; anchors.centerIn: parent }
        }

        RoundButton {
            width: 45; height: 45
            onClicked: mapRoot.setZoom(0.7)
            background: Rectangle {
                color: parent.pressed ? "#636e72" : "#2d3436"
                radius: width/2
                border.color: "#b2bec3"
            }
            contentItem: Text { text: "−"; color: "white"; font.pixelSize: 24; anchors.centerIn: parent }
        }
    }
}
