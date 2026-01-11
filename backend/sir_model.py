import pandas as pd
from dataclasses import dataclass
import sqlite3 as sql
import random

@dataclass
class SIR():
    mapa_mundo: dict = None 
    df: pd.DataFrame = None

    def infectar_primera_vez(self):
        infectados_iniciales = 1
        paciente_cero_index = random.randint(0,len(self.df) - 1 )
        nombre_pais = self.df.loc[paciente_cero_index, "Country Name"]
        self.df.loc[paciente_cero_index,"S"] -= infectados_iniciales
        self.df.loc[paciente_cero_index,"I"] += infectados_iniciales
        print(f"El virus ha comenzado en {nombre_pais}")        
        return [paciente_cero_index,nombre_pais]

    
    def infectar(self,pais_infectado):        
        lista_paises = self.df[self.df["Country Name"] == pais_infectado]
        vecinos = lista_paises["vecinos"]
        print(vecinos)


    
    def ejecutar(self):            
    
        sano_a_infectado = self.df["beta"] * self.df["S"] * self.df["I"] / self.df["poblacion"]
        infectado_a_recuperado = self.df["I"] * self.df["gamma"]
        self.df["S"] = (self.df["S"] - sano_a_infectado)
        self.df["I"] = (self.df["I"] + sano_a_infectado - infectado_a_recuperado)
        self.df["R"] = (self.df["R"] + infectado_a_recuperado)
        cols_a_redondear = ["S", "I", "R"]
        self.df[cols_a_redondear] = self.df[cols_a_redondear].round(2)        
        return self.df
