from PySide6.QtCore import QAbstractListModel, Qt, Slot
import json
import os

class MapaModeloSIRD(QAbstractListModel):
    CodigoRole = Qt.UserRole + 1
    NombreRole = Qt.UserRole + 2
    PathRole = Qt.UserRole + 3
    InfectadoRole = Qt.UserRole + 4
    RecuperadoRole = Qt.UserRole + 5
    ColorRole = Qt.UserRole + 6 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paises = []
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(BASE_DIR, "ui", "assets", "paises.json")

        with open(json_path) as f:
            self.geometria = json.load(f)

        self._inicializar_vacio()

    def _inicializar_vacio(self):
        """Estado inicial: Todo azul tranquilo"""
        self.beginResetModel()
        self.paises = []
        # Color base solicitado: #A2B2F3 (Azul claro)
        for codigo, path in self.geometria.items():
            self.paises.append({
                "codigo": codigo,
                "nombre": codigo, 
                "path": path,
                "infectado": 0,
                "recuperado": 0,
                "poblacion": 1, # Temporal hasta que llegue la data real
                "color": "#A2B2F3"
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
        if role == self.ColorRole: return pais["color"]
        return None

    @Slot(str, result=str)
    def get_datos_pais_html(self, codigo_pais):
        for pais in self.paises:
            if pais["codigo"] == codigo_pais:
                # Evitamos dividir por cero
                pob = pais['poblacion'] if pais['poblacion'] > 0 else 1
                pct = (pais['infectado'] / pob) * 100
                
                # Formato bonito para el Tooltip
                return (f"<b>{pais['nombre']}</b> ({pais['codigo']})<br>"
                        f"👥 Población: {pob:,}<br>"
                        f"🤒 Infectados: {pais['infectado']:,} ({pct:.2f}%)<br>"
                        f"💚 Recuperados: {pais['recuperado']:,}")
        return "Sin datos"

    # =========================================================
    # GRADIENTE DE COLOR (Azul -> Morado -> Rosa -> Rojo)
    # =========================================================
    def calcular_color_hex(self, porcentaje):
        # porcentaje viene de 0.0 a 1.0
        
        # Puntos de control del gradiente (Porcentaje, R, G, B)
        stops = [
            (0.00, 162, 178, 243), # 0%   - #A2B2F3 (Azul Calma)
            (0.05, 156, 39, 176),  # 5%   - #9C27B0 (Morado - Inicio brote)
            (0.20, 233, 30, 99),   # 20%  - #E91E63 (Rosa - Grave)
            (0.50, 213, 0, 0),     # 50%  - #D50000 (Rojo - Crítico)
            (1.00, 100, 0, 0)      # 100% - #640000 (Rojo Oscuro - Total)
        ]

        # Buscar en qué segmento estamos
        for i in range(len(stops) - 1):
            t1, r1, g1, b1 = stops[i]
            t2, r2, g2, b2 = stops[i+1]

            if porcentaje <= t2:
                # Interpolación lineal
                factor = (porcentaje - t1) / (t2 - t1)
                r = int(r1 + (r2 - r1) * factor)
                g = int(g1 + (g2 - g1) * factor)
                b = int(b1 + (b2 - b1) * factor)
                return f"#{r:02x}{g:02x}{b:02x}"
        
        return "#640000" # Si se pasa de 100%

 
    def actualizar_datos(self, lista_paises):
        if not self.paises: return
                    
        datos_dict = {fila["Country Code"]: fila for fila in lista_paises}
                            
        hay_cambios_visuales = False
        idx_min = len(self.paises)
        idx_max = 0
                    
        for i, pais in enumerate(self.paises):
            codigo = pais["codigo"]
            if codigo in datos_dict:
                dato = datos_dict[codigo]
                                    
                s = int(dato.get("S", 0))       # Susceptibles (Sanos que nunca se enfermaron)
                i_val = int(dato.get("I", 0))   # Infectados (Enfermos ahora)
                r = int(dato.get("R", 0))       # Recuperados
                d = int(dato.get("D", 0))       # Muertos
                                    
                poblacion_total = s + i_val + r + d

                if poblacion_total <= 0: poblacion_total = 1
                                        
                afectados_acumulados = i_val + r + d
                pct_infeccion = afectados_acumulados / poblacion_total
                                    
                if pct_infeccion > 1.0: pct_infeccion = 1.0
                                    
                nuevo_color = self.calcular_color_hex(pct_infeccion)                    
                pais["infectado"] = i_val
                pais["recuperado"] = r
                pais["poblacion"] = poblacion_total
                pais["nombre"] = dato.get("Country Name", codigo)
                    
            if pais["color"] != nuevo_color:
                pais["color"] = nuevo_color
                hay_cambios_visuales = True
                if i < idx_min: idx_min = i
                if i > idx_max: idx_max = i
                    

        if hay_cambios_visuales:
            top = self.index(idx_min, 0)
            bot = self.index(idx_max, 0)
            self.dataChanged.emit(top, bot, [self.ColorRole])
