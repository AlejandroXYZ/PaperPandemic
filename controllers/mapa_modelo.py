from PySide6.QtCore import QAbstractListModel, Qt
import json
import os

class MapaModeloSIRD(QAbstractListModel):
    CodigoRole = Qt.UserRole + 1
    NombreRole = Qt.UserRole + 2
    PathRole = Qt.UserRole + 3
    InfectadoRole = Qt.UserRole + 4
    RecuperadoRole = Qt.UserRole + 5
    # --- NUEVO: DEFINIMOS EL ROL PARA EL COLOR ---
    ColorRole = Qt.UserRole + 6 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paises = []
        
        # Carga del JSON (Ruta a prueba de balas)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(BASE_DIR, "ui", "assets", "paises.json")

        with open(json_path) as f:
            self.geometria = json.load(f)

    def roleNames(self):
        return {
            self.CodigoRole: b"codigo",
            self.NombreRole: b"nombre",
            self.PathRole: b"path",
            self.InfectadoRole: b"infectado",
            self.RecuperadoRole: b"recuperado",
            # --- NUEVO: LE DECIMOS A QML QUE USE EL NOMBRE "color_pais" ---
            self.ColorRole: b"color_pais"
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
        
        # --- NUEVO: RETORNAMOS EL COLOR HEXADECIMAL ---
        if role == self.ColorRole: return pais.get("color", "#D1D5DB") # Gris por defecto
        
        return None

    # ==========================================================
    # FUNCIÓN DE ACTUALIZACIÓN (OPTIMIZADA PARA ATOM)
    # ==========================================================
    def actualizar_datos(self, lista_paises):
        # 1. CARGA INICIAL (Solo ocurre una vez al arrancar)
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
                        "recuperado": int(fila["R"]),
                        # Guardamos el color que calculó Python
                        "color": fila.get("color_calculado", "#D1D5DB") 
                    })
            self.endResetModel()
            return

        # 2. ACTUALIZACIÓN EN TIEMPO REAL (Batch Update)
        # Convertimos la lista nueva a diccionario para acceso instantáneo
        diccionario_datos = {fila["Country Code"]: fila for fila in lista_paises}
        cambios = []
        
        hay_cambios_visuales = False
        indice_min = len(self.paises)
        indice_max = 0

        for i, pais in enumerate(self.paises):
            codigo = pais["codigo"]
            if codigo in diccionario_datos:
                fila_nueva = diccionario_datos[codigo]
                
                # Obtenemos los nuevos valores
                nuevo_infectado = int(fila_nueva["I"])
                nuevo_recuperado = int(fila_nueva["R"])
                nuevo_color = fila_nueva.get("color_calculado", "#D1D5DB")

                # Actualizamos siempre los datos numéricos en memoria
                pais["infectado"] = nuevo_infectado
                pais["recuperado"] = nuevo_recuperado

                # --- EL FILTRO DE RENDIMIENTO ---
                # Solo avisamos a la tarjeta gráfica si cambió el COLOR
                if pais.get("color") != nuevo_color:
                    pais["color"] = nuevo_color # Actualizamos color en memoria
                    cambios.append(i)
                    hay_cambios_visuales = True
                    if i < indice_min: indice_min = i
                    if i > indice_max: indice_max = i


        cantidad_cambios = len(cambios)

        if cantidad_cambios == 0:
            return

        if cantidad_cambios < 10: 
            for i in cambios:
                idx = self.index(i, 0)
                self.dataChanged.emit(idx, idx, [self.ColorRole])

        else:
            min_idx = min(cambios)
            max_idx = max(cambios)
            top_left = self.index(min_idx, 0)
            bottom_right = self.index(max_idx, 0)
            self.dataChanged.emit(top_left, bottom_right, [self.ColorRole])        

        if hay_cambios_visuales:
            top_left = self.index(indice_min, 0)
            bottom_right = self.index(indice_max, 0)
            self.dataChanged.emit(top_left, bottom_right, [self.ColorRole, self.InfectadoRole])
