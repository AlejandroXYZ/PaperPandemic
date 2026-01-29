import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    anchors.fill: parent

    signal volverClicked()

    // Datos crudos
    property var rawData: [] // [Dias, S, I, R, M]
    property int maxDias: 1
    
    // Control de Visibilidad (Click en leyenda para alternar)
    property bool showS: true
    property bool showI: true
    property bool showR: true
    property bool showM: true

    // Colores Profesionales
    readonly property color colS: "#DCE775" // Verde Lima
    readonly property color colI: "#ff5252" // Rojo Intenso
    readonly property color colR: "#4fc3f7" // Azul Cielo
    readonly property color colM: "#95a5a6" // Gris Acero
    readonly property color colGrid: "#33ffffff" // Blanco muy tenue

    // Propiedad calculada: Máximo valor en el eje Y según lo que esté visible
    property real maxY: 1.0

    function cargarDatos() {
        if(backend) {
            var raw = backend.obtener_datos_historial()
            if(raw && raw.length === 5 && raw[0].length > 0) {
                rawData = raw
                maxDias = raw[0][raw[0].length - 1]
                calcularMaxY()
                canvas.requestPaint()
            }
        }
    }

    function calcularMaxY() {
        if (!rawData || rawData.length === 0) return;
        let maxVal = 0;
        // Buscamos el valor más alto SOLO de las líneas visibles
        // Esto permite "Zoom" automático al ocultar los Susceptibles
        if (showS) maxVal = Math.max(maxVal, Math.max(...rawData[1]));
        if (showI) maxVal = Math.max(maxVal, Math.max(...rawData[2]));
        if (showR) maxVal = Math.max(maxVal, Math.max(...rawData[3]));
        if (showM) maxVal = Math.max(maxVal, Math.max(...rawData[4]));
        
        // Un poco de margen arriba (10%)
        root.maxY = maxVal > 0 ? maxVal * 1.1 : 100;
    }

    // Al cambiar cualquier toggle, recalculamos escala y repintamos
    onShowSChanged: { calcularMaxY(); canvas.requestPaint() }
    onShowIChanged: { calcularMaxY(); canvas.requestPaint() }
    onShowRChanged: { calcularMaxY(); canvas.requestPaint() }
    onShowMChanged: { calcularMaxY(); canvas.requestPaint() }

    Component.onCompleted: cargarDatos()

    Rectangle {
        anchors.fill: parent
        color: "#1e1e2e" // Fondo oscuro elegante
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 10

        // --- CABECERA ---
        RowLayout {
            Layout.fillWidth: true
            Button {
                text: "⬅ Volver"
                flat: true
                onClicked: root.volverClicked()
                contentItem: Text { text: parent.text; color: "#bdc3c7"; font.bold: true }
                background: Rectangle { color: "#3a3f55"; radius: 5 }
            }
            Item { Layout.fillWidth: true } 
            Text {
                text: "Análisis de Tendencias SIRD"
                color: "white"
                font.pixelSize: 20
                font.bold: true
                font.letterSpacing: 1
            }
            Item { Layout.fillWidth: true }
        }

        // --- LEYENDA INTERACTIVA (Botones Toggle) ---
        Row {
            Layout.alignment: Qt.AlignHCenter
            spacing: 15
            
            // Componente interno para el botón de leyenda
            component LeyendaItem: MouseArea {
                width: rowInt.width + 10; height: 25
                property string label: ""
                property color colorBase: "white"
                property bool activo: true
                property var targetProp: "" // Nombre de la propiedad a cambiar (ej "showS")

                cursorShape: Qt.PointingHandCursor
                onClicked: root[targetProp] = !root[targetProp]

                Rectangle {
                    anchors.fill: parent
                    color: parent.activo ? "#20ffffff" : "transparent"
                    radius: 4
                    border.color: parent.activo ? parent.colorBase : "#555"
                    border.width: 1
                }
                Row {
                    id: rowInt
                    anchors.centerIn: parent
                    spacing: 6
                    Rectangle { 
                        width: 10; height: 10; radius: 5
                        color: parent.parent.activo ? parent.parent.colorBase : "#555"
                    }
                    Text { 
                        text: parent.parent.label
                        color: parent.parent.activo ? "white" : "#777"
                        font.pixelSize: 12
                        font.bold: true
                    }
                }
            }

            LeyendaItem { label: "Susceptibles"; colorBase: colS; activo: showS; targetProp: "showS" }
            LeyendaItem { label: "Infectados"; colorBase: colI; activo: showI; targetProp: "showI" }
            LeyendaItem { label: "Recuperados"; colorBase: colR; activo: showR; targetProp: "showR" }
            LeyendaItem { label: "Muertos"; colorBase: colM; activo: showM; targetProp: "showM" }
        }

        // --- GRÁFICO ---
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            Canvas {
                id: canvas
                anchors.fill: parent
                // Renderizado inmediato para evitar el "flicker" en Intel Atom
                renderStrategy: Canvas.Immediate 
                renderTarget: Canvas.Image

                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.clearRect(0, 0, width, height);

                    if (!root.rawData || root.rawData.length === 0) return;

                    var dias = root.rawData[0];
                    // Márgenes
                    var padL = 50; var padB = 30; var padR = 20; var padT = 20;
                    var plotW = width - padL - padR;
                    var plotH = height - padB - padT;

                    if (plotW <= 0 || plotH <= 0) return;

                    // Escala
                    var maxD = root.maxDias > 0 ? root.maxDias : 1;
                    var maxY = root.maxY > 0 ? root.maxY : 100;

                    function getX(dia) { return padL + (dia / maxD) * plotW; }
                    function getY(val) { return padT + plotH - (val / maxY) * plotH; }

                    // 1. DIBUJAR GRID (Cuadrícula)
                    ctx.strokeStyle = root.colGrid;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    // Horizontales (5 líneas)
                    for(var j=0; j<=5; j++) {
                        var yLine = padT + (plotH * j / 5);
                        ctx.moveTo(padL, yLine); ctx.lineTo(width-padR, yLine);
                        // Texto Eje Y
                        var labelVal = Math.round(maxY * (1 - j/5));
                        ctx.fillStyle = "#aaa"; ctx.font = "10px sans-serif";
                        ctx.fillText(formatNumber(labelVal), 2, yLine + 3);
                    }
                    // Verticales (5 líneas)
                    for(var k=0; k<=5; k++) {
                        var xLine = padL + (plotW * k / 5);
                        ctx.moveTo(xLine, padT); ctx.lineTo(xLine, height-padB);
                    }
                    ctx.stroke();

                    // 2. FUNCIÓN PARA DIBUJAR CURVAS CON RELLENO
                    function drawCurve(dataArr, color, isVisible) {
                        if(!isVisible) return;
                        
                        // A) El Relleno (Gradiente)
                        var grad = ctx.createLinearGradient(0, padT, 0, height-padB);
                        grad.addColorStop(0.0, color); // Color sólido arriba
                        grad.addColorStop(1.0, "transparent"); // Transparente abajo

                        ctx.beginPath();
                        ctx.moveTo(getX(dias[0]), getY(dataArr[0]));
                        for(var i=1; i<dias.length; i++) {
                            ctx.lineTo(getX(dias[i]), getY(dataArr[i]));
                        }
                        // Cerrar polígono para rellenar
                        ctx.lineTo(getX(dias[dias.length-1]), height-padB);
                        ctx.lineTo(getX(dias[0]), height-padB);
                        ctx.closePath();
                        
                        ctx.globalAlpha = 0.3; // Semitransparente
                        ctx.fillStyle = grad;
                        ctx.fill();
                        ctx.globalAlpha = 1.0;

                        // B) La Línea (Borde)
                        ctx.beginPath();
                        ctx.strokeStyle = color;
                        ctx.lineWidth = 2;
                        ctx.moveTo(getX(dias[0]), getY(dataArr[0]));
                        for(var i=1; i<dias.length; i++) {
                            ctx.lineTo(getX(dias[i]), getY(dataArr[i]));
                        }
                        ctx.stroke();
                    }

                    // 3. DIBUJAR CAPAS (Orden inverso para superposición correcta)
                    // Dibujamos primero Muertos/Recuperados para que queden abajo si se solapan
                    drawCurve(root.rawData[4], colM, showM); // M
                    drawCurve(root.rawData[3], colR, showR); // R
                    drawCurve(root.rawData[2], colI, colI, showI); // I
                    drawCurve(root.rawData[1], colS, showS); // S

                    // Ejes finales
                    ctx.strokeStyle = "#fff"; ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(padL, padT); ctx.lineTo(padL, height-padB); // Y
                    ctx.moveTo(padL, height-padB); ctx.lineTo(width-padR, height-padB); // X
                    ctx.stroke();
                    
                    // Texto Eje X
                    ctx.fillStyle = "#aaa";
                    ctx.fillText("Día 0", padL, height - 10);
                    ctx.fillText("Día " + maxD, width - 60, height - 10);
                }

                // Helper para formatear millones (1M, 500k)
                function formatNumber(num) {
                    if(num >= 1000000000) return (num/1000000000).toFixed(1) + "B";
                    if(num >= 1000000) return (num/1000000).toFixed(1) + "M";
                    if(num >= 1000) return (num/1000).toFixed(1) + "k";
                    return num;
                }
            }

            // --- CROSSHAIR (MIRA TELESCÓPICA) ---
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onPositionChanged: (mouse) => {
                    cursorLine.x = mouse.x
                    cursorLine.visible = (mouse.x > 50 && mouse.x < width - 20 && mouse.y < height - 30)
                    
                    if(cursorLine.visible && root.rawData.length > 0) {
                        // Calcular día aproximado
                        var plotW = width - 70; 
                        var pct = (mouse.x - 50) / plotW;
                        var diaIdx = Math.round(pct * (root.rawData[0].length - 1));
                        
                        // Clamp index
                        if(diaIdx < 0) diaIdx = 0;
                        if(diaIdx >= root.rawData[0].length) diaIdx = root.rawData[0].length - 1;

                        // Actualizar tooltip
                        tooltip.dia = root.rawData[0][diaIdx];
                        tooltip.s = root.rawData[1][diaIdx];
                        tooltip.i = root.rawData[2][diaIdx];
                        tooltip.r = root.rawData[3][diaIdx];
                        tooltip.m = root.rawData[4][diaIdx];
                        
                        // Posicionar tooltip inteligente (para que no se salga de pantalla)
                        if(mouse.x > width / 2) tooltip.x = mouse.x - tooltip.width - 15;
                        else tooltip.x = mouse.x + 15;
                        
                        tooltip.y = mouse.y
                    }
                }
                onExited: cursorLine.visible = false
            }

            // Línea Vertical
            Rectangle {
                id: cursorLine
                width: 1; height: parent.height - 30
                y: 20
                color: "white"
                visible: false
                opacity: 0.5
            }

            // Tooltip Flotante
            Rectangle {
                id: tooltip
                visible: cursorLine.visible
                width: 140; height: 110
                color: "#cc1e1e2e"; radius: 5; border.color: "#555"
                
                property int dia: 0
                property int s: 0; property int i: 0; property int r: 0; property int m: 0

                Column {
                    anchors.centerIn: parent
                    spacing: 3
                    Text { text: "Día " + tooltip.dia; color: "white"; font.bold: true; font.pixelSize: 14 }
                    Rectangle { width: parent.width; height: 1; color: "#555" }
                    
                    // Solo mostramos filas si están activas en la leyenda
                    Row { visible: root.showS; spacing: 5; Rectangle{width:8;height:8;color:colS;radius:4;anchors.verticalCenter:parent.verticalCenter} Text{text:"S: "+tooltip.format(tooltip.s);color:"#ccc";font.pixelSize:11} }
                    Row { visible: root.showI; spacing: 5; Rectangle{width:8;height:8;color:colI;radius:4;anchors.verticalCenter:parent.verticalCenter} Text{text:"I: "+tooltip.format(tooltip.i);color:"#ccc";font.pixelSize:11} }
                    Row { visible: root.showR; spacing: 5; Rectangle{width:8;height:8;color:colR;radius:4;anchors.verticalCenter:parent.verticalCenter} Text{text:"R: "+tooltip.format(tooltip.r);color:"#ccc";font.pixelSize:11} }
                    Row { visible: root.showM; spacing: 5; Rectangle{width:8;height:8;color:colM;radius:4;anchors.verticalCenter:parent.verticalCenter} Text{text:"M: "+tooltip.format(tooltip.m);color:"#ccc";font.pixelSize:11} }
                }

                function format(n) { return Number(n).toLocaleString(Qt.locale(), 'f', 0); }
            }
        }
    }
}
