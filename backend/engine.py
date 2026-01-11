from sir_model import SIR
from loader import Loader
import sqlite3 as sql
import pandas as pd

csv = Loader("data/poblacion.csv")
db = csv.crear_db()
conn = sql.connect("data/mundo.db")

dataframe = csv.cargar_df()

mapa = csv.cargar_mapa(dataframe)
sir = SIR(mapa_mundo = mapa,df = dataframe)



def avanzar_dia(dataframe):

    if db == False:
        print("Creando Base de datos")
        infectar = sir.infectar_primera_vez()
        infectado = infectar[1]
    else:
        print("Base de datos cargada")
        dataframe = csv.cargar_db()
        historial = csv.historial()
        infectado = historial["Primer_pais"].iloc[0]
    sir.infectar(infectado)
    resultado = sir.ejecutar()
    print("guardando estados")
    csv.guardar_estados(resultado,infectado)
    print("estados guardados")
    return resultado

        
avanzar_dia(dataframe)
