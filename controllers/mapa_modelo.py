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
        
        # Cargar geometría del mapa
        try:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path = os.path.join(BASE_DIR, "ui", "assets", "paises.json")
            with open(json_path, encoding='utf-8') as f:
                self.geometria = json.load(f)
        except Exception as e:
            print(f"❌ Error cargando paises.json: {e}")
            self.geometria = {}

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
                "poblacion": 1, 
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
        if index.row() >= len(self.paises): return None
        
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
                pob = pais['poblacion'] if pais['poblacion'] > 0 else 1
                pct = (pais['infectado'] / pob) * 100
                
                return (f"<b>{pais['nombre']}</b> ({pais['codigo']})<br>"
                        f"👥 Población: {pob:,}<br>"
                        f"🤒 Infectados: {pais['infectado']:,} ({pct:.2f}%)<br>"
                        f"💚 Recuperados: {pais['recuperado']:,}")
        return "Sin datos"

    # =========================================================
    # MOTOR DE COLORES
    # =========================================================
    def calcular_color_hex(self, porcentaje):
        # porcentaje de 0.0 a 1.0
        stops = [
            (0.00, 162, 178, 243), # Azul Base
            (0.05, 156, 39, 176),  # Morado (Inicio)
            (0.20, 233, 30, 99),   # Rosa (Grave)
            (0.50, 213, 0, 0),     # Rojo (Crítico)
            (1.00, 100, 0, 0)      # Rojo Oscuro (Apocalipsis)
        ]

        for i in range(len(stops) - 1):
            t1, r1, g1, b1 = stops[i]
            t2, r2, g2, b2 = stops[i+1]

            if porcentaje <= t2:
                factor = (porcentaje - t1) / (t2 - t1)
                r = int(r1 + (r2 - r1) * factor)
                g = int(g1 + (g2 - g1) * factor)
                b = int(b1 + (b2 - b1) * factor)
                return f"#{r:02x}{g:02x}{b:02x}"
        
        return "#640000"

    # =========================================================
    # ACTUALIZACIÓN BLINDADA (Aquí estaba el error)
    # =========================================================
    def actualizar_datos(self, lista_paises):
        if not self.paises or not lista_paises: return

        # Creamos diccionario ignorando filas sin código
        datos_dict = {}
        for fila in lista_paises:
            if "Country Code" in fila:
                datos_dict[fila["Country Code"]] = fila
        
        hay_cambios_visuales = False
        idx_min = len(self.paises)
        idx_max = 0

        for i, pais in enumerate(self.paises):
            codigo = pais["codigo"]
            
            # --- CORRECCIÓN: Todo ocurre SOLO si el país existe en los datos ---
            if codigo in datos_dict:
                dato = datos_dict[codigo]
                
                # 1. Obtenemos datos seguros (con .get para evitar KeyError)
                s = int(dato.get("S", 0))
                i_val = int(dato.get("I", 0))
                r = int(dato.get("R", 0))
                m = int(dato.get("M", 0)) # Usamos 'M' para coincidir con Loader
                
                # 2. Población real
                poblacion_total = s + i_val + r + m
                if poblacion_total <= 0: poblacion_total = 1
                
                # 3. Cálculo de Impacto (Acumulativo: I + R + M)
                afectados_acumulados = i_val + r + m
                pct_infeccion = afectados_acumulados / poblacion_total
                if pct_infeccion > 1.0: pct_infeccion = 1.0
                
                # 4. Cálculo de Color
                # Definimos la variable AQUÍ DENTRO
                nuevo_color = self.calcular_color_hex(pct_infeccion)
                
                # 5. Actualizar Datos Internos
                pais["infectado"] = i_val
                pais["recuperado"] = r
                pais["poblacion"] = poblacion_total
                # Actualizamos nombre si viene en el CSV (a veces el JSON tiene códigos raros)
                if "Country Name" in dato:
                    pais["nombre"] = dato["Country Name"]

                # 6. Detección de Cambios Visuales
                # Esta comprobación DEBE estar identada DENTRO del 'if codigo in datos_dict'
                if pais["color"] != nuevo_color:
                    pais["color"] = nuevo_color
                    hay_cambios_visuales = True
                    if i < idx_min: idx_min = i
                    if i > idx_max: idx_max = i

        # Solo emitimos señal a QML si realmente cambiaron colores (Optimización)
        if hay_cambios_visuales:
            top = self.index(idx_min, 0)
            bot = self.index(idx_max, 0)
            self.dataChanged.emit(top, bot, [self.ColorRole])
