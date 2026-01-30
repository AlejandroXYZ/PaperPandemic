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
    MuertoRole = Qt.UserRole + 7
    PoblacionRole = Qt.UserRole + 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paises = []
        
        # Cargar geometría del mapa
        try:
            # Truco para ruta segura
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path = os.path.join(BASE_DIR, "ui", "assets", "paises.json")
            with open(json_path, encoding='utf-8') as f:
                self.geometria = json.load(f)
        except Exception as e:
            print(f"❌ Error cargando paises.json: {e}")
            self.geometria = {}


        self.paleta_actual = [
            (0.00, 162, 178, 243), # Azul
            (0.25, 156, 39, 176),  # Morado
            (0.50, 233, 30, 99),   # Rosa
            (0.75, 213, 0, 0),     # Rojo
            (1.00, 100, 0, 0)      # Rojo Oscuro
        ]

        self._inicializar_vacio()

    def _inicializar_vacio(self):
        """Estado inicial: Todo azul tranquilo"""
        self.beginResetModel()
        self.paises = []
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
        # Esto permite encontrar un país instantáneamente sin buscar en la lista
        self._indice_rapido = {p["codigo"]: i for i, p in enumerate(self.paises)}

    def roleNames(self):
        return {
            self.CodigoRole: b"codigo",
            self.NombreRole: b"nombre",
            self.PathRole: b"path",
            self.InfectadoRole: b"infectado",
            self.RecuperadoRole: b"recuperado",
            self.ColorRole: b"color_pais",
            self.MuertoRole: b"muerto",     
            self.PoblacionRole: b"poblacion"
        }

    def rowCount(self, parent=None):
        return len(self.paises)

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self.paises): return None
        pais = self.paises[index.row()]
        
        if role == self.CodigoRole: return pais["codigo"]
        if role == self.NombreRole: return pais["nombre"]
        if role == self.PathRole: return pais["path"]
        if role == self.InfectadoRole: return pais["infectado"]
        if role == self.RecuperadoRole: return pais["recuperado"]
        if role == self.ColorRole: return pais["color"]
        if role == self.MuertoRole: return pais.get("muerto", 0) #.get por seguridad
        if role == self.PoblacionRole: return pais["poblacion"]
        return None


    @Slot(str, result=str)
    def get_datos_pais_html(self, codigo_pais):
        # OPTIMIZACIÓN O(1): Usamos el diccionario en vez de un bucle for
        idx = self._indice_rapido.get(codigo_pais)
        
        if idx is not None:
            pais = self.paises[idx]
            pob = pais['poblacion'] if pais['poblacion'] > 0 else 1
            pct = (pais['infectado'] / pob) * 100
            
            return (f"<b>{pais['nombre']}</b> ({pais['codigo']})<br>"
                    f"👥 Población: {pob:,}<br>"
                    f"🤒 Infectados: {pais['infectado']:,} ({pct:.2f}%)<br>"
                    f"💚 Recuperados: {pais['recuperado']:,}")
        
        return "Sin datos"



    def calcular_color_hex(self, porcentaje):
        stops = self.paleta_actual
                
        # Algoritmo de interpolación lineal
        for i in range(len(stops) - 1):
            t1, r1, g1, b1 = stops[i]
            t2, r2, g2, b2 = stops[i+1]
                    
            if porcentaje <= t2:
                # Evitar división por cero
                dist = t2 - t1
                if dist == 0: return f"#{r1:02x}{g1:02x}{b1:02x}"
                        
                factor = (porcentaje - t1) / dist
                r = int(r1 + (r2 - r1) * factor)
                g = int(g1 + (g2 - g1) * factor)
                b = int(b1 + (b2 - b1) * factor)
                return f"#{r:02x}{g:02x}{b:02x}"
                
        # Si supera el 100%, devuelve el último color
        _, lr, lg, lb = stops[-1]
        return f"#{lr:02x}{lg:02x}{lb:02x}"

    def actualizar_datos(self, lista_paises):
        if not self.paises or not lista_paises: return
        
        # Diccionario para acceso rápido O(1)
        datos_dict = { fila["Country Code"]: fila for fila in lista_paises if "Country Code" in fila }
        
        hay_cambios = False
        idx_min, idx_max = len(self.paises), 0

        for i, pais in enumerate(self.paises):
            codigo = pais["codigo"]
            if codigo in datos_dict:
                dato = datos_dict[codigo]
                
                i_val = int(dato.get("I", 0))
                r_val = int(dato.get("R", 0))
                m_val = int(dato.get("M", 0))
                pob = int(dato.get("S", 0)) + i_val + r_val + m_val
                
                if pob <= 0: pob = 1
                pais["poblacion"] = pob
                pais["infectado"] = i_val
                pais["recuperado"] = r_val
                pais["muerto"] = m_val
                
                if "Country Name" in dato:
                    pais["nombre"] = dato["Country Name"]
                
                # Color
                pct = (i_val + r_val + m_val) / pob
                nuevo_color = self.calcular_color_hex(pct)
                
                if pais["color"] != nuevo_color:
                    pais["color"] = nuevo_color
                    hay_cambios = True
                    idx_min = min(idx_min, i)
                    idx_max = max(idx_max, i)

        if hay_cambios:
            top = self.index(idx_min, 0)
            bot = self.index(idx_max, 0)
            self.dataChanged.emit(top, bot, [self.ColorRole, self.InfectadoRole, self.RecuperadoRole])



    def _hex_to_rgb(self, hex_color):
        """Convierte '#RRGGBB' a (R, G, B) enteros"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def actualizar_paleta_colores(self, lista_hex):
        """Recibe lista de 5 strings Hex desde QML y actualiza el motor"""
        if len(lista_hex) != 5: return
            
        nuevos_stops = []
        pasos = [0.00, 0.25, 0.50, 0.75, 1.00]
            
        for i, hex_code in enumerate(lista_hex):
            r, g, b = self._hex_to_rgb(hex_code)
            nuevos_stops.append((pasos[i], r, g, b))
                
        self.paleta_actual = nuevos_stops
            
        # FORZAMOS RE-PINTADO DE TODOS LOS PAÍSES
        # Recorremos todos los países y recalculamos su color con la nueva paleta
        hay_cambios = False
        for pais in self.paises:
            # Recalculamos el porcentaje actual
            pob = pais["poblacion"]
            infectados = pais["infectado"] + pais["recuperado"] + pais.get("muerto", 0)
            pct = infectados / pob if pob > 0 else 0
                
            nuevo_color = self.calcular_color_hex(pct)
            pais["color"] = nuevo_color
            hay_cambios = True
                
        if hay_cambios and self.paises:
            # Emitimos señal de que TODO cambió
            self.dataChanged.emit(self.index(0,0), self.index(len(self.paises)-1, 0), [self.ColorRole])
