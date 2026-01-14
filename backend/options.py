from dataclasses import dataclass

@dataclass
class Options():

    # RUTAS DE ARCHIVOS
    RUTA_CSV:str = "data/poblacion.csv"
    RUTA_DB_CREADA:str = "data/mundo.db"


    # PARÁMETROS:
    BETA: float = 0.3
    GAMMA: float = 0.1
    INDEX_PAIS_A_INFECTAR: int = 88

    # OPCIONES DE INFECCIÓN DURANTE EJECUCIÓN
    PROBABILIDAD_INFECTAR_VECINOS_FRONTERA: float = 0.3
    PROBABILIDAD_INFECTAR_VUELO: float = 0.0005
    PROBABILIDAD_INFECTAR_PUERTO:float = 0.0001
    INFECTADOS_INICIALES: int = 400
    INFECTADOS_INICIALES_VECINOS: int = 1
    UMBRAL_INFECCION_EXTERNO : int = 500
    
