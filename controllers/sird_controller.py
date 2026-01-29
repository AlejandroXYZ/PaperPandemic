from PySide6.QtCore import QObject, Slot, Signal, Property, QTimer
from backend.engine import Engine
from controllers.mapa_modelo import MapaModeloSIRD
from backend.options import Options

class ControladorSIRD(QObject):
    # Señales
    datosCambios = Signal()
    noticiaCambio = Signal(str)
    statsChanged = Signal() 
    diaChanged = Signal(str) 


    def __init__(self):
        super().__init__()
        
        # 1. Inicializar objetos
        self.opciones = Options()
        self.mapa_modelo = MapaModeloSIRD()
        self.motor = Engine(self.opciones) # Pasamos opciones al motor

        # 2. Variables de estado
        self._dia = "1"
        self._sanos = 0
        self._infectados = 0
        self._recuperados = 0
        self._muertos = 0
        self._paisesInfectados = 0
        self._primerPais = "Esperando..."
        self._noticia = "Preparado. Pulsa Play."
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick_simulacion)
        self.isPlaying = False
        self._intervalo_ms = 1000

        # 3. ¡IMPORTANTE! Cargar datos iniciales (para no ver ceros)
        # Ejecutamos una actualización manual sin avanzar el tiempo
        self.actualizar_interfaz_desde_motor()

    @Property(QObject, constant=True)
    def config(self):
        return self.opciones

    @Property(float, notify=statsChanged)
    def sanos(self): return float(self._sanos)

    @Property(float, notify=statsChanged)
    def infectados(self): return float(self._infectados)

    @Property(float, notify=statsChanged)
    def recuperados(self): return float(self._recuperados)

    @Property(float, notify=statsChanged)
    def muertos(self): return float(self._muertos)
    
    # Este puede quedarse en int porque nunca habrá más de 200 países
    @Property(int, notify=statsChanged)
    def paisesInfectados(self): return self._paisesInfectados

    @Property(str, notify=statsChanged)
    def primerPais(self): return self._primerPais

    @Property(str, notify=diaChanged)
    def dia(self): return str(self._dia)

    @Property(str, notify=noticiaCambio)
    def noticia(self): return self._noticia


    @Slot(float)
    def cambiar_velocidad(self, valor):
        """
        Recibe valor del slider (0.0 a 2.0)
        Convierte a milisegundos (4000ms a 200ms)
        """
        # TUS LÍMITES
        ms_min = 200     # Lo más rápido (límite del hardware)
        ms_max = 4000    # Lo más lento
        slider_max = 2.0 # El valor 'maximo' que pusiste en el QML

        # 1. Normalizamos: Convertimos el 0..2.0 a 0..1.0
        # Ejemplo: si entra 2.0, factor será 1.0. Si entra 1.0, factor será 0.5
        factor = valor / slider_max 
        
        # 2. Interpolación Lineal Inversa
        # Intervalo = Inicio + (Fin - Inicio) * factor
        # Pero como queremos ir de Mayor a Menor, restamos:
        rango = ms_max - ms_min
        nuevo_intervalo = int(ms_max - (factor * rango))
        
        # 3. Seguridad: Nunca bajar del mínimo del hardware
        nuevo_intervalo = max(ms_min, nuevo_intervalo)
        
        self._intervalo_ms = nuevo_intervalo
        
        # Debug para verificar
        print(f"🏎️ Slider: {valor:.2f} -> Intervalo Real: {self._intervalo_ms} ms")

        # Aplicar inmediatamente si está corriendo
        if self.isPlaying:
            self.timer.setInterval(self._intervalo_ms)

    # --- LÓGICA ---
    @Slot(bool)
    def toggle_simulacion(self, encendido):
        self.isPlaying = encendido
        if encendido:
            print("▶️ Iniciando Timer...")
            self.timer.start(self._intervalo_ms)
        else:
            print("⏸️ Pausando Timer...")
            self.timer.stop()

    @Slot()
    def pausar_simulacion(self):
        self.toggle_simulacion(False)

    @Slot()
    def reiniciar_simulacion(self):
        self.reiniciar()

    @Slot()
    def reiniciar(self):
        print("⟲ Reiniciando...")
        self.timer.stop()
        self.isPlaying = False

        # Limpiar
        if hasattr(self, 'motor'):
            try: self.motor.csv.limpiar_db()
            except: pass

        self.mapa_modelo._inicializar_vacio()
        self.motor = Engine(self.opciones) # Motor nuevo con opciones

        self._noticia = "Simulación Reiniciada."
        
        # Cargar estado inicial limpio
        self.actualizar_interfaz_desde_motor()

    def tick_simulacion(self):
        if not self.isPlaying: return
        
        # Avanzar lógica
        resultado = self.motor.avanzar_dia()
        self.procesar_resultado(resultado)

    def actualizar_interfaz_desde_motor(self):
        """Lee el estado actual del motor SIN avanzar el día"""
        # Forzamos una lectura del estado actual del dataframe
        if hasattr(self.motor, 'dataframe'):
             # Construimos un 'resultado' falso solo para actualizar la UI
             df = self.motor.dataframe
             nombre = getattr(self.motor, 'primer_pais', "Desconocido")

             
             if not nombre or nombre == "Desconocido":
                 # INTENTO DE RESCATE: Si el motor no sabe, miramos si alguien tiene infectados
                 infectados = df[df["I"] > 0]
                 if not infectados.empty:
                     nombre = infectados.iloc[0]["Country Name"]
                 else:
                     # Si nadie está infectado aún (Día 0), predecimos quién será
                     idx_target = self.opciones.INDEX_PAIS_A_INFECTAR
                     if idx_target in df.index:
                         nombre = df.loc[idx_target, "Country Name"]
                         
             self._primerPais = str(nombre) if nombre else "Desconocido"
             
             totales = {
                 "S": int(df["S"].sum()),
                 "I": int(df["I"].sum()),
                 "R": int(df["R"].sum()),
                 "M": int(df["M"].sum())
             }
             # Actualizamos variables
             self._sanos = totales["S"]
             self._infectados = totales["I"]
             self._recuperados = totales["R"]
             self._muertos = totales["M"]
             self._dia = "1"
             self.statsChanged.emit()
             self.diaChanged.emit(self._dia)
             self.noticiaCambio.emit(self._noticia)
             
             # Actualizar colores iniciales
             self.mapa_modelo.actualizar_datos(df.to_dict(orient="records"))

    def procesar_resultado(self, resultado):
        status = resultado.get("status", "Jugando")
        
        datos = resultado.get("datos", [])
        if datos: self.mapa_modelo.actualizar_datos(datos)

        totales = resultado.get("totales", {})
        if totales:
            self._sanos = int(totales.get("S", 0))
            self._infectados = int(totales.get("I", 0))
            self._recuperados = int(totales.get("R", 0))
            self._muertos = int(totales.get("M", 0))

        self._dia = str(resultado.get("dia", self._dia))
        self._paisesInfectados = sum(1 for p in datos if p.get("I", 0) > 0)

        self.statsChanged.emit()
        self.diaChanged.emit(self._dia)

        if status != "PLAYING" and status != "Jugando":
            self.pausar_simulacion()
            self._noticia = f"🏁 FIN: {status}"
            self.noticiaCambio.emit(self._noticia)

    @Slot(result=list)
    def obtener_datos_historial(self):
        """
        Devuelve una lista de 5 listas: [Dias, S, I, R, M]
        Optimizado para graficar rápido.
        """
        if not hasattr(self.motor, 'historial'): return []
        
        # Obtenemos el DataFrame del historial
        # Si está vacío, intentamos recargar de la DB
        df = self.motor.historial
        if df.empty:
             df = self.motor.csv.historial()
        
        if df.empty: return []

        # Extraemos columnas como listas simples de Python (JSON compatible)
        # Aseguramos que estén ordenados por día
        try:
            # Convertir a numérico por seguridad
            dias = df["dia"].astype(int).tolist()
            s = df["total_S"].astype(float).tolist()
            i = df["total_I"].astype(float).tolist()
            r = df["total_R"].astype(float).tolist()
            m = df["total_M"].astype(float).tolist()
            
            return [dias, s, i, r, m]
        except Exception as e:
            print(f"Error extrayendo historial: {e}")
            return []

    @Slot(str, result=list)
    def obtener_ranking_global(self, criterio="I"):
        """
        Devuelve el ranking ordenado según el criterio:
        'I': Infectados, 'M': Muertos, 'R': Recuperados, 'S': Sanos
        """
        if not hasattr(self.motor, 'dataframe'): return []
        
        df = self.motor.dataframe.copy()
        
        # Evitar división por cero
        df["poblacion"] = df["poblacion"].replace(0, 1)
        
        # Seleccionamos la columna clave para ordenar
        col_sort = "I"
        if criterio == "M": col_sort = "M"
        elif criterio == "R": col_sort = "R"
        elif criterio == "S": col_sort = "S"
        
        # Calculamos el ratio específico para la barra de progreso
        df["ratio"] = df[col_sort] / df["poblacion"]
        
        # Ordenamos de Mayor a Menor
        df_sorted = df.sort_values(by=col_sort, ascending=False)
        
        # Extraemos Top 200
        resultado = []
        for index, row in df_sorted.iterrows():
            # Filtro visual: Si el valor es 0, quizás no queramos mostrarlo (opcional)
            # Pero para Sanos siempre habrá, así que lo dejamos pasar.
            
            resultado.append({
                "nombre": str(row["Country Name"]),
                "codigo": str(row.get("Country Code", "???")),
                "poblacion": int(row["poblacion"]),
                "valor": int(row[col_sort]), # El valor principal (ej. Muertos)
                "ratio": float(row["ratio"]), # Para la barra (0.0 a 1.0)
                "infectados": int(row["I"]),    # Datos extra por si acaso
                "muertos": int(row["M"]),
                "recuperados": int(row["R"]),
                "sanos": int(row["S"])
            })
                
        return resultado
