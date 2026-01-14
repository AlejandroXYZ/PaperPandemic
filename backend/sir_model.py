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
        paciente_cero_index = opt.INDEX_PAIS_A_INFECTAR
        nombre_pais = self.df.loc[paciente_cero_index, "Country Name"]
        self.df.loc[paciente_cero_index,"S"] -= infectados_iniciales
        self.df.loc[paciente_cero_index,"I"] += infectados_iniciales
        print(f"El virus ha comenzado en: {nombre_pais}")  
        return nombre_pais

    def infectar(self,index): 
        infectados_iniciales = opt.INFECTADOS_INICIALES_VECINOS
        nombre_pais = self.df.loc[index, "Country Name"]
        self.df.loc[index,"S"] -= infectados_iniciales
        self.df.loc[index,"I"] += infectados_iniciales
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
        if not indexses[0]:
            return None
        else:
            infectados = self.df.loc[indexses]
            infectados = infectados[infectados["I"] == 0]
            lista_final = infectados.index.tolist()
            return lista_final

    
    def buscar_vuelos_y_puertos(self,columna):
        limpiar = self.df[columna].astype(str).str.lower() 
        tiene_conexion = limpiar.str.contains("accesible|océano|mar|rutas internacionales")

        # Identificar emisores
        emisores = tiene_conexion & (self.df["I"] > opt.UMBRAL_INFECCION_EXTERNO)
        num_emisores = emisores.sum()

        if num_emisores == 0:
            return [],0

        victimas = tiene_conexion & (self.df["I"] == 0)
        indice_victimas = self.df[victimas].index.tolist()
        return indice_victimas,num_emisores    


    def ejecutar(self):

        

        sano_a_infectado = self.df["beta"] * self.df["S"] * self.df["I"] / self.df["poblacion"]
        infectado_a_recuperado = self.df["I"] * self.df["gamma"]
        infectado_a_muerto = self.df["I"] * self.df["mu"]
        self.df["S"] = (self.df["S"] - sano_a_infectado)
        self.df["I"] = (self.df["I"] + sano_a_infectado - infectado_a_recuperado - infectado_a_muerto)
        self.df["R"] = (self.df["R"] + infectado_a_recuperado)
        self.df["M"] = (self.df["M"] + infectado_a_muerto)

        cols_a_redondear = ["S", "I", "R","M"]
        self.df[cols_a_redondear] = self.df[cols_a_redondear].round(2)        
        return self.df
