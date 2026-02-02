import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class SIR:
    """
    Modelo SIRD(Susceptibles,Infectados,Recuperdos y Fallecidos/Deceased)
    esta clase contiene toda la lógica matemática para que este modelo sea altamente realista
    """

    def __init__(self, mapa_mundo, df, opt) -> None:
        self.mapa_mundo: pd.Dataframe = mapa_mundo
        self.df: pd.Dataframe = df
        self.opt = opt         
        filtro = "accesible|océano|mar|rutas internacionales"
        self._mascara_vuelos: pd.Series = self.df["vuelo"].astype(str).str.lower().str.contains(filtro)
        self._mascara_puertos: pd.Series = self.df["puerto"].astype(str).str.lower().str.contains(filtro)


    def infectar_primera_vez(self):
        """Inicia la infección del virus """
        
        infectados_iniciales: str = self.opt.INFECTADOS_INICIALES
        
        nombre_objetivo: str = self.opt.PAIS_INICIO
        
        # Busca el índice en el mapa
        paciente_cero_index: int|None = self.mapa_mundo.get(nombre_objetivo)
        
        if paciente_cero_index is None:
            print(f"⚠️ ERROR CRÍTICO: No encuentro el país '{nombre_objetivo}' en la base de datos.")
            print("➡️ Usando el primer país de la lista como fallback.")
            paciente_cero_index: str = self.df.index[0]
            # Actualiza el nombre en opciones para que la UI lo sepa
            self.opt.PAIS_INICIO: str = self.df.at[paciente_cero_index, "Country Name"]
        
        poblacion_pais: float = self.df.loc[paciente_cero_index, "poblacion"]
        infectados_reales: float = min(infectados_iniciales, poblacion_pais)
        
        self.df.loc[paciente_cero_index,"S"] -= infectados_reales
        self.df.loc[paciente_cero_index,"I"] += infectados_reales
        



    def actualizar_cooldowns(self):
        """Resta 1 día al contador de espera de todos los países para evitar que un país contagie
            demasiado rápido
        """
        
        # Uso de vectorización para restar 1, pero sin bajar de 0
        self.df["cooldown_vuelo"]: pd.Series = np.maximum(0, self.df["cooldown_vuelo"] - 1)
        self.df["cooldown_puerto"]: pd.Series = np.maximum(0, self.df["cooldown_puerto"] - 1)
        self.df["cooldown_frontera"]: pd.Series = np.maximum(0, self.df["cooldown_frontera"] - 1)


        
    def procesar_fronteras_inteligente(self) -> None:
        """
        Lógica de contagio vecinal:
        1. Emisor > 20% Infectados.
        2. Cooldown Frontera == 0.
        3. Elige 1 vecino aleatorio disponible.
        """
        
        # 1. Filtra países peligrosos (Emisores)
        poblacion_minima: int = 1
        pct_infectados: pd.Series = self.df["I"] / np.maximum(self.df["poblacion"], poblacion_minima)

        condicion_infeccion = (pct_infectados >= self.opt.UMBRAL_PCT_FRONTERA) | \
                              (self.df["I"] > self.opt.UMBRAL_INFECCION_EXTERNO)
        
        mask_emisores: pd.Series = (
            (pct_infectados >= self.opt.UMBRAL_PCT_FRONTERA) &
            (self.df["cooldown_frontera"] == 0) &
            (self.df["vecinos"] != "No") # Que tenga vecinos
        )
        
        indices_emisores: List[int]|None = self.df[mask_emisores].index.tolist()
        
        if not indices_emisores: return # Nadie puede infectar hoy

        infectados_nuevos: List = []

        # 2. Itera solo sobre los países peligrosos
        for emisor_idx in indices_emisores:
            # Obteniene la cadena de vecinos "China, Russia, Mongolia"
            vecinos_str: str = self.df.at[emisor_idx, "vecinos"]
            if not vecinos_str or vecinos_str == "No": continue

            lista_vecinos_nombres: List[str] = [v.strip() for v in vecinos_str.split(",")]
            
            # Convertimos nombres a índices numéricos usando self.mapa_mundo
            vecinos_indices: List[int] = []
            
            for nombre in lista_vecinos_nombres:
            
                 # Ignorar si dice "Ninguno" o "No"
                 if "Ninguno" in nombre or nombre == "No": continue
                 
                 idx: int|None = self.mapa_mundo.get(nombre)
                 if idx is None:
                    continue
                 
                 vecinos_indices.append(idx)
            
            if not vecinos_indices: continue

            # Filtra Solo vecinos que estén SANOS
            vecinos_validos = [idx for idx in vecinos_indices if self.df.at[idx, "S"] > 0]
            
            if vecinos_validos:
                # 4. DADO: Elegir UNO al azar
                victima_idx: int = np.random.choice(vecinos_validos)
                
                # Infectamos a la víctima
                infectados_nuevos.append(victima_idx)
                
                # Cooldown al emisor
                self.df.at[emisor_idx, "cooldown_frontera"] = self.opt.DIAS_COOLDOWN_FRONTERA
                

        # Aplicar infecciones en lote
        if infectados_nuevos:
            self.infectar_multiples(np.array(infectados_nuevos))

            

    def procesar_logistica(self, tipo_transporte: str = "vuelo" ) -> None :
        """
        Lógica avanzada:
        1. Emisor debe tener > 40% infectados.
        2. Emisor debe tener cooldown == 0.
        3. Elige 1 víctima al azar.
        4. Aplica cooldown al emisor.
        """
        
        # Seleccionar columna y cooldown correcto
        col_cooldown:str = "cooldown_vuelo" if tipo_transporte == "vuelo" else "cooldown_puerto"
        mascara_conexion:str = self._mascara_vuelos if tipo_transporte == "vuelo" else self._mascara_puertos
        
        # IDENTIFICAR EMISORES (Países peligrosos)
        # Regla: Tienen conexión + Infectados > 40% + Cooldown en 0
        poblacion_minima: int = 1 # Evitar división por cero
        pct_infectados: pd.Series = self.df["I"] / np.maximum(self.df["poblacion"], poblacion_minima)
        
        # Filtro booleano vectorizado
        emisores_validos: pd.Dataframe = (
            mascara_conexion & 
            (pct_infectados >= self.opt.UMBRAL_PCT_TRANSPORTE) & 
            (self.df[col_cooldown] == 0) &
            (self.df["I"] > 0)
        )
        
        indices_emisores: List[int]|None = self.df[emisores_validos].index.tolist()
        
        if not indices_emisores:
            return # Nadie cumple los requisitos para atacar hoy

        # IDENTIFICAR VÍCTIMAS POTENCIALES (Cualquiera con conexión y Sano)
        # Asume "Global Connection": Si tienes aeropuerto, puedes ir a cualquier aeropuerto
        victimas_validas: pd.Series = (
            mascara_conexion & 
            (self.df["I"] == 0) & 
            (self.df["S"] > 0)
        )
        
        indices_victimas: List[int]|None = self.df[victimas_validas].index.tolist()

        if not indices_victimas:
            return # Ya no queda nadie sano con aeropuerto/puerto

        # LANZAR LOS DADOS 
        # Solo iteramos sobre los emisores, que serán pocos al inicio.
        nuevos_infectados: List[int] = []
        
        # Baraja víctimas para evitar sesgos
        np.random.shuffle(indices_victimas)
        
        for emisor_idx in indices_emisores:
            if not indices_victimas: break # Se acabaron las víctimas
            
            # Probabilidad de éxito del viaje
            if np.random.random() < self.opt.PROBABILIDAD_INFECTAR_VUELO:
                # Tomamos una víctima y la sacamos de la lista para que no la infecten 2 veces en un día
                victima: int = indices_victimas.pop() 
                nuevos_infectados.append(victima)
                
                # Cooldown de 3 días
                self.df.at[emisor_idx, col_cooldown] = self.opt.DIAS_COOLDOWN_TRANSPORTE
                

                nombre_emisor: str = self.df.at[emisor_idx, "Country Name"]
                nombre_victima: str = self.df.at[victima, "Country Name"]

        # APLICAR INFECCIÓN
        if nuevos_infectados:
            self.infectar_multiples(np.array(nuevos_infectados))

            

    def infectar_multiples(self, indices: np.NDArray) -> None:
        """
            Infectar a múltiples países a la vez usando numpy para que sea instantáneo
        """
        if len(indices) == 0: return
        sanos_disponibles: pd.Series = self.df.loc[indices, "S"]
        infectados_reales: np.NDArray = np.minimum(self.opt.INFECTADOS_INICIALES_VECINOS, sanos_disponibles)
        self.df.loc[indices, "S"] -= infectados_reales
        self.df.loc[indices, "I"] += infectados_reales

        

    def buscar_vecinos(self, pais_infectado: str) -> List:
        """
            Función para detectar cuales son los vecinos de un país específico

            Args:
                pais_infectado: Nombre del país infectado
        """
        
        lista_paises: pd.Series = self.df[self.df["Country Name"] == pais_infectado]
        if lista_paises.empty: return None
        vecinos: List[str]|None = list(lista_paises["vecinos"])
        if not vecinos: return None
        paises: List[str]|None = vecinos[0].split(",")
        indexses: List[int]|None = []
        for i in paises:
            index = self.mapa_mundo.get(i.strip())
            if index is not None: indexses.append(index)
        if not indexses: return None
        else:
            infectados: pd.Dataframe = self.df.loc[indexses]
            return infectados[infectados["I"] == 0].index.tolist()


    def ejecutar(self, dia_actual: str) -> pd.Dataframe:
        """
            Método Principal de la clase, realiza toda la lógica matemática para la infección
        """
        
        # Carga tasas base
        self.df["beta"]: pd.Series = self.opt.beta
        
        if dia_actual <= 4:
            self.df["gamma"]: pd.Series = 0.0
            self.df["mu"]: pd.Series = 0.0
        else:
            # A partir del día 16, usamos los valores de los sliders para evitar que la infección
            # se extinga antes de tiempo
            self.df["gamma"]: pd.Series = self.opt.gamma
            self.df["mu"] :pd.Series = self.opt.mu

        # ----------------------------------------------------

        # Cálculos SIRD Vectorizados
        sano_a_infectado: pd.Series = self.df["beta"] * self.df["S"] * self.df["I"] / (self.df["poblacion"] + 1)
        sano_a_infectado: pd.Series = sano_a_infectado.clip(upper=self.df["S"])

        infectado_a_recuperado: pd.Series = self.df["I"] * self.df["gamma"]
        infectado_a_muerto: pd.Series = self.df["I"] * self.df["mu"]

        total_salidas: pd.Series = infectado_a_recuperado + infectado_a_muerto
        factor: np.NDArray = np.ones_like(self.df["I"])
        mask_exceso: pd.Series = total_salidas > self.df["I"]
        if mask_exceso.any():
            factor[mask_exceso]: pd.Series = self.df.loc[mask_exceso, "I"] / (total_salidas[mask_exceso] + 1e-9)

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
            tasa_salida_total: pd.Series = self.df["gamma"] + self.df["mu"]
            
            # Solo limpia si hay MENOS de 1 infectado (residuos decimales 0.005, etc)
            erradicacion: pd.Series = (self.df["I"] > 0) & \
                           (self.df["I"] < self.opt.UMBRAL_ERRADICACION) & \
                           (tasa_salida_total > 0)

            if erradicacion.any():
                infectados_restantes: pd.Series|pd.Dataframe = self.df.loc[erradicacion, "I"].copy()
                
                gamma_vec: pd.Series = self.df.loc[erradicacion, "gamma"]
                total_vec: pd.Series = tasa_salida_total[erradicacion]
                
                # Evitar división por cero
                prop_recuperacion: np.NDArray = np.zeros_like(gamma_vec)
                mask_total_pos: pd.Series = total_vec > 0
                prop_recuperacion[mask_total_pos]: pd.Series = gamma_vec[mask_total_pos] / total_vec[mask_total_pos]
                
                recuperados_finales: pd.Series = (infectados_restantes * prop_recuperacion).round(0)
                muertes_finales: pd.Series = infectados_restantes - recuperados_finales

                self.df.loc[erradicacion, "M"] += muertes_finales
                self.df.loc[erradicacion, "R"] += recuperados_finales
                self.df.loc[erradicacion, "I"]: pd.Series = 0

        # Redondeo seguro para visualización
        cols_a_redondear: List[str] = ["S", "I", "R", "M"]
        self.df[cols_a_redondear]: pd.Dataframe = self.df[cols_a_redondear].clip(lower=0)        
        
        return self.df
