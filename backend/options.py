from PySide6.QtCore import QObject, Signal, Property
import os
import json

class Options(QObject):
    # =========================================================
    # 1. CONSTANTES Y RUTAS
    # =========================================================
    _BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    RUTA_DB_CREADA = os.path.join(_BACKEND_DIR, "data", "mundo.db")
    RUTA_CSV = os.path.join(_BACKEND_DIR, "data", "poblacion.csv")
    
    # NUEVO: Archivo para guardar tus preferencias
    RUTA_CONFIG = os.path.join(_BACKEND_DIR, "data", "config.json")

    # Constantes fijas de juego
    INFECTADOS_INICIALES = 2
    INFECTADOS_INICIALES_VECINOS = 11
    UMBRAL_INFECCION_EXTERNO = 500
    UMBRAL_ERRADICACION = 10
    MAX_NOTICIAS_HISTORIAL = 50 
    UMBRAL_PCT_TRANSPORTE = 0.40 
    DIAS_COOLDOWN_TRANSPORTE = 3
    UMBRAL_PCT_FRONTERA = 0.05   
    DIAS_COOLDOWN_FRONTERA = 2   

    # =========================================================
    # 2. SEÑALES
    # =========================================================
    betaChanged = Signal(float)
    gammaChanged = Signal(float)
    muChanged = Signal(float)
    pFronteraChanged = Signal(float)
    virusNombreChanged = Signal(str)
    paisInicioChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Valores por defecto
        self._beta = 0.5
        self._gamma = 0.02
        self._mu = 0.005
        self._p_frontera = 1.0
        self._nombre_virus = "Paper-20"
        self._pais_inicio = "Venezuela"
        
        self.PROBABILIDAD_INFECTAR_VUELO = 1.0
        self.PROBABILIDAD_INFECTAR_PUERTO = 1.0

        # CARGAR CONFIGURACIÓN GUARDADA AL INICIAR
        self.cargar_config()

    # --- SISTEMA DE GUARDADO/CARGA (NUEVO) ---
    def cargar_config(self):
        if os.path.exists(self.RUTA_CONFIG):
            try:
                with open(self.RUTA_CONFIG, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Solo cargamos si existen las claves
                    self._nombre_virus = data.get("nombre_virus", "Paper-20")
                    self._pais_inicio = data.get("pais_inicio", "Venezuela")
                    print("📂 Configuración cargada exitosamente.")
            except Exception as e:
                print(f"⚠️ Error cargando config: {e}")

    def guardar_config(self):
        data = {
            "nombre_virus": self._nombre_virus,
            "pais_inicio": self._pais_inicio
        }
        try:
            with open(self.RUTA_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error guardando config: {e}")

    # --- GETTERS Y SETTERS CON AUTO-GUARDADO ---

    @Property(str, notify=virusNombreChanged)
    def NOMBRE_VIRUS(self): return self._nombre_virus

    @NOMBRE_VIRUS.setter
    def NOMBRE_VIRUS(self, val):
        if self._nombre_virus != val:
            self._nombre_virus = val
            self.guardar_config() # <--- Guardamos al cambiar
            self.virusNombreChanged.emit(val)

    @Property(str, notify=paisInicioChanged)
    def PAIS_INICIO(self): return self._pais_inicio

    @PAIS_INICIO.setter
    def PAIS_INICIO(self, val):
        if self._pais_inicio != val:
            self._pais_inicio = val
            self.guardar_config() # <--- Guardamos al cambiar
            self.paisInicioChanged.emit(val)

    # (El resto de propiedades numéricas se mantienen igual, 
    #  puedes agregarlas al save_config si quieres que también se guarden)
    @Property(float, notify=betaChanged)
    def beta(self): return self._beta
    @beta.setter
    def beta(self, val):
        if self._beta != val: self._beta = val; self.betaChanged.emit(val)

    @Property(float, notify=gammaChanged)
    def gamma(self): return self._gamma
    @gamma.setter
    def gamma(self, val):
        if self._gamma != val: self._gamma = val; self.gammaChanged.emit(val)

    @Property(float, notify=muChanged)
    def mu(self): return self._mu
    @mu.setter
    def mu(self, val):
        if self._mu != val: self._mu = val; self.muChanged.emit(val)

    @Property(float, notify=pFronteraChanged)
    def p_frontera(self): return self._p_frontera
    @p_frontera.setter
    def p_frontera(self, val):
        if self._p_frontera != val: self._p_frontera = val; self.pFronteraChanged.emit(val)
