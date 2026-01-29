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

    def actualizar_cooldowns(self):
        """Resta 1 día al contador de espera de todos los países"""
        # Usamos vectorización para restar 1, pero sin bajar de 0
        self.df["cooldown_vuelo"] = np.maximum(0, self.df["cooldown_vuelo"] - 1)
        self.df["cooldown_puerto"] = np.maximum(0, self.df["cooldown_puerto"] - 1)
        self.df["cooldown_frontera"] = np.maximum(0, self.df["cooldown_frontera"] - 1)

        
    def procesar_fronteras_inteligente(self):
        """
        Lógica de contagio vecinal:
        1. Emisor > 20% Infectados.
        2. Cooldown Frontera == 0.
        3. Elige 1 vecino aleatorio disponible.
        """
        # 1. Filtramos países peligrosos (Emisores)
        poblacion_minima = 1
        pct_infectados = self.df["I"] / np.maximum(self.df["poblacion"], poblacion_minima)

        condicion_infeccion = (pct_infectados >= self.opt.UMBRAL_PCT_FRONTERA) | \
                              (self.df["I"] > self.opt.UMBRAL_INFECCION_EXTERNO)
        
        mask_emisores = (
            (pct_infectados >= self.opt.UMBRAL_PCT_FRONTERA) &
            (self.df["cooldown_frontera"] == 0) &
            (self.df["vecinos"] != "No") # Que tenga vecinos
        )
        
        indices_emisores = self.df[mask_emisores].index.tolist()
        
        if not indices_emisores: return # Nadie puede infectar hoy

        infectados_nuevos = []

        # 2. Iteramos solo sobre los países peligrosos
        for emisor_idx in indices_emisores:
            # Obtenemos la cadena de vecinos "China, Russia, Mongolia"
            vecinos_str = self.df.at[emisor_idx, "vecinos"]
            if not vecinos_str or vecinos_str == "No": continue

            lista_vecinos_nombres = [v.strip() for v in vecinos_str.split(",")]
            
            # Convertimos nombres a índices numéricos usando self.mapa_mundo
            # (Optimizacion: self.mapa_mundo es un dict {"Nombre": Indice})
            vecinos_indices = []
            for nombre in lista_vecinos_nombres:
                idx = self.mapa_mundo.get(nombre)
                if idx is None:
                    print(f"⚠️ ALERTA: No encuentro el país vecino '{nombre}' en el mapa.")
                    continue
                if idx is not None:
                    vecinos_indices.append(idx)
            
            if not vecinos_indices: continue

            # 3. Filtramos: Solo vecinos que estén SANOS (o con poca infección si quisieras)
            # Para este juego, asumiremos que atacamos a cualquiera, 
            # pero solo 'cuenta' si tiene sanos disponibles.
            vecinos_validos = [idx for idx in vecinos_indices if self.df.at[idx, "S"] > 0]
            
            if vecinos_validos:
                # 4. DADO: Elegir UNO al azar
                victima_idx = np.random.choice(vecinos_validos)
                
                # Infectamos a la víctima
                infectados_nuevos.append(victima_idx)
                
                # CASTIGO: Cooldown al emisor
                self.df.at[emisor_idx, "cooldown_frontera"] = self.opt.DIAS_COOLDOWN_FRONTERA
                
                # Debug (Opcional)
                # print(f"🚶 Frontera: {self.df.at[emisor_idx, 'Country Name']} -> {self.df.at[victima_idx, 'Country Name']}")

        # Aplicar infecciones en lote
        if infectados_nuevos:
            self.infectar_multiples(np.array(infectados_nuevos))

    def procesar_logistica(self, tipo_transporte="vuelo"):
        """
        Lógica avanzada:
        1. Emisor debe tener > 40% infectados.
        2. Emisor debe tener cooldown == 0.
        3. Elige 1 víctima al azar.
        4. Aplica cooldown al emisor.
        """
        # Seleccionar columna y cooldown correcto
        col_cooldown = "cooldown_vuelo" if tipo_transporte == "vuelo" else "cooldown_puerto"
        mascara_conexion = self._mascara_vuelos if tipo_transporte == "vuelo" else self._mascara_puertos
        
        # 1. IDENTIFICAR EMISORES (Países peligrosos)
        # Regla: Tienen conexión + Infectados > 40% + Cooldown en 0
        poblacion_minima = 1 # Evitar div por cero
        pct_infectados = self.df["I"] / np.maximum(self.df["poblacion"], poblacion_minima)
        
        # Filtro booleano vectorizado (Muy rápido)
        emisores_validos = (
            mascara_conexion & 
            (pct_infectados >= self.opt.UMBRAL_PCT_TRANSPORTE) & 
            (self.df[col_cooldown] == 0) &
            (self.df["I"] > 0)
        )
        
        indices_emisores = self.df[emisores_validos].index.tolist()
        
        if not indices_emisores:
            return # Nadie cumple los requisitos para atacar hoy

        # 2. IDENTIFICAR VÍCTIMAS POTENCIALES (Cualquiera con conexión y Sano)
        # Asumimos "Global Connection": Si tienes aeropuerto, puedes ir a cualquier aeropuerto
        victimas_validas = (
            mascara_conexion & 
            (self.df["I"] == 0) & 
            (self.df["S"] > 0)
        )
        indices_victimas = self.df[victimas_validas].index.tolist()

        if not indices_victimas:
            return # Ya no queda nadie sano con aeropuerto/puerto

        # 3. LANZAR LOS DADOS (Iteración optimizada)
        # Solo iteramos sobre los emisores, que serán pocos al inicio.
        nuevos_infectados = []
        
        # Barajamos víctimas para evitar sesgos
        np.random.shuffle(indices_victimas)
        
        for emisor_idx in indices_emisores:
            if not indices_victimas: break # Se acabaron las víctimas
            
            # Probabilidad de éxito del viaje (Opcional: añadir factor de riesgo)
            if np.random.random() < self.opt.PROBABILIDAD_INFECTAR_VUELO:
                # Tomamos una víctima y la sacamos de la lista (para que no la infecten 2 veces hoy)
                victima = indices_victimas.pop() 
                nuevos_infectados.append(victima)
                
                # CASTIGO AL EMISOR: Cooldown de 3 días
                self.df.at[emisor_idx, col_cooldown] = self.opt.DIAS_COOLDOWN_TRANSPORTE
                
                # Debug en consola (útil para verificar que funciona)
                nombre_emisor = self.df.at[emisor_idx, "Country Name"]
                nombre_victima = self.df.at[victima, "Country Name"]

        # 4. APLICAR INFECCIÓN
        if nuevos_infectados:
            self.infectar_multiples(np.array(nuevos_infectados))

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
