from PySide6.QtCore import QAbstractListModel, Qt, Slot
import json
import os
from typing import List,Dict,Tuple

class MapaModeloSIRD(QAbstractListModel):
    """Esta clase es la encargada de enviarles los datos a QML para dibujar el Mapa"""

    # Roles para QML
    CodigoRole: int = Qt.UserRole + 1
    NombreRole: int = Qt.UserRole + 2
    PathRole: int = Qt.UserRole + 3
    InfectadoRole:int = Qt.UserRole + 4
    RecuperadoRole:int = Qt.UserRole + 5
    ColorRole:int = Qt.UserRole + 6 
    MuertoRole:int = Qt.UserRole + 7
    PoblacionRole:int = Qt.UserRole + 8


    def __init__(self, parent=None):
        super().__init__(parent)
        self.paises: List = []
        
        # 1. CARGA DE GEOMETRÍA
        try:
            BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path: str = rutas(os.path.join("ui","assets","paises.json"))
            with open(json_path, encoding='utf-8') as f:
                self.geometria = json.load(f)
        except Exception as e:
            print(f"❌ Error cargando paises.json: {e}")
            self.geometria: Dict = {}

        # 2. DICCIONARIO DE ALIAS (Para arreglar las islas "Sin datos")
        self.alias_map: Dict[str,str] = {
            "BAK": "UMI", "GLO": "UMI", "HOW": "UMI", "JAR": "UMI", 
            "JHN": "UMI", "JUA": "UMI", "MID": "UMI", "WAK": "UMI", 
            "XKX": "XKX"
        }

        # 3. Paleta de colores inicial
        self.paleta_actual: List[Tuple[float]] = [
            (0.00, 162, 178, 243), # Azul
            (0.25, 156, 39, 176),  # Morado
            (0.50, 233, 30, 99),   # Rosa
            (0.75, 213, 0, 0),     # Rojo
            (1.00, 100, 0, 0)      # Rojo Oscuro
        ]

        self._inicializar_vacio()

    def _inicializar_vacio(self):
        """Estado inicial del Mapa"""
        self.beginResetModel()
        self.paises: List[Dict[str,str|int]] = []
        # Ordenamos por código para consistencia
        for codigo, path in sorted(self.geometria.items()):
            self.paises.append({
                "codigo": codigo,
                "nombre": codigo, 
                "path": path,
                "infectado": 0, "recuperado": 0, "muerto": 0, "poblacion": 1, 
                "color": "#A2B2F3"
            })
        self.endResetModel()
        self._indice_rapido: Dict[str,int] = {p["codigo"]: i for i, p in enumerate(self.paises)} # Agrega los indices a los paises


    def roleNames(self) -> Dict[int,bytes]:
        """Convierte los enteros a bytes porque el motor de C++ espera un objeto tipo QByteArray"""
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

    def rowCount(self, parent=None) -> int:
        """Método Abstracto de la clase QAbstractListModel, pide que le pase la cantidad de objetos"""
        return len(self.paises)


    def data(self, index, role):
        """
            Metodo Esencial que actua como mensajero entre QML y Python
            Args:
                index: indica la posición que se quiere consultar
                role: indica qué tipo de información se solicita
        """
        
        if not index.isValid() or index.row() >= len(self.paises): return None
        pais:pd.Series = self.paises[index.row()]
        
        if role == self.CodigoRole: return pais["codigo"]
        if role == self.NombreRole: return pais["nombre"]
        if role == self.PathRole: return pais["path"]
        if role == self.InfectadoRole: return pais["infectado"]
        if role == self.RecuperadoRole: return pais["recuperado"]
        if role == self.ColorRole: return pais["color"]
        if role == self.MuertoRole: return pais.get("muerto", 0)
        if role == self.PoblacionRole: return pais["poblacion"]
        return None


    # --- MÉTODOS PARA QML ---

    @Slot(str, result=str)
    def get_datos_pais_html(self, codigo_pais:str) -> Tuple|str:
        """
        Proporciona datos al tooltip que se aparece cuando se hace hover encima de un país
        """
        
        idx: int = self._indice_rapido.get(codigo_pais)
        
        if idx is not None:
            pais = self.paises[idx]
            pob = pais['poblacion'] if pais['poblacion'] > 0 else 1
            pct = (pais['infectado'] / pob) * 100
            
            return (f"<b>{pais['nombre']}</b> ({pais['codigo']})<br>"
                    f"👥 Población: {pob:,}<br>"
                    f"🤒 Infectados: {pais['infectado']:,} ({pct:.2f}%)<br>"
                    f"💚 Recuperados: {pais['recuperado']:,}")
        
        return "Sin datos"


    # --- ESTOS SON NECESARIOS PARA EL GRÁFICO DE PASTEL ---
    @Slot(str, result=str)
    def get_nombre_pais(self, codigo_pais:str) -> str:
        idx:int = self._indice_rapido.get(codigo_pais)
        if idx is not None: return self.paises[idx]["nombre"]
        return codigo_pais

    @Slot(str, result=int)
    def get_poblacion_pais(self, codigo_pais:str) -> int:
        idx:int = self._indice_rapido.get(codigo_pais)
        if idx is not None: return int(self.paises[idx]["poblacion"])
        return 0
    # ------------------------------------------------------

    def calcular_color_hex(self, porcentaje: float) -> str:
        """Determina el color de un país según su número de infectados"""
        stops: List[Tuple[float]]  = self.paleta_actual
        for i in range(len(stops) - 1):
            t1, r1, g1, b1 = stops[i]
            t2, r2, g2, b2 = stops[i+1]
            if porcentaje <= t2:
                dist: float = t2 - t1
                if dist == 0: return f"#{r1:02x}{g1:02x}{b1:02x}"
                factor: float = (porcentaje - t1) / dist
                r: int = int(r1 + (r2 - r1) * factor)
                g: int = int(g1 + (g2 - g1) * factor)
                b: int = int(b1 + (b2 - b1) * factor)
                return f"#{r:02x}{g:02x}{b:02x}"
        _, lr, lg, lb = stops[-1]
        return f"#{lr:02x}{lg:02x}{lb:02x}"



    def actualizar_datos(self, lista_paises: Dict) -> None:
    
        if not self.paises or not lista_paises: return
        
        datos_dict: Dict = { fila["Country Code"]: fila for fila in lista_paises if "Country Code" in fila }
        
        hay_cambios : bool= False
        idx_min, idx_max = len(self.paises), 0

        for i, pais in enumerate(self.paises):
            codigo_mapa: str  = pais["codigo"]
            
            # TRADUCCIÓN DE ALIAS (Para arreglar islas UMI, BAK, etc.)
            codigo_busqueda:str = self.alias_map.get(codigo_mapa, codigo_mapa)
            
            if codigo_busqueda in datos_dict:
                dato:str = datos_dict[codigo_busqueda]
                
                i_val:int = int(dato.get("I", 0))
                r_val:int = int(dato.get("R", 0))
                m_val:int = int(dato.get("M", 0))
                pob:int = int(dato.get("S", 0)) + i_val + r_val + m_val
                
                if pob <= 0: pob:int = 1
                pais["poblacion"]:int = pob
                pais["infectado"]:int = i_val
                pais["recuperado"]:int = r_val
                pais["muerto"]:int = m_val
                
                if "Country Name" in dato:
                    pais["nombre"]: str = dato["Country Name"]
                
                # Color
                pct:float = (i_val + r_val + m_val) / pob
                nuevo_color: str = self.calcular_color_hex(pct)
                
                if pais["color"] != nuevo_color:
                    pais["color"]: str = nuevo_color
                    hay_cambios: bool = True
                    idx_min: int = min(idx_min, i)
                    idx_max: int = max(idx_max, i)

        if hay_cambios:
            top: int = self.index(idx_min, 0)
            bot: int = self.index(idx_max, 0)
            self.dataChanged.emit(top, bot, [self.ColorRole, self.InfectadoRole, self.RecuperadoRole])

            

    def _hex_to_rgb(self, hex_color) -> Tuple[int]:
        """Convierte los colores a números para usarlos en formato RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        

    def actualizar_paleta_colores(self, lista_hex):
        if len(lista_hex) != 5: return
        nuevos_stops: List[Tuple] = []
        pasos: List[float] = [0.00, 0.25, 0.50, 0.75, 1.00]
        for i, hex_code in enumerate(lista_hex):
            r, g, b = self._hex_to_rgb(hex_code)
            nuevos_stops.append((pasos[i], r, g, b))
        self.paleta_actual: List[Tuple] = nuevos_stops
        
        hay_cambios: bool = False
        
        for pais in self.paises:
            pob : float = pais["poblacion"]
            infectados: float = pais["infectado"] + pais["recuperado"] + pais.get("muerto", 0)
            pct: float = infectados / pob if pob > 0 else 0
            
            nuevo_color: str = self.calcular_color_hex(pct)
            pais["color"]: str = nuevo_color
            hay_cambios: bool = True
                
        if hay_cambios and self.paises:
            self.dataChanged.emit(self.index(0,0), self.index(len(self.paises)-1, 0), [self.ColorRole])
