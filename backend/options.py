from PySide6.QtCore import QObject, Signal, Property
import os

class Options(QObject):
    # =========================================================
    # 1. CONSTANTES DE RUTA (Arreglado para carpeta 'backend')
    # =========================================================
    
    # Obtenemos la ruta absoluta de la carpeta donde está ESTE archivo (backend/)
    _BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Construimos las rutas apuntando a la carpeta 'data' dentro de 'backend'
    RUTA_DB_CREADA = os.path.join(_BACKEND_DIR, "data", "mundo.db")
    RUTA_CSV = os.path.join(_BACKEND_DIR, "data", "poblacion.csv")

    # Constantes fijas del juego
    INDEX_PAIS_A_INFECTAR = 88
    INFECTADOS_INICIALES = 2
    INFECTADOS_INICIALES_VECINOS = 11 # Mayor a umbral de erradicacion siempre
    UMBRAL_INFECCION_EXTERNO = 500
    UMBRAL_ERRADICACION = 10

    # El porcentaje de población infectada necesario para que salgan aviones/barcos (0.4 = 40%)
    UMBRAL_PCT_TRANSPORTE = 0.40 
    # Días de espera antes de poder volver a infectar por este medio
    DIAS_COOLDOWN_TRANSPORTE = 3
    UMBRAL_PCT_FRONTERA = 0.05   # 20% de infectados para cruzar a pie
    DIAS_COOLDOWN_FRONTERA = 2   # Espera entre contagios vecinales

    # =========================================================
    # 2. SEÑALES
    # =========================================================
    betaChanged = Signal(float)
    gammaChanged = Signal(float)
    muChanged = Signal(float)
    pFronteraChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Debug: Imprimimos la ruta para que verifiques en consola
        print(f"📁 BUSCANDO DATOS EN: {self.RUTA_CSV}")

        # =====================================================
        # 3. VARIABLES DINÁMICAS
        # =====================================================
        self._beta = 0.5
        self._gamma = 0.02
        self._mu = 0.005
        self._p_frontera = 1.0
        
        # Probabilidades extra
        self.PROBABILIDAD_INFECTAR_VUELO = 1.0
        self.PROBABILIDAD_INFECTAR_PUERTO = 1.0

    # --- GETTERS Y SETTERS ---
    @Property(float, notify=betaChanged)
    def beta(self): return self._beta

    @beta.setter
    def beta(self, val):
        if self._beta != val:
            self._beta = val
            self.betaChanged.emit(val)

    @Property(float, notify=gammaChanged)
    def gamma(self): return self._gamma

    @gamma.setter
    def gamma(self, val):
        if self._gamma != val:
            self._gamma = val
            self.gammaChanged.emit(val)

    @Property(float, notify=muChanged)
    def mu(self): return self._mu

    @mu.setter
    def mu(self, val):
        if self._mu != val:
            self._mu = val
            self.muChanged.emit(val)

    @Property(float, notify=pFronteraChanged)
    def p_frontera(self): return self._p_frontera

    @p_frontera.setter
    def p_frontera(self, val):
        if self._p_frontera != val:
            self._p_frontera = val
            self.pFronteraChanged.emit(val)
