import pandas as pd
from dataclasses import dataclass
import sqlite3 as sql
import random
from options import Options as opt

opt = opt()


@dataclass
class SIR():
    mapa_mundo: dict = None 
    df: pd.DataFrame = None

    def infectar_primera_vez(self):
        infectados_iniciales = opt.INFECTADOS_INICIALES
        paciente_cero_index = random.randint(0,len(self.df) - 1 )
        nombre_pais = self.df.loc[paciente_cero_index, "Country Name"]
        self.df.loc[paciente_cero_index,"S"] -= infectados_iniciales
        self.df.loc[paciente_cero_index,"I"] += infectados_iniciales
        print(f"El virus ha comenzado en: {nombre_pais}")  
        return nombre_pais

    def infectar_vecinos(self,index_paises): 
        infectados_iniciales = opt.INFECTADOS_INICIALES_VECINOS
        pais = random.choice(index_paises)
        nombre_pais = self.df.loc[pais, "Country Name"]
        self.df.loc[pais,"S"] -= infectados_iniciales
        self.df.loc[pais,"I"] += infectados_iniciales
        print(f"El virus ha comenzado en {nombre_pais}")        
        return nombre_pais

    
    def buscar_vecinos(self,pais_infectado):        
        lista_paises = self.df[self.df["Country Name"] == pais_infectado]
        vecinos = list(lista_paises["vecinos"])
        paises = vecinos[0].split(",")
        indexses = []
        for i in paises:
            pais = i.strip()
            index = self.mapa_mundo.get(pais)
            indexses.append(index)
        return indexses


    
    def ejecutar(self):            
    
        sano_a_infectado = self.df["beta"] * self.df["S"] * self.df["I"] / self.df["poblacion"]
        infectado_a_recuperado = self.df["I"] * self.df["gamma"]
        self.df["S"] = (self.df["S"] - sano_a_infectado)
        self.df["I"] = (self.df["I"] + sano_a_infectado - infectado_a_recuperado)
        self.df["R"] = (self.df["R"] + infectado_a_recuperado)
        cols_a_redondear = ["S", "I", "R"]
        self.df[cols_a_redondear] = self.df[cols_a_redondear].round(2)        
        return self.df
