import pandas as pd
import numpy as np

class SIR:
    def __init__(self, mapa_mundo, df, opt):
        self.mapa_mundo = mapa_mundo
        self.df = df
        self.opt = opt 
        self._inicializar_cache()

    def _inicializar_cache(self):
        filtro = "accesible|océano|mar|rutas internacionales"
        self._mascara_vuelos = self.df["vuelo"].astype(str).str.lower().str.contains(filtro)
        self._mascara_puertos = self.df["puerto"].astype(str).str.lower().str.contains(filtro)

    def infectar_primera_vez(self):
        infectados_iniciales = self.opt.INFECTADOS_INICIALES
        paciente_cero_index = self.opt.INDEX_PAIS_A_INFECTAR
        
        poblacion_pais = self.df.loc[paciente_cero_index, "poblacion"]
        infectados_reales = min(infectados_iniciales, poblacion_pais)
        
        self.df.loc[paciente_cero_index,"S"] -= infectados_reales
        self.df.loc[paciente_cero_index,"I"] += infectados_reales

    def infectar_multiples(self, indices):
        if len(indices) == 0: return
        sanos_disponibles = self.df.loc[indices, "S"]
        infectados_reales = np.minimum(self.opt.INFECTADOS_INICIALES_VECINOS, sanos_disponibles)
        self.df.loc[indices, "S"] -= infectados_reales
        self.df.loc[indices, "I"] += infectados_reales

    def buscar_vecinos(self, pais_infectado): 
        lista_paises = self.df[self.df["Country Name"] == pais_infectado]
        if lista_paises.empty: return None
        vecinos = list(lista_paises["vecinos"])
        if not vecinos: return None
        paises = vecinos[0].split(",")
        indexses = []
        for i in paises:
            index = self.mapa_mundo.get(i.strip())
            if index is not None: indexses.append(index)
        if not indexses: return None
        else:
            infectados = self.df.loc[indexses]
            return infectados[infectados["I"] == 0].index.tolist()

    def buscar_vuelos_y_puertos(self, tipo):
        tiene_conexion = self._mascara_vuelos if tipo == "vuelo" else self._mascara_puertos
        emisores = tiene_conexion & (self.df["I"] > self.opt.UMBRAL_INFECCION_EXTERNO)
        if emisores.sum() == 0: return [], 0
        victimas = tiene_conexion & (self.df["I"] == 0) & (self.df["S"] > 0)
        return self.df[victimas].index.tolist(), emisores.sum()

    # =========================================================
    # FUNCIÓN EJECUTAR MODIFICADA
    # =========================================================
    def ejecutar(self, dia_actual):
        # 1. Cargar tasas base
        self.df["beta"] = self.opt.beta
        
        if dia_actual <= 4:
            self.df["gamma"] = 0.0
            self.df["mu"] = 0.0
        else:
            # A partir del día 16, usamos los valores de los sliders
            self.df["gamma"] = self.opt.gamma
            self.df["mu"] = self.opt.mu

        # ----------------------------------------------------

        # Cálculos SIRD (Vectorizado)
        sano_a_infectado = self.df["beta"] * self.df["S"] * self.df["I"] / (self.df["poblacion"] + 1)
        sano_a_infectado = sano_a_infectado.clip(upper=self.df["S"])

        infectado_a_recuperado = self.df["I"] * self.df["gamma"]
        infectado_a_muerto = self.df["I"] * self.df["mu"]

        total_salidas = infectado_a_recuperado + infectado_a_muerto
        factor = np.ones_like(self.df["I"])
        mask_exceso = total_salidas > self.df["I"]
        if mask_exceso.any():
            factor[mask_exceso] = self.df.loc[mask_exceso, "I"] / (total_salidas[mask_exceso] + 1e-9)

        infectado_a_recuperado *= factor
        infectado_a_muerto *= factor
        
        self.df["S"] -= sano_a_infectado
        self.df["I"] += (sano_a_infectado - infectado_a_recuperado - infectado_a_muerto)
        self.df["R"] += infectado_a_recuperado
        self.df["M"] += infectado_a_muerto

        # =============================================================
        # LIMPIEZA AUTOMÁTICA (Solo aplica DESPUÉS del día 15)
        # =============================================================
        if dia_actual > 15:
            tasa_salida_total = self.df["gamma"] + self.df["mu"]
            
            # Solo limpiamos si hay MENOS de 1 infectado (residuos decimales 0.005, etc)
            # Antes usabas UMBRAL_ERRADICACION (10), pero es mejor usar < 1.0 para ser precisos.
            erradicacion = (self.df["I"] > 0) & \
                           (self.df["I"] < self.opt.UMBRAL_ERRADICACION) & \
                           (tasa_salida_total > 0)

            if erradicacion.any():
                infectados_restantes = self.df.loc[erradicacion, "I"].copy()
                
                gamma_vec = self.df.loc[erradicacion, "gamma"]
                total_vec = tasa_salida_total[erradicacion]
                
                # Evitar división por cero
                prop_recuperacion = np.zeros_like(gamma_vec)
                mask_total_pos = total_vec > 0
                prop_recuperacion[mask_total_pos] = gamma_vec[mask_total_pos] / total_vec[mask_total_pos]
                
                recuperados_finales = (infectados_restantes * prop_recuperacion).round(0)
                muertes_finales = infectados_restantes - recuperados_finales

                self.df.loc[erradicacion, "M"] += muertes_finales
                self.df.loc[erradicacion, "R"] += recuperados_finales
                self.df.loc[erradicacion, "I"] = 0

        # Redondeo seguro para visualización
        cols_a_redondear = ["S", "I", "R", "M"]
        self.df[cols_a_redondear] = self.df[cols_a_redondear].clip(lower=0)        
        
        return self.df
