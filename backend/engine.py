from sir_model import SIR
from loader import Loader
from options import Options as opt
import sqlite3 as sql
import random


opt = opt()    
csv = Loader(opt.RUTA_CSV)
db = csv.crear_db()
conn = sql.connect(opt.RUTA_DB_CREADA)
dataframe = csv.cargar_df()  # Carga el archivo csv
mapa = csv.cargar_mapa(dataframe)
sir = SIR(mapa_mundo = mapa,df = dataframe)
    

def avanzar_dia():

    if db == False:
        print("Creando Base de datos")
        infectar = sir.infectar_primera_vez()
        infectado = dataframe.loc[opt.INDEX_PAIS_A_INFECTAR, "Country Name"]
    else:
        print("Base de datos cargada")
        df = csv.cargar_db()
        
        sanos_totales = df["S"].sum()
        infectados_totales = df["I"].sum()

        if sanos_totales <= 0:
            print("Todo el mundo está infectado")
        elif infectados_totales <= 0:
            print("El virus se extinguió")
            return {"status":"HUMAN WINS"}
        
        sir.df = df
        historial = csv.historial()
        infectado = historial["Primer_pais"].iloc[0] if not historial.empty else "Desconocido"
        vecinos = sir.buscar_vecinos(infectado)
        pais_infectado = sir.df[sir.df["Country Name"] == infectado]
        if pais_infectado["I"].values[0] > opt.UMBRAL_INFECCION_EXTERNO:
            if vecinos:
                for i in vecinos:
                    probabilidad_infectar_vecinos = random.random()
                    if probabilidad_infectar_vecinos < opt.PROBABILIDAD_INFECTAR_VECINOS_FRONTERA:
                        sir.infectar(i)

    victimas_aereas,amenazas_aereas = sir.buscar_vuelos_y_puertos("vuelo")
    if amenazas_aereas > 0:
        riesgo_actual = opt.PROBABILIDAD_INFECTAR_VUELO * (1 + (amenazas_aereas * 0.1))
        riesgo_actual = min(riesgo_actual,0.5)

        for victima in victimas_aereas:
            dado = random.random()
            if dado < riesgo_actual:
                sir.infectar(victima)
                print(f"Contagio Aéreo, un avión infectó a {sir.df.at[victima,'Country Name']}")
                

    victimas_mar,amenazas_puertos = sir.buscar_vuelos_y_puertos("puerto")
    if amenazas_puertos > 0:
        riego_actual = opt.PROBABILIDAD_INFECTAR_PUERTO * (1 + (amenazas_puertos * 0.05))
        riego_actual = min(riesgo_actual,0.3)
        for victima in victimas_mar:
            if random.random() < riesgo_actual:
                sir.infectar(victima)            
                print(f"Contagio marítimo, un barco a infectado a {sir.df.at[victima,'Country Name']}")

    resultado = sir.ejecutar()
    print("guardando estados")
    csv.guardar_estados(resultado,infectado)
    print("estados guardados")
    print(f"Total Sanos:  {resultado["S"].sum().round()}")
    print(f"Total de infectados:  {resultado["I"].sum().round()}")
    print(f"Total de Recuperados:  {resultado["R"].sum().round()}")
    print(f"Total de Muertos: {resultado["M"].sum().round()}")
    print(f"Total países infectados:  {len(sir.df.loc[sir.df["I"] > 0].index.tolist())}")
    return resultado

        
avanzar_dia()
