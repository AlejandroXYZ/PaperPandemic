from sir_model import SIR
from loader import Loader
from options import Options as opt
import sqlite3 as sql
import random

opt = opt()

csv = Loader(opt.RUTA_CSV)
db = csv.crear_db()
conn = sql.connect(opt.RUTA_DB_CREADA)

dataframe = csv.cargar_df()

mapa = csv.cargar_mapa(dataframe)
sir = SIR(mapa_mundo = mapa,df = dataframe)



def avanzar_dia(dataframe):

    if db == False:
        print("Creando Base de datos")
        infectar = sir.infectar_primera_vez()
        infectado = infectar
    else:
        print("Base de datos cargada")
        dataframe = csv.cargar_db()
        historial = csv.historial()
        infectado = historial["Primer_pais"].iloc[0]
        probabilidad_infectar_vecinos = random.random()
        if probabilidad_infectar_vecinos < opt.PROBABILIDAD_INFECTAR_VECINOS_FRONTERA:
            vecinos = sir.buscar_vecinos(infectado)
            sir.infectar_vecinos(vecinos)
    resultado = sir.ejecutar()
    print("guardando estados")
    csv.guardar_estados(resultado,infectado)
    print("estados guardados")
    return resultado

        
avanzar_dia(dataframe)
