from PySide6.QtCore import QAbstractListModel, Qt, Slot
import json
import os

class MapaModeloSIRD(QAbstractListModel):
    # Definimos los identificadores para QML
    CodigoRole = Qt.UserRole + 1
    NombreRole = Qt.UserRole + 2
    PathRole = Qt.UserRole + 3
    InfectadoRole = Qt.UserRole + 4
    RecuperadoRole = Qt.UserRole + 5
    ColorRole = Qt.UserRole + 6 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paises = []
        
        # Carga del JSON
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(BASE_DIR, "ui", "assets", "paises.json")

        with open(json_path) as f:
            self.geometria = json.load(f)

        # Carga inicial vacía para que el mapa se vea gris al abrir la app
        self._inicializar_vacio()

    def _inicializar_vacio(self):
        """Carga la geometría base sin datos de infección"""
        self.beginResetModel()
        self.paises = []
        for codigo, path in self.geometria.items():
            self.paises.append({
                "codigo": codigo,
                "nombre": codigo, # Se actualizará luego con el nombre real
                "path": path,
                "infectado": 0,
                "recuperado": 0,
                "color": "#CFD8DC" # Gris inicial
            })
        self.endResetModel()

    def roleNames(self):
        return {
            self.CodigoRole: b"codigo",
            self.NombreRole: b"nombre",
            self.PathRole: b"path",
            self.InfectadoRole: b"infectado",
            self.RecuperadoRole: b"recuperado",
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
        if role == self.ColorRole: return pais.get("color", "#CFD8DC")
        
        return None


    @Slot(str, result=str)
    def get_datos_pais_html(self, codigo_pais):
        """Busca los datos frescos en memoria y devuelve HTML listo para el Tooltip"""
        for pais in self.paises:
            if pais["codigo"] == codigo_pais:
                return (f"<b>{pais['nombre']} ({pais['codigo']})</b><br>"
                        f"🤒 Infectados: {pais['infectado']:,}<br>"
                        f"💚 Recuperados: {pais['recuperado']:,}")
        return "Sin datos"


    # ==========================================================
    # FUNCIÓN CORREGIDA (Ahora actualiza Tooltips + Colores)
    # ==========================================================
    def actualizar_datos(self, lista_paises):
        # Si la lista está vacía (inicio), la llenamos primero
        if not self.paises:
            self._inicializar_vacio()

        diccionario_datos = {fila["Country Code"]: fila for fila in lista_paises}
        
        hay_cambios = False
        idx_min = len(self.paises)
        idx_max = 0

        for i, pais in enumerate(self.paises):
            codigo = pais["codigo"]
            if codigo in diccionario_datos:
                dato_nuevo = diccionario_datos[codigo]
                
                nuevo_color = dato_nuevo.get("color_calculado", "#CFD8DC")
                nuevo_infectado = int(dato_nuevo["I"])
                nuevo_recuperado = int(dato_nuevo["R"])
                nuevo_nombre = dato_nuevo["Country Name"]

                # --- EL CAMBIO CLAVE ESTÁ AQUÍ ---
                # Comparamos TODO: Color, Infectados y Recuperados.
                # Si CUALQUIERA cambia, marcamos para actualizar.
                if (pais["infectado"] != nuevo_infectado or 
                    pais["recuperado"] != nuevo_recuperado or 
                    pais["color"] != nuevo_color):
                    
                    # Actualizamos memoria
                    pais["infectado"] = nuevo_infectado
                    pais["recuperado"] = nuevo_recuperado
                    pais["color"] = nuevo_color
                    pais["nombre"] = nuevo_nombre # Actualizamos nombre real
                    
                    hay_cambios = True
                    if i < idx_min: idx_min = i
                    if i > idx_max: idx_max = i

        # Si hubo cambios, avisamos a QML
        if hay_cambios:
            top_left = self.index(idx_min, 0)
            bottom_right = self.index(idx_max, 0)
            
            # IMPORTANTE: Enviamos la lista de TODOS los roles que cambiaron
            # Esto le dice a QML: "Redibuja el color Y actualiza el texto del tooltip"
            self.dataChanged.emit(top_left, bottom_right, [
                self.ColorRole, 
                self.InfectadoRole, 
                self.RecuperadoRole,
                self.NombreRole
            ])
