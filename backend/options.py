from path import rutas
from PySide6.QtCore import QObject, Signal, Property
import os
import json
from typing import Dict

class Options(QObject):
    """
    Esta Clase tiene como atributos todas las configuraciones y comportamiento del simulador SIRD

    """

    #--------------------------------------------------------------
    # Rutas    
    #--------------------------------------------------------------

    _BACKEND_DIR: str = os.path.dirname(os.path.abspath(__file__))
    RUTA_DB_CREADA: str = rutas(os.path.join("backend","data","mundo.db"))
    RUTA_CSV: str = rutas(os.path.join("backend","data","poblacion.csv"))
    
    # Archivo para guardar preferencias
    RUTA_CONFIG: str = os.path.join(_BACKEND_DIR, "data", "config.json")

     
    #-----------------------------------------------------
    # Constantes usadas para el comportamiento del Programa
    #-----------------------------------------------------
    INFECTADOS_INICIALES: int = 2
    INFECTADOS_INICIALES_VECINOS: int = 11
    UMBRAL_INFECCION_EXTERNO: int = 500
    UMBRAL_ERRADICACION: int = 10
    MAX_NOTICIAS_HISTORIAL: int = 50 
    UMBRAL_PCT_TRANSPORTE: float = 0.40 
    DIAS_COOLDOWN_TRANSPORTE: int = 3
    UMBRAL_PCT_FRONTERA: float = 0.05   
    DIAS_COOLDOWN_FRONTERA: int = 2   
    

    # ======================================================================================
    # 2. SEÑALES PARA COMUNICARSE CON QT Y QML, INDICAN A ESTOS CUANDO UNA VARIABLE CAMBIA
    # ======================================================================================
    betaChanged: Signal = Signal(float)
    gammaChanged: Signal = Signal(float)
    muChanged: Signal = Signal(float)
    pFronteraChanged: Signal = Signal(float)
    virusNombreChanged: Signal = Signal(str)
    paisInicioChanged: Signal = Signal(str)



    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        
        # Valores por defecto, puede cambiarse desde las configuraciones del programa
        self._beta: float = 0.5
        self._gamma: float = 0.02
        self._mu: float = 0.005
        self._p_frontera: float = 1.0
        self._nombre_virus: str = "Paper-20"
        self._pais_inicio: str = "Venezuela"
        
        self.PROBABILIDAD_INFECTAR_VUELO: float = 1.0
        self.PROBABILIDAD_INFECTAR_PUERTO: float = 1.0

        # CARGAR CONFIGURACIÓN GUARDADA AL INICIAR
        self.cargar_config()




    #=========================================================================
    # --- SISTEMA DE GUARDADO/CARGA ---
    #==========================================================================
    def cargar_config(self) -> None:
        """ Carga el archivo de configuración JSON que guarda las preferencias del usuario                
        """
        if os.path.exists(self.RUTA_CONFIG):
            try:
                with open(self.RUTA_CONFIG, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Solo carga si existen las claves
                    self._nombre_virus = data.get("nombre_virus", "Paper-20")
                    self._pais_inicio = data.get("pais_inicio", "Venezuela")
                    print("📂 Configuración cargada exitosamente.")
            except Exception as e:
                print(f"⚠️ Error carggando config: {e}")
                

    def guardar_config(self) -> None:
        """Guarda las preferencias del Usuario en un archivo JSON"""
        
        data: Dict[str, str] = {
            "nombre_virus": self._nombre_virus,
            "pais_inicio": self._pais_inicio
        }
        
        try:
            with open(self.RUTA_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error guardando config: {e}")



    """
        GETTERS Y SETTERS CON AUTO-GUARDADO

        Uso de Getters y Setters para mantener el control total de lo que sucede con los datos
        y también para poder disparar un Signal a QML cada vez que el valor cambia

    """

    @Property(str, notify=virusNombreChanged)
    def NOMBRE_VIRUS(self) -> str: return self._nombre_virus

    @NOMBRE_VIRUS.setter
    def NOMBRE_VIRUS(self, val) -> None:
        if self._nombre_virus != val:
            self._nombre_virus = val
            self.guardar_config() # Guarda la configuración en archivo JSON  
            self.virusNombreChanged.emit(val)

    @Property(str, notify=paisInicioChanged)
    def PAIS_INICIO(self) -> str: return self._pais_inicio

    @PAIS_INICIO.setter
    def PAIS_INICIO(self, val):
        if self._pais_inicio != val:
            self._pais_inicio = val
            self.guardar_config() # <--- Guarda al cambiar
            self.paisInicioChanged.emit(val)
            

    @Property(float, notify=betaChanged)
    def beta(self) -> float : return self._beta
    @beta.setter
    def beta(self, val):
        if self._beta != val: self._beta = val; self.betaChanged.emit(val)

    @Property(float, notify=gammaChanged)
    def gamma(self) -> float: return self._gamma
    @gamma.setter
    def gamma(self, val):
        if self._gamma != val: self._gamma = val; self.gammaChanged.emit(val)

    @Property(float, notify=muChanged)
    def mu(self) -> float: return self._mu
    @mu.setter
    def mu(self, val):
        if self._mu != val: self._mu = val; self.muChanged.emit(val)

    @Property(float, notify=pFronteraChanged)
    def p_frontera(self) -> float: return self._p_frontera
    @p_frontera.setter
    def p_frontera(self, val):
        if self._p_frontera != val: self._p_frontera = val; self.pFronteraChanged.emit(val)
