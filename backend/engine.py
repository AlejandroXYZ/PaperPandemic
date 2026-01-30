from backend.sir_model import SIR
from backend.loader import Loader
import numpy as np

class Engine():

    def __init__(self, opciones_instancia):
        self.opt = opciones_instancia    
        self.csv = Loader(self.opt)
                    
        # Intentar crear/conectar DB
        # self.db devuelve True si es NUEVA, False si ya EXISTÍA
        self.db = self.csv.crear_db()
        self.dia_simulacion = 1
        self.dias_consecutivos_cero = 0 
                    
        # --- LÓGICA DE CARGA SEGURA ---
        if self.db:            
            # CASO A: Partida Nueva (Acabas de borrar la DB o es la primera vez)
            self.dataframe = self.csv.cargar_df()
                        
            # --- FIX: CREAR HISTORIAL VACÍO ---
            # Antes faltaba esta línea, por eso fallaba al decir 'object has no attribute historial'
            self.historial = self.csv.historial() 
                        
            self.primer_pais = None 
            
        else:
        # CASO B: Cargar Partida Existente (Guinea sigue viva aquí)
            self.dataframe = self.csv.cargar_db()
            self.historial = self.csv.historial()
                        
            # Recuperar día guardado
            if not self.historial.empty:
                try: self.dia_simulacion = int(self.historial.iloc[-1]["dia"])
                except: self.dia_simulacion = 1
                    
        # --- LÓGICA DE NOMBRE (Ahora ya es seguro ejecutar esto) ---
        # 1. Si hay historial (partida cargada), respetamos el país original
        if not self.historial.empty and "Primer_pais" in self.historial.columns:
            val = self.historial["Primer_pais"].iloc[0]
            self.primer_pais = val if val else "Desconocido"
        else:

            # 2. Si NO hay historial (partida nueva), usamos tu configuración de options.py
            nombre_target = self.opt.PAIS_INICIO
            # Verificamos si existe en la columna de nombres del DF
            if nombre_target in self.dataframe["Country Name"].values:
                self.primer_pais = nombre_target
            else:
                self.primer_pais = "Desconocido (Error Nombre)"
            
        # Cargar mapa y modelo...
        self.mapa = self.csv.cargar_mapa(self.dataframe)
        self.sir = SIR(mapa_mundo=self.mapa, df=self.dataframe, opt=self.opt)
                    
        # Precarga de vecinos (igual que antes)
        if self.primer_pais and self.primer_pais != "Desconocido":
            vecinos = self.sir.buscar_vecinos(self.primer_pais)
            self.indices_vecinos_zona_cero = np.array(vecinos) if vecinos else np.array([])
        else:
            self.indices_vecinos_zona_cero = np.array([])
    
    def avanzar_dia(self):
        # 1. AUMENTAR DÍA
        self.dia_simulacion += 1
        
        # Calculamos totales actuales para tomar decisiones
        infectados_totales = self.dataframe["I"].sum()
        sanos_totales = self.dataframe["S"].sum()
        historia_pandemia = self.dataframe["R"].sum() + self.dataframe["M"].sum()
        poblacion_total = sanos_totales + infectados_totales + historia_pandemia

        # =================================================================
        # 2. LÓGICA DE INICIO (Paciente Cero)
        # =================================================================
        # Si no hay infectados Y NADIE ha muerto ni se ha recuperado (Inicio virgen)
        if infectados_totales == 0 and historia_pandemia == 0:
            print("☣️ Paciente Cero detectado.")
            self.sir.infectar_primera_vez()                
            self.primer_pais = self.opt.PAIS_INICIO
                        
            self.dia_simulacion = 1
            self.db = False 
                        
            infectados_totales = self.dataframe["I"].sum()

    # =================================================================
    # 3. VERIFICAR ESTADO DEL JUEGO
    # =================================================================

        status = "Jugando"

    # Lógica de conteo de días sin virus
        if infectados_totales == 0 and historia_pandemia > 0:
            self.dias_consecutivos_cero += 1
        else:
            self.dias_consecutivos_cero = 0 # Reiniciar si alguien se infecta

    # CONDICIONES DE VICTORIA/DERROTA
        if sanos_totales <= 0 and infectados_totales <= 0:
            status = "Extinción Total" # Todos murieron
        elif self.dias_consecutivos_cero >= 3:
            status = "Virus Erradicado" # Fin normal

        
        # Si el juego terminó, devolvemos resultado final inmediatamente
        if status != "Jugando":
            return {
                "status": status,
                "dia": str(self.dia_simulacion),
                "datos": self.dataframe.to_dict(orient="records"),
                "totales": {
                    "S": int(self.dataframe["S"].sum()),
                    "I": int(self.dataframe["I"].sum()),
                    "R": int(self.dataframe["R"].sum()),
                    "M": int(self.dataframe["M"].sum())
                }
            }
            
        self.sir.procesar_fronteras_inteligente()
        self.sir.actualizar_cooldowns()
                
        if "vuelo" in self.dataframe.columns:
            self.sir.procesar_logistica(tipo_transporte="vuelo")
        
        if "puerto" in self.dataframe.columns:
            self.sir.procesar_logistica(tipo_transporte="puerto")


        # =================================================================
        # 5. MATEMÁTICAS SIRD (Pasando el día actual para la regla del día 15)
        # =================================================================
        resultado = self.sir.ejecutar(dia_actual=self.dia_simulacion)
        
        try:
            self.csv.guardar_estados(resultado, self.primer_pais)
        except Exception as e:
            print(e)
             

        return {
            "status": "PLAYING",
            "dia": str(self.dia_simulacion),
            "totales": {
                "S": int(resultado["S"].sum()),
                "I": int(resultado["I"].sum()),
                "R": int(resultado["R"].sum()),
                "M": int(resultado["M"].sum())
            },
            "datos": resultado.to_dict(orient="records")
        }



    def cheat_fin_rapido(self):
        """
        Versión BLINDADA contra números negativos.
        Usa float64 para los cálculos intermedios para evitar el límite de 32 bits.
        """
        
        # 1. Convertimos a NUMPY ARRAYS de tipo FLOAT64 (Decimales de alta precisión)
        # Esto evita que Pandas intente usar enteros de 32 bits.
        sanos = self.dataframe["S"].to_numpy(dtype=np.float64)
        infectados = self.dataframe["I"].to_numpy(dtype=np.float64)
        recuperados = self.dataframe["R"].to_numpy(dtype=np.float64)
        muertos = self.dataframe["M"].to_numpy(dtype=np.float64)

        # 2. Generamos aleatoriedad
        rng = np.random.default_rng()
        factores_suerte = rng.random(len(sanos)) # Array de 0.0 a 1.0
        
        # 3. Cálculo Seguro (Matemática de Flotantes)
        nuevos_r_float = sanos * factores_suerte
        nuevos_m_float = sanos - nuevos_r_float
        
        # 4. Convertimos a INT64 (Enteros Gigantes) explícitamente
        # np.floor redondea hacia abajo para evitar decimales sueltos
        nuevos_r = np.floor(nuevos_r_float).astype(np.int64)
        nuevos_m = np.floor(nuevos_m_float).astype(np.int64)
        
        # Sumamos los infectados a los muertos (convertidos a int64)
        nuevos_m += infectados.astype(np.int64)
        
        # 5. Escribimos de vuelta al DataFrame forzando el tipo
        self.dataframe["S"] = 0
        self.dataframe["I"] = 0
        
        # Suma final segura
        total_r = recuperados.astype(np.int64) + nuevos_r
        total_m = muertos.astype(np.int64) + nuevos_m
        
        self.dataframe["R"] = total_r
        self.dataframe["M"] = total_m
        
        # Aseguramos que las columnas en Pandas sean int64
        self.dataframe["R"] = self.dataframe["R"].astype('int64')
        self.dataframe["M"] = self.dataframe["M"].astype('int64')

        # Fin del juego
        self.dias_consecutivos_cero = 5 
        
        return self.dataframe
