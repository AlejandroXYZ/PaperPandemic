from sir_model import SIR
from loader import Loader
from options import Options as opt
import sqlite3 as sql
import random


class Engine():

    def __init__(self):
        self.opt = opt()    
        self.csv = Loader(opt.RUTA_CSV)
        self.db = self.csv.crear_db()
        if self.db:            
            self.primer_pais = None
            self.dataframe = self.csv.cargar_df()
        else:
            self.dataframe = self.csv.cargar_db()
            self.historial = self.csv.historial()
            self.primer_pais = self.historial["Primer_pais"].iloc[0] if not self.historial.empty else "Desconocido"
        self.mapa = self.csv.cargar_mapa(self.dataframe)
        self.sir = SIR(mapa_mundo = self.mapa,df = self.dataframe)
    
    def avanzar_dia(self):

        if self.db and self.dataframe["I"].sum() == 0:
            print("Creando Base de datos")
            self.sir.infectar_primera_vez()
            self.primer_pais = self.dataframe.loc[opt.INDEX_PAIS_A_INFECTAR, "Country Name"]
            self.db = False 

        else:
            print("Base de datos cargada")        
            sanos_totales = self.dataframe["S"].sum()
            infectados_totales = self.dataframe["I"].sum()
            status = "Jugando"

            if sanos_totales <= 0:
                print("Todo el mundo está infectado")
                status = "Virus Gana"
            elif infectados_totales < 0:
                print("El virus se extinguió")
                status = "Humanos Ganan"

            if status != "Jugando":
                return {
                    "status": status,
                    "dia": self.historial["dia"].iloc[-1] if not self.historial.empty else "Desconocido",
                    "datos": self.dataframe.to_dict(orient="records") 
                }

        if self.primer_pais:
            vecinos = self.sir.buscar_vecinos(self.primer_pais)
            pais_infectado = self.sir.df[self.sir.df["Country Name"] == self.primer_pais]
            if pais_infectado["I"].values[0] > opt.UMBRAL_INFECCION_EXTERNO:
                if vecinos:
                    for i in vecinos:
                        probabilidad_infectar_vecinos = random.random()
                        if probabilidad_infectar_vecinos < opt.PROBABILIDAD_INFECTAR_VECINOS_FRONTERA:
                                self.sir.infectar(i)

            victimas_aereas,amenazas_aereas = self.sir.buscar_vuelos_y_puertos("vuelo")
            if amenazas_aereas > 0:
                riesgo_actual = opt.PROBABILIDAD_INFECTAR_VUELO * (1 + (amenazas_aereas * 0.1))
                riesgo_actual = min(riesgo_actual,0.5)

                for victima in victimas_aereas:
                    dado = random.random()
                    if dado < riesgo_actual:
                        self.sir.infectar(victima)
                        print(f"Contagio Aéreo, un avión infectó a {self.sir.df.at[victima,'Country Name']}")
                

            victimas_mar,amenazas_puertos = self.sir.buscar_vuelos_y_puertos("puerto")
            if amenazas_puertos > 0:
                riesgo_actual = opt.PROBABILIDAD_INFECTAR_PUERTO * (1 + (amenazas_puertos * 0.05))
                riesgo_actual = min(riesgo_actual,0.3)
                for victima in victimas_mar:
                    if random.random() < riesgo_actual:
                        self.sir.infectar(victima)            
                        print(f"Contagio marítimo, un barco a infectado a {self.sir.df.at[victima,'Country Name']}")

        resultado = self.sir.ejecutar()
        print("guardando estados")
        self.csv.guardar_estados(resultado,self.primer_pais)
        print("estados guardados")
        print(f"Total Sanos:  {resultado["S"].sum().round()}")
        print(f"Total de infectados:  {resultado["I"].sum().round()}")
        print(f"Total de Recuperados:  {resultado["R"].sum().round()}")
        print(f"Total de Muertos: {resultado["M"].sum().round()}")
        print(f"Total países infectados:  {len(self.sir.df.loc[self.sir.df["I"] > 0].index.tolist())}")


        return {
            "status": "PLAYING",
            "totales": {
            "S": int(resultado["S"].sum()),
            "I": int(resultado["I"].sum()),
            "R": int(resultado["R"].sum()),
            "M": int(resultado["M"].sum())
        },
        "datos": resultado.to_dict(orient="records")
        }


if __name__ == "__main__":
    motor = Engine()

    for i in range(10):
        motor.avanzar_dia()

