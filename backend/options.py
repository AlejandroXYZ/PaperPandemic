from dataclasses import dataclass

@dataclass
class Options():

    # RUTAS DE ARCHIVOS
    RUTA_CSV:str = "data/poblacion.csv"
    RUTA_DB_CREADA:str = "data/mundo.db"


    # PARÁMETROS:
    BETA: float = 1.0
    GAMMA: float = 0.0
    MU: float = 0.5
    INDEX_PAIS_A_INFECTAR: int = 88

    # OPCIONES DE INFECCIÓN DURANTE EJECUCIÓN
    PROBABILIDAD_INFECTAR_VECINOS_FRONTERA: float = 1.0
    PROBABILIDAD_INFECTAR_VUELO: float = 1.0
    PROBABILIDAD_INFECTAR_PUERTO:float = 1.0
    INFECTADOS_INICIALES: int = 8000000000
    INFECTADOS_INICIALES_VECINOS: int = 8000000000
    UMBRAL_INFECCION_EXTERNO : int = 5000
    UMBRAL_ERRADICACION: int = 30

    


