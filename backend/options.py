from dataclasses import dataclass

@dataclass
class Options():

    # RUTAS DE ARCHIVOS
    RUTA_CSV:str = "data/poblacion.csv"
    RUTA_DB_CREADA:str = "data/mundo.db"


    # PARÁMETROS:
    BETA: float = 0.3
    GAMMA: float = 0.1


    # OPCIONES DE INFECCIÓN DURANTE EJECUCIÓN
    PROBABILIDAD_INFECTAR_VECINOS_FRONTERA: float = 0.08
    INFECTADOS_INICIALES: int = 1
    INFECTADOS_INICIALES_VECINOS: int = 1
