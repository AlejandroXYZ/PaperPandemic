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
        infectado = dataframe.loc[opt.INDEX_PAIS_A_INFECTAR, "Country Name"]
    else:
        print("Base de datos cargada")
        dataframe = csv.cargar_db()
        sir.df = dataframe
        historial = csv.historial()
        infectado = historial["Primer_pais"].iloc[0] if not historial.empty else "Desconocido"
        vecinos = sir.buscar_vecinos(infectado)
        if not vecinos:
            print("El virus está contenido, no hay vecinos sanos cerca")
        else:
            for i in vecinos:
                probabilidad_infectar_vecinos = random.random()
                if probabilidad_infectar_vecinos < opt.PROBABILIDAD_INFECTAR_VECINOS_FRONTERA:
                    sir.infectar(i)
    resultado = sir.ejecutar()
    print("guardando estados")
    csv.guardar_estados(resultado,infectado)
    print("estados guardados")
    print(f"Total de infectados:  {resultado["I"].sum()}")
    return resultado

        
avanzar_dia(dataframe)
