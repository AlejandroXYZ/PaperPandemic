from backend.sir_model import SIR
from backend.loader import Loader
import numpy as np

class Engine():

    def __init__(self, opciones_instancia):
        self.opt = opciones_instancia    
        self.csv = Loader(self.opt)
        
        # Intentar crear/conectar DB
        self.db = self.csv.crear_db()
        
        # --- NUEVO: CONTADOR DE DÍAS INTERNO ---
        self.dia_simulacion = 1 
        
        if self.db:            
            self.primer_pais = None
            self.dataframe = self.csv.cargar_df()
        else:
            self.dataframe = self.csv.cargar_db()
            self.historial = self.csv.historial()
            
            # Si cargamos partida, intentamos recuperar el día donde nos quedamos
            if not self.historial.empty:
                try:
                    self.dia_simulacion = int(self.historial.iloc[-1]["dia"])
                except:
                    self.dia_simulacion = 1

            if not self.historial.empty and "Primer_pais" in self.historial.columns:
                self.primer_pais = self.historial["Primer_pais"].iloc[0]
            else:
                self.primer_pais = "Desconocido"

        self.mapa = self.csv.cargar_mapa(self.dataframe)
        self.sir = SIR(mapa_mundo=self.mapa, df=self.dataframe, opt=self.opt)
        
        # Precarga de vecinos del paciente cero (Optimización)
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
            
            pais_idx = self.opt.INDEX_PAIS_A_INFECTAR
            if pais_idx in self.dataframe.index:
                self.primer_pais = self.dataframe.loc[pais_idx, "Country Name"]
            else:
                self.primer_pais = "Desconocido"
            
            # Reiniciar día si empezamos de cero
            self.dia_simulacion = 1
            self.db = False 
            
            # Recalculamos para que el status no dé "Humanos Ganan" en este mismo tick
            infectados_totales = self.dataframe["I"].sum()

        # =================================================================
        # 3. VERIFICAR ESTADO DEL JUEGO
        # =================================================================
        status = "Jugando"

        if poblacion_total == 0:
            status = "Cargando..."
        elif sanos_totales <= 0:
            status = "Virus Gana"
        elif infectados_totales <= 0 and historia_pandemia > 0:
            # Solo ganan los humanos si hubo virus alguna vez y se extinguió
            status = "Humanos Ganan"

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
        except:
            pass 

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
