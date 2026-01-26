from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex
import json
import os

class MapaModeloSIRD(QAbstractListModel):
    CodigoRole = Qt.UserRole + 1
    NombreRole = Qt.UserRole + 2
    PathRole = Qt.UserRole + 3
    InfectadoRole = Qt.UserRole + 4
    RecuperadoRole = Qt.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paises = []

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(BASE_DIR, "ui", "assets", "paises.json")
        
        # Cargamos la geometría (los dibujos SVG) del mapa una sola vez
        with open(json_path) as f:
            self.geometria = json.load(f)

    def roleNames(self):
        return {
            self.CodigoRole: b"codigo",
            self.NombreRole: b"nombre",
            self.PathRole: b"path",
            self.InfectadoRole: b"infectado",
            self.RecuperadoRole: b"recuperado"
        }

    def rowCount(self, parent=None):
        return len(self.paises)

    def data(self, index, role):
        if not index.isValid(): return None
        pais = self.paises[index.row()]

        if role == self.CodigoRole: return pais["codigo"]
        if role == self.NombreRole: return pais["nombre"]
        if role == self.PathRole: return pais["path"]
        if role == self.InfectadoRole: return pais["infectado"]
        if role == self.RecuperadoRole: return pais["recuperado"]
        return None



    def actualizar_datos(self, lista_paises):
        if not self.paises:
            self.beginResetModel()
            for fila in lista_paises:
                codigo = fila["Country Code"]
                if codigo in self.geometria:
                    self.paises.append({
                        "codigo": codigo,
                        "nombre": fila["Country Name"],
                        "path": self.geometria[codigo],
                        "infectado": int(fila["I"]),
                        "recuperado": int(fila["R"])
                    })
            self.endResetModel()
        else:
            diccionario_datos = {fila["Country Code"]: fila for fila in lista_paises}
            
                        # Actualizamos los números de cada país
            for pais in self.paises:
                codigo = pais["codigo"]
                if codigo in diccionario_datos:
                    fila_nueva = diccionario_datos[codigo]
                    pais["infectado"] = int(fila_nueva["I"])
                    pais["recuperado"] = int(fila_nueva["R"])
            
            top_left = self.index(0, 0)
            bottom_right = self.index(len(self.paises) - 1, 0)
            self.dataChanged.emit(top_left, bottom_right)
