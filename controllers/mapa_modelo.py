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
        # 1. Si es la primera vez, construimos la lista (esto no cambia)
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
            return

        # 2. Convertimos la lista nueva a diccionario para acceso rápido
        diccionario_datos = {fila["Country Code"]: fila for fila in lista_paises}
        
        # Variables para detectar el rango de cambios
        hay_cambios = False
        indice_min = len(self.paises)
        indice_max = 0

        # 3. Actualizamos los datos en MEMORIA (esto es rapidísimo, no toca la interfaz)
        for i, pais in enumerate(self.paises):
            codigo = pais["codigo"]
            if codigo in diccionario_datos:
                fila_nueva = diccionario_datos[codigo]
                nuevos_infectados = int(fila_nueva["I"])
                nuevos_recuperados = int(fila_nueva["R"])

                # Solo marcamos si hubo cambio real
                if pais["infectado"] != nuevos_infectados or pais["recuperado"] != nuevos_recuperados:
                    pais["infectado"] = nuevos_infectados
                    pais["recuperado"] = nuevos_recuperados
                    
                    hay_cambios = True
                    if i < indice_min: indice_min = i
                    if i > indice_max: indice_max = i

        # 4. EL SECRETO: Emitimos UNA SOLA señal al final
        # Solo si hubo cambios, le decimos a QML: "Redibuja desde el índice X hasta el Y"
        if hay_cambios:
            top_left = self.index(indice_min, 0)
            bottom_right = self.index(indice_max, 0)
            # El tercer argumento le dice a QML que SOLO revise los colores, no la geometría
            self.dataChanged.emit(top_left, bottom_right, [self.InfectadoRole, self.RecuperadoRole])
