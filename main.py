import sys
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtCore import QObject, QAbstractListModel, Qt, QUrl, Slot
import os
import json
import pandas as pd
import sqlite3 as sql
from controllers.sird_controller import ControladorSIRD


if __name__ == "__main__":
    
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_THEME"] = "Dark"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_ACCENT"] = "Purple"

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    controlador = ControladorSIRD()


    with open("ui/assets/paises.json") as f:
        json = json.load(f)

    conexion = sql.connect("backend/data/mundo.db")
    db = pd.read_sql("SELECT * FROM estado_actual",conexion)
    db.set_index("Country Code",inplace=True)
    conexion.close()

    engine.rootContext().setContextProperty("mapa_modelo", controlador.mapa_modelo)
    engine.rootContext().setContextProperty("backend", controlador)

    
    qml_file = Path(__file__).parent / "ui/main.qml"
    base_dir = os.path.dirname(__file__)
    engine.addImportPath(os.path.join(base_dir, "ui"))

    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
