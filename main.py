import sys
import os
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

# Asegúrate de que el import sea correcto según tu estructura de carpetas
from controllers.sird_controller import ControladorSIRD

if __name__ == "__main__":
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_THEME"] = "Dark"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_ACCENT"] = "Purple"

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Instanciar el Controlador
    controlador = ControladorSIRD()

    # Exponer a QML
    engine.rootContext().setContextProperty("backend", controlador)
    engine.rootContext().setContextProperty("mapa_modelo", controlador.mapa_modelo)
    
    # NOTA: Ya no hace falta setContextProperty("opciones"...) 
    # porque lo hacemos a través de backend.config
    
    # Rutas
    base_dir = os.path.dirname(os.path.abspath(__file__))
    engine.addImportPath(os.path.join(base_dir, "ui"))
    
    qml_file = Path(__file__).parent / "ui/main.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
