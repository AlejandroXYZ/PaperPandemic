import pandas as pd
import pandas as pd
import numpy as np # <-- IMPORTANTE: Agregamos NumPy
from dataclasses import dataclass
import sqlite3 as sql
import random
from backend.options import Options as opt

opt = opt()

@dataclass
class SIR():
    mapa_mundo: dict = None 
    df: pd.DataFrame = None

    # ==========================================================
    # NUEVO: CACHÉ DE DATOS ESTÁTICOS (Se ejecuta 1 sola vez)
    # ==========================================================
    def __post_init__(self):
        # Cacheamos qué países tienen puerto o vuelo para NO buscar texto nunca más.
        # Esto ahorra un 90% del tiempo de búsqueda en cada día.
        filtro = "accesible|océano|mar|rutas internacionales"
        self._mascara_vuelos = self.df["vuelo"].astype(str).str.lower().str.contains(filtro)
        self._mascara_puertos = self.df["puerto"].astype(str).str.lower().str.contains(filtro)

    def infectar_primera_vez(self):
        infectados_iniciales = opt.INFECTADOS_INICIALES
        paciente_cero_index = opt.INDEX_PAIS_A_INFECTAR
        poblacion_pais = self.df.loc[paciente_cero_index, "poblacion"]
        infectados_reales = min(infectados_iniciales, poblacion_pais)
        nombre_pais = self.df.loc[paciente_cero_index, "Country Name"]
        self.df.loc[paciente_cero_index,"S"] -= infectados_reales
        self.df.loc[paciente_cero_index,"I"] += infectados_reales
        return nombre_pais

    # ==========================================================
    # NUEVA FUNCIÓN VECTORIZADA (Reemplaza a infectar_uno_por_uno)
    # ==========================================================
    def infectar_multiples(self, indices):
        """Infecta a múltiples países AL MISMO TIEMPO con una sola operación Pandas"""
        if len(indices) == 0:
            return

        # 1. Obtenemos los sanos de TODOS los países víctimas de golpe
        sanos_disponibles = self.df.loc[indices, "S"]

        # 2. Calculamos los infectados reales para todos (vectorizado)
        # np.minimum es mágico: compara 20 números al mismo tiempo
        infectados_reales = np.minimum(opt.INFECTADOS_INICIALES_VECINOS, sanos_disponibles)

        # 3. Restamos y sumamos a TODOS los países en una sola línea (0.01 ms)
        self.df.loc[indices, "S"] -= infectados_reales
        self.df.loc[indices, "I"] += infectados_reales

    def buscar_vecinos(self,pais_infectado): 
        # (Esta función también se podría optimizar pre-calculando, 
        # pero por ahora no es el cuello de botella principal)
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

    # ==========================================================
    # BUSCADOR OPTIMIZADO (Usa las máscaras cacheadas)
    # ==========================================================
    def buscar_vuelos_y_puertos(self, tipo):
        # Usamos la máscara que ya calculamos en el día 0
        tiene_conexion = self._mascara_vuelos if tipo == "vuelo" else self._mascara_puertos

        # Identificar emisores (Países que ya son un peligro)
        emisores = tiene_conexion & (self.df["I"] > opt.UMBRAL_INFECCION_EXTERNO)
        num_emisores = emisores.sum()

        if num_emisores == 0:
            return [], 0

        # Identificar víctimas (Países vírgenes que reciben vuelos/barcos)
        victimas = tiene_conexion & (self.df["I"] == 0) & (self.df["S"] > 0)
        indice_victimas = self.df[victimas].index.tolist()

        return indice_victimas, num_emisores

    def ejecutar(self):

        sano_a_infectado = self.df["beta"] * self.df["S"] * self.df["I"] / (self.df["poblacion"] + 1) # Se suma 1 para evitar que python explote si llega a 0
        sano_a_infectado = sano_a_infectado.clip(upper=self.df["S"])

        infectado_a_recuperado = self.df["I"] * self.df["gamma"]
        infectado_a_muerto = self.df["I"] * self.df["mu"]

        total_salidas = infectado_a_recuperado + infectado_a_muerto

        factor = (self.df["I"] / (total_salidas + 1)).clip(upper=1.0)
        infectado_a_recuperado *= factor
        infectado_a_muerto *= factor
        
        self.df["S"] = (self.df["S"] - sano_a_infectado)
        self.df["I"] = (self.df["I"] + sano_a_infectado - infectado_a_recuperado - infectado_a_muerto)
        self.df["R"] = (self.df["R"] + infectado_a_recuperado)
        self.df["M"] = (self.df["M"] + infectado_a_muerto)

        # Erradicación

        erradicacion = (self.df["I"] > 0) & (self.df["S"] < opt.UMBRAL_ERRADICACION)

        if erradicacion.any():
            infectados_restantes = self.df.loc[erradicacion, "I"]

            total_tasa = self.df.loc[erradicacion, "gamma"] + self.df.loc[erradicacion, "mu"]
            total_tasa = total_tasa.replace(0, 1.0)             
            fraccion_muertes = self.df.loc[erradicacion, "mu"] / total_tasa
            muertes_finales = (infectados_restantes * fraccion_muertes).round(0)
            recuperados_finales = infectados_restantes - muertes_finales

            self.df.loc[erradicacion, "M"] += muertes_finales
            self.df.loc[erradicacion, "R"] += recuperados_finales
            self.df.loc[erradicacion, "I"] = 0

        cols_a_redondear = ["S", "I", "R","M"]
        self.df[cols_a_redondear] = self.df[cols_a_redondear].clip(lower=0)        
        return self.df
