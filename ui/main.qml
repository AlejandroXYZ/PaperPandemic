import QtQuick
import QtQuick.Controls
import components.utils
import QtQuick.Layouts

ApplicationWindow{
    id: mainWindow
    visible: true
    width: 1200 // Hacemos la ventana un poco más grande
    height: 720
    title: "Simulador SIRD - Dashboard"
    color: "#121212" // Fondo general de la app

    RowLayout {
        anchors.fill: parent
        
        Mapa {
            Layout.preferredWidth: parent.width * 0.7
            Layout.preferredHeight: parent.height
        }
    }
}
