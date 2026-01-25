import QtQuick
import QtQuick.Controls
import QtQuick.Shapes

Item {
    id: mapRoot
    anchors.fill: parent
    clip: true // Evita que el mapa se desborde del área que le asignes

    // Función para "volar" hacia el país
    function flyToCountry(clickX, clickY) {
        let targetScale = 5.0; 
        
        // Calculamos el centro usando el ancho/alto de este componente (mapRoot)
        let newX = (mapRoot.width / 2) - 500 - (clickX - 500) * targetScale;
        let newY = (mapRoot.height / 2) - 400 - (clickY - 400) * targetScale;

        mapContainer.scale = targetScale;
        mapContainer.x = newX;
        mapContainer.y = newY;
    }

    // Función para los botones de zoom manual (+/-)
    function setZoom(factor) {
        let newScale = mapContainer.scale * factor;
        mapContainer.scale = Math.max(0.5, Math.min(newScale, 10.0));
    }

    Item {
        id: mapContainer
        width: 1000
        height: 800
        scale: 0.8
        transformOrigin: Item.Center 

        DragHandler {
            id: mapDragHandler
            target: mapContainer
            acceptedButtons: Qt.LeftButton 
        }

        WheelHandler {
            id: mapWheelHandler 
            target: mapContainer
            onWheel: (event) => {
                mapRoot.setZoom(event.angleDelta.y > 0 ? 1.15 : 0.85);
            }
        }

        // Animaciones desactivadas durante la interacción manual
        Behavior on x { enabled: !mapDragHandler.active; NumberAnimation { duration: 600; easing.type: Easing.InOutQuad } }
        Behavior on y { enabled: !mapDragHandler.active; NumberAnimation { duration: 600; easing.type: Easing.InOutQuad } }
        Behavior on scale { enabled: !mapWheelHandler.active; NumberAnimation { duration: 600; easing.type: Easing.InOutQuad } }

        Repeater {
            // El modelo viene de Python (main.py)
            model: mapa_modelo 

            Shape {
                id: countryShape
                width: 1000
                height: 800
                containsMode: Shape.FillContains 

                ShapePath {
                    strokeWidth: 1
                    strokeColor: "#ffffff"
                    fillRule: ShapePath.WindingFill 

                    fillColor: mouseArea.containsMouse ? "#BDD7DA" : 
                               (model.infectado > 1 ? "#ffb8b8" : "#A2C8E7")

                    PathSvg { path: model.path } 
                }

                MouseArea {
                    id: mouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    containmentMask: countryShape 
                    preventStealing: false 
                    
                    onDoubleClicked: (mouse) => {
                        mapRoot.flyToCountry(mouse.x, mouse.y);
                    }
                }

                ToolTip {
                    id: countryTooltip
                    visible: mouseArea.containsMouse
                    delay: 50
                    x: mouseArea.mouseX + 15
                    y: mouseArea.mouseY + 15

                    text: "<b>" + model.nombre + " (" + model.codigo + ")</b><br>" + 
                          "🤒 Infectados: " + model.infectado + "<br>" +
                          "💚 Recuperados: " + model.recuperado
                    
                    background: Rectangle {
                        color: "#2f3542"
                        radius: 6
                        border.color: "#747d8c"
                        border.width: 1
                    }
                    
                    contentItem: Text {
                        text: countryTooltip.text 
                        color: "white"
                        font.pixelSize: 14
                        textFormat: Text.RichText 
                    }
                }
            }
        }
    }

    // BOTONES FLOTANTES DE ZOOM
    Column {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20
        spacing: 10

        RoundButton {
            width: 45; height: 45
            onClicked: mapRoot.setZoom(1.5)
            background: Rectangle {
                color: parent.pressed ? "#444" : "#2f3542"
                radius: width / 2
                border.color: "#747d8c"
            }
            contentItem: Text { text: "+"; color: "white"; font.pixelSize: 24; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
        }

        RoundButton {
            width: 45; height: 45
            onClicked: mapRoot.setZoom(0.7)
            background: Rectangle {
                color: parent.pressed ? "#444" : "#2f3542"
                radius: width / 2
                border.color: "#747d8c"
            }
            contentItem: Text { text: "−"; color: "white"; font.pixelSize: 24; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
        }
    }
}
