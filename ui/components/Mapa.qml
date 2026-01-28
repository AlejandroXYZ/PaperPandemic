import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15

Item {
    id: mapRoot
    anchors.fill: parent
    clip: true

    // =========================================================
    // 1. TOOLTIP (Variables Globales)
    // =========================================================
    property string tooltipHtml: ""
    property bool isTooltipVisible: false
    property real tipX: 0
    property real tipY: 0

    // =========================================================
    // 2. LÓGICA DE ZOOM (Doble Clic con Animación)
    // =========================================================
    function flyToCountry(mapX, mapY) {
        let targetScale = 6.0
        
        // Calculamos dónde debe quedar el mapa
        let newX = (mapRoot.width / 2) - (mapX * targetScale)
        let newY = (mapRoot.height / 2) - (mapY * targetScale)

        // Preparamos la animación
        animScale.from = mapContainer.scale
        animScale.to = targetScale
        
        animX.from = mapContainer.x
        animX.to = newX
        
        animY.from = mapContainer.y
        animY.to = newY
        
        // ¡Arrancamos el vuelo suave!
        zoomAnim.restart()
    }

    // Animación SOLO para el doble clic o botones (no afecta la rueda)
    ParallelAnimation {
        id: zoomAnim
        NumberAnimation { id: animX; target: mapContainer; property: "x"; duration: 600; easing.type: Easing.OutCubic }
        NumberAnimation { id: animY; target: mapContainer; property: "y"; duration: 600; easing.type: Easing.OutCubic }
        NumberAnimation { id: animScale; target: mapContainer; property: "scale"; duration: 600; easing.type: Easing.OutCubic }
    }

    // Zoom manual (Botones) - Usa animación
    function setZoomManual(factor) {
        let newScale = mapContainer.scale * factor
        newScale = Math.max(0.5, Math.min(newScale, 30.0))
        
        // Hacemos zoom al centro de la pantalla
        let centerOffsetX = (mapRoot.width / 2 - mapContainer.x) / mapContainer.scale
        let centerOffsetY = (mapRoot.height / 2 - mapContainer.y) / mapContainer.scale
        
        let newX = (mapRoot.width / 2) - (centerOffsetX * newScale)
        let newY = (mapRoot.height / 2) - (centerOffsetY * newScale)

        animScale.from = mapContainer.scale
        animScale.to = newScale
        animX.from = mapContainer.x
        animX.to = newX
        animY.from = mapContainer.y
        animY.to = newY
        zoomAnim.restart()
    }

    // =========================================================
    // 3. CONTENEDOR DEL MAPA
    // =========================================================
    Item {
        id: mapContainer
        width: 1010
        height: 660
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        scale: 0.9
        transformOrigin: Item.TopLeft 

        // NOTA: He borrado los "Behavior on x/y/scale". 
        // Esto hace que el movimiento sea instantáneo y muy rápido.

        // A) Arrastre del fondo
        DragHandler {
            target: mapContainer
            acceptedButtons: Qt.LeftButton
        }

        // B) Zoom con Rueda (INSTANTÁNEO)
        WheelHandler {
            target: mapContainer
            onWheel: (event) => {
                let zoomFactor = event.angleDelta.y > 0 ? 1.15 : 0.85
                
                // Calcular posición del mouse relativa al mapa antes del zoom
                let mouseX_in_map = (event.x - mapContainer.x) / mapContainer.scale
                let mouseY_in_map = (event.y - mapContainer.y) / mapContainer.scale
                
                let newScale = Math.max(0.5, Math.min(mapContainer.scale * zoomFactor, 30.0))
                
                // Aplicar cambios directamente (sin animación)
                mapContainer.x = event.x - (mouseX_in_map * newScale)
                mapContainer.y = event.y - (mouseY_in_map * newScale)
                mapContainer.scale = newScale
            }
        }

        // C) Países
        Repeater {
            model: mapa_modelo

            Shape {
                id: countryShape
                width: 1010
                height: 660
                containsMode: Shape.FillContains

                ShapePath {
                    strokeWidth: 1.0 / mapContainer.scale 
                    strokeColor: "white"
                    fillColor: (model.color_pais && model.color_pais !== "") ? model.color_pais : "#CFD8DC"
                    fillRule: ShapePath.WindingFill
                    PathSvg { path: model.path }
                }

                MouseArea {
                    id: countryMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    containmentMask: countryShape
                    cursorShape: pressed ? Qt.ClosedHandCursor : Qt.PointingHandCursor
                    
                    // Permite arrastrar el mapa desde un país
                    drag.target: mapContainer
                    drag.filterChildren: true 

                    onDoubleClicked: (mouse) => {
                        let mapPoint = mapContainer.mapFromItem(countryMouse, mouse.x, mouse.y)
                        mapRoot.flyToCountry(mapPoint.x, mapPoint.y)
                    }

                    // --- TOOLTIP CORREGIDO ---
                    onEntered: {
                        if (!countryMouse.drag.active) {
                            try {
                                mapRoot.tooltipHtml = mapa_modelo.get_datos_pais_html(model.codigo)
                            } catch(e) { mapRoot.tooltipHtml = "Cargando..." }
                            
                            mapRoot.isTooltipVisible = true
                            // CORRECCIÓN: Usamos mouseX/mouseY directos, no el objeto 'mouse'
                            updateTooltipPos(mouseX, mouseY)
                        }
                    }
                    
                    onPositionChanged: (mouse) => {
                        if (countryMouse.drag.active) {
                            mapRoot.isTooltipVisible = false
                        } else {
                            // Aquí 'mouse' sí existe porque viene de la señal
                            updateTooltipPos(mouse.x, mouse.y)
                        }
                    }

                    onExited: mapRoot.isTooltipVisible = false
                    onCanceled: mapRoot.isTooltipVisible = false // Por si el arrastre cancela el hover

                    function updateTooltipPos(mx, my) {
                        var pos = mapToItem(mapRoot, mx, my)
                        mapRoot.tipX = pos.x + 15
                        mapRoot.tipY = pos.y + 15
                    }
                }
            }
        }
    }

    // =========================================================
    // 4. EL TOOLTIP
    // =========================================================
    Rectangle {
        visible: mapRoot.isTooltipVisible
        x: mapRoot.tipX
        y: mapRoot.tipY
        z: 9999
        width: infoTxt.contentWidth + 24
        height: infoTxt.contentHeight + 16
        color: "#2d3436"
        radius: 4
        border.color: "white"
        opacity: 0.95

        Text {
            id: infoTxt
            anchors.centerIn: parent
            text: mapRoot.tooltipHtml
            color: "white"
            font.pixelSize: 13
            textFormat: Text.RichText
        }
    }

    // =========================================================
    // 5. BOTONES
    // =========================================================
    Column {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20
        spacing: 10
        RoundButton {
            width: 50; height: 50; text: "+"; font.pixelSize: 24
            onClicked: mapRoot.setZoomManual(1.5)
        }
        RoundButton {
            width: 50; height: 50; text: "-"; font.pixelSize: 24
            onClicked: mapRoot.setZoomManual(0.6)
        }
    }
}
