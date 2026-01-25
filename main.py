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




class SIRD(QAbstractListModel):
    CodigoRole = Qt.UserRole + 1
    NombreRole = Qt.UserRole + 2
    PathRole = Qt.UserRole + 3
    SanoRole = Qt.UserRole + 4
    InfectadoRole = Qt.UserRole + 5
    RecuperadoRole = Qt.UserRole + 6
    MuertoRole = Qt.UserRole + 7


    def __init__(self, parent=None):
        super().__init__()
        self.paises = []



    def roleNames(self):
        return {
            self.CodigoRole: b"codigo",
            self.NombreRole: b"nombre",
            self.PathRole: b"path",
            self.SanoRole: b"sano",
            self.InfectadoRole: b"infectado",
            self.RecuperadoRole: b"recuperado",
            self.MuertoRole: b"muerto"
        }

    def rowCount(self, parent=None):
        return len(self.paises)


    def data(self, index, role):
        if not index.isValid():
            return None
        country = self.paises[index.row()]

        if role == self.CodigoRole: return country["codigo"]
        if role == self.NombreRole: return country["nombre"]
        if role == self.PathRole: return country["path"]
        if role == self.InfectadoRole: return country["infectado"]
        if role == self.SanoRole: return country["sano"]
        if role == self.RecuperadoRole: return country["recuperado"]
        if role == self.MuertoRole: return country["muerto"]

        return None


    def load_data(self, json_data, sql_data):
        self.beginResetModel()
        self.paises = []

        for code, path in json_data.items():
            if code in sql_data.index:
                sql_info = sql_data.loc[code]
                self.paises.append({
                    "codigo": code,
                    "path": path,
                    "nombre": sql_info["Country Name"],
                    "sano": int(sql_info["S"]),
                    "infectado": int(sql_info["I"]),
                    "recuperado": int(sql_info["R"]),
                    "muerto": int(sql_info["M"])
                })
        print(f"✅ ¡Éxito! Se cargaron {len(self.paises)} países en el modelo.")
        self.endResetModel()


if __name__ == "__main__":
    
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_THEME"] = "Dark"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_ACCENT"] = "Purple"

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    with open("ui/assets/paises.json") as f:
        json = json.load(f)

    conexion = sql.connect("backend/data/mundo.db")
    db = pd.read_sql("SELECT * FROM estado_actual",conexion)
    db.set_index("Country Code",inplace=True)
    conexion.close()

    mapa_modelo = SIRD()
    mapa_modelo.load_data(json,db)
    engine.rootContext().setContextProperty("mapa_modelo",mapa_modelo)
    
    qml_file = Path(__file__).parent / "ui/main.qml"
    base_dir = os.path.dirname(__file__)
    engine.addImportPath(os.path.join(base_dir, "ui"))

    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
