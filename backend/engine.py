from backend.sir_model import SIR
from backend.loader import Loader
from backend.options import Options as opt
import sqlite3 as sql
import random
import numpy as np

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
            self.sir.infectar_primera_vez()
            self.primer_pais = self.dataframe.loc[opt.INDEX_PAIS_A_INFECTAR, "Country Name"]
            self.db = False 

        else:
            sanos_totales = self.dataframe["S"].sum()
            infectados_totales = self.dataframe["I"].sum()
            status = "Jugando"

            if sanos_totales <= 0:
                status = "Virus Gana"
            elif infectados_totales < 0:
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
                    # 1. Convertimos la lista de vecinos a un array de NumPy
                    vecinos_array = np.array(vecinos)

                    # 2. Tiramos los dados para todos los vecinos de un solo golpe
                    dados_vecinos = np.random.random(len(vecinos_array))

                    # 3. Filtramos a los vecinos que tuvieron mala suerte
                    vecinos_a_infectar = vecinos_array[dados_vecinos < opt.PROBABILIDAD_INFECTAR_VECINOS_FRONTERA]

                    # 4. Usamos la nueva función ultra-rápida
                    self.sir.infectar_multiples(vecinos_a_infectar)

            victimas_aereas, amenazas_aereas = self.sir.buscar_vuelos_y_puertos("vuelo")
            
            victimas_aereas = np.array(victimas_aereas) 

            if amenazas_aereas > 0 and len(victimas_aereas) > 0:
                riesgo_actual = opt.PROBABILIDAD_INFECTAR_VUELO * (1 + (amenazas_aereas * 0.1))
                riesgo_actual = min(riesgo_actual, 0.5)

                dados = np.random.random(len(victimas_aereas))

                infectados_aereos = victimas_aereas[dados < riesgo_actual]

                self.sir.infectar_multiples(infectados_aereos)

            victimas_mar, amenazas_puertos = self.sir.buscar_vuelos_y_puertos("puerto")
            victimas_mar = np.array(victimas_mar)

            if amenazas_puertos > 0 and len(victimas_mar) > 0:
                riesgo_actual = opt.PROBABILIDAD_INFECTAR_PUERTO * (1 + (amenazas_puertos * 0.05))
                riesgo_actual = min(riesgo_actual, 0.3)

                dados = np.random.random(len(victimas_mar))
                infectados_maritimos = victimas_mar[dados < riesgo_actual]

                self.sir.infectar_multiples(infectados_maritimos)

        resultado = self.sir.ejecutar()


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
    motor.avanzar_dia()
