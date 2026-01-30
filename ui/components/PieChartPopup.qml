import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: 320; height: 450 // Aumentamos un poco la altura para el nuevo texto
    color: "#ee1e1e2e" 
    radius: 12
    border.color: "#666"
    border.width: 1
    visible: false
    z: 10000 

    property var datosPais: ({ valS:0, valI:0, valR:0, valM:0, poblacion:0, nombre:"Cargando..." })
    property string codigoPaisActual: "" 

    signal cerrarFronterasClicked()
    signal estadisticasClicked()

    readonly property color cS: "#DCE775"
    readonly property color cI: "#ff5252"
    readonly property color cR: "#4fc3f7"
    readonly property color cM: "#95a5a6"

    property int hoveredSlice: -1
    property string tooltipText: ""
    property color tooltipColor: "transparent"

    Timer {
        id: forcePaintTimer
        interval: 100
        repeat: false
        onTriggered: pieCanvas.requestPaint()
    }

    Connections {
        target: root.visible ? backend : null
        function onDiaChanged(nuevoDia) {
            if (root.codigoPaisActual === "") return;
            var diaNum = parseInt(nuevoDia)
            if (diaNum % 5 === 0) refrescarDatos()
        }
    }

    function refrescarDatos() {
        if(backend && root.codigoPaisActual !== "") {
            var nuevosDatos = backend.obtener_detalle_pais(root.codigoPaisActual)
            if (nuevosDatos.existe) root.datosPais = nuevosDatos
        }
    }

    function abrir(xClick, anchoPantalla, altoPantalla, codigoPais) {
        root.codigoPaisActual = codigoPais
        refrescarDatos()

        if(!datosPais.existe) return;

        var margen = 30
        var topMargen = 40
        var anchoPanel = (anchoPantalla * 0.45) 
        var altoPanel = altoPantalla - (topMargen * 2)

        root.width = anchoPanel
        root.height = altoPanel
        root.y = topMargen

        if (xClick < anchoPantalla / 2) {
            root.x = anchoPantalla - anchoPanel - margen
        } else {
            root.x = margen
        }
        
        root.visible = true
        pieCanvas.requestPaint()
        forcePaintTimer.start()
    }

    onDatosPaisChanged: pieCanvas.requestPaint()

    RoundButton {
        text: "✕"
        width: 40; height: 40
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 10
        font.pixelSize: 18
        flat: true
        contentItem: Text { text: parent.text; color: "#aaa"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
        onClicked: {
            root.visible = false
            root.codigoPaisActual = "" 
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 25
        spacing: 15

        // TÍTULO DEL PAÍS
        Text {
            text: root.datosPais.nombre || "..."
            color: "white"
            font.bold: true
            font.pixelSize: 26
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }

        // GRÁFICO (Canvas)
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 180
            
            Canvas {
                id: pieCanvas
                anchors.fill: parent
                
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.clearRect(0, 0, width, height);
                    
                    if (!root.datosPais || root.datosPais.poblacion === undefined) return;

                    var minSide = Math.min(width, height);
                    if (minSide < 10) return;

                    var cx = width / 2;
                    var cy = height / 2;
                    var radius = (minSide / 2) - 15;

                    if (radius <= 0) return;

                    var total = Number(root.datosPais.poblacion);
                    var valS = Number(root.datosPais.valS);
                    var valI = Number(root.datosPais.valI);
                    var valR = Number(root.datosPais.valR);
                    var valM = Number(root.datosPais.valM);

                    var startAngle = 0;

                    function drawSlice(val, color) {
                        if(val <= 0) return;
                        var sliceAngle = (val / total) * 2 * Math.PI;
                        
                        ctx.beginPath();
                        ctx.moveTo(cx, cy); // Vamos al centro para hacer pastel completo
                        ctx.arc(cx, cy, radius, startAngle, startAngle + sliceAngle);
                        ctx.closePath();
                        
                        // 1. Relleno
                        ctx.fillStyle = color;
                        ctx.fill();
                        
                        // 2. Borde Blanco Grueso
                        ctx.lineWidth = 3; // Grosor del borde
                        ctx.strokeStyle = "white";
                        ctx.stroke();
                        
                        startAngle += sliceAngle;
                    }

                    drawSlice(valS, root.cS);
                    drawSlice(valI, root.cI);
                    drawSlice(valR, root.cR);
                    drawSlice(valM, root.cM);
                    
                    // YA NO DIBUJAMOS EL AGUJERO DEL DONUT AQUÍ
                }
            }

            // Mouse Hover (Actualizado para pastel completo)
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onExited: root.hoveredSlice = -1
                
                onPositionChanged: (mouse) => {
                    var cx = width / 2; var cy = height / 2;
                    var dx = mouse.x - cx; var dy = mouse.y - cy;
                    var dist = Math.sqrt(dx*dx + dy*dy);
                    var minSide = Math.min(width, height);
                    var radius = (minSide / 2) - 15;

                    if (radius <= 0) return;
                    // Solo comprobamos si sale del radio exterior (ya no hay hueco interior)
                    if (dist > radius) {
                        root.hoveredSlice = -1; return;
                    }

                    var angle = Math.atan2(dy, dx);
                    if (angle < 0) angle += 2 * Math.PI;

                    var total = Number(root.datosPais.poblacion);
                    var currentAngle = 0;
                    var slices = [
                        {val: Number(root.datosPais.valS), lbl: "Sanos", pct: root.datosPais.pctS, col: root.cS},
                        {val: Number(root.datosPais.valI), lbl: "Infectados", pct: root.datosPais.pctI, col: root.cI},
                        {val: Number(root.datosPais.valR), lbl: "Recuperados", pct: root.datosPais.pctR, col: root.cR},
                        {val: Number(root.datosPais.valM), lbl: "Muertos", pct: root.datosPais.pctM, col: root.cM}
                    ];

                    for(var i=0; i<slices.length; i++) {
                        if(slices[i].val <= 0) continue;
                        var sliceAngle = (slices[i].val / total) * 2 * Math.PI;
                        if (angle < currentAngle + sliceAngle) {
                            root.hoveredSlice = i;
                            root.tooltipText = slices[i].lbl + "\n" + Number(slices[i].pct).toFixed(2) + "%";
                            root.tooltipColor = slices[i].col;
                            return;
                        }
                        currentAngle += sliceAngle;
                    }
                    root.hoveredSlice = -1;
                }
            }
            
            // Tooltip flotante
            Rectangle {
                visible: root.hoveredSlice !== -1
                width: 100; height: 50
                color: root.tooltipColor
                radius: 8
                border.color: "white"
                border.width: 2
                anchors.centerIn: parent
                Text {
                    anchors.centerIn: parent
                    text: root.tooltipText
                    color: "black"; font.bold: true; horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        // LEYENDA (DATOS NUMÉRICOS)
        RowLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter
            spacing: 15

            component LeyendaItem: Column {
                property color colorBase
                property string titulo
                property real valor
                
                spacing: 3
                Layout.alignment: Qt.AlignTop 

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 5
                    Rectangle { width: 10; height: 10; radius: 5; color: parent.parent.colorBase; anchors.verticalCenter: parent.verticalCenter }
                    Text { text: parent.parent.titulo; color: "#ccc"; font.pixelSize: 11; font.bold: true }
                }
                Text { 
                    text: Number(parent.valor || 0).toLocaleString(Qt.locale(), 'f', 0)
                    color: "white"; font.bold: true; font.pixelSize: 13
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
            
            LeyendaItem { colorBase: root.cS; titulo: "Sanos";       valor: root.datosPais.valS }
            LeyendaItem { colorBase: root.cI; titulo: "Infectados";  valor: root.datosPais.valI }
            LeyendaItem { colorBase: root.cR; titulo: "Recuperados"; valor: root.datosPais.valR }
            LeyendaItem { colorBase: root.cM; titulo: "Muertos";     valor: root.datosPais.valM }
        }

        // NUEVO: TEXTO POBLACIÓN TOTAL
        // Se coloca DEBAJO de la leyenda, como título centrado
        Text {
            text: "Población: " + Number(root.datosPais.poblacion).toLocaleString(Qt.locale(), 'f', 0)
            color: "white"
            font.bold: true
            font.pixelSize: 18 // Un poco más grande
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 5
        }

        Item { Layout.fillHeight: true; Layout.preferredHeight: 10 }

        // BOTONES
        ColumnLayout {
            spacing: 10
            
            component ActionButton: Button {
                Layout.fillWidth: true; height: 45
                property color baseColor: "#333"
                background: Rectangle { color: parent.baseColor; radius: 8 }
                contentItem: Text { text: parent.text; color: "white"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                scale: hovered ? 1.02 : 1.0
                Behavior on scale { NumberAnimation { duration: 100 } }
            }

            ActionButton {
                text: "🔒 CERRAR FRONTERAS"
                baseColor: "#3a3f55"
                onClicked: root.cerrarFronterasClicked()
            }

            ActionButton {
                text: "📊 VER ESTADÍSTICAS"
                baseColor: "#e67e22"
                onClicked: root.estadisticasClicked()
            }
        }
    }
}
