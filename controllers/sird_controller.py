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
        self._dia = "Día 1"
        self._sanos = 0
        self._infectados = 0
        self._recuperados = 0
        self._muertos = 0
        self._paisesInfectados = 0
        self._noticia = "Preparado. Pulsa Play."
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick_simulacion)
        self.isPlaying = False

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

    @Property(str, notify=diaChanged)
    def dia(self): return str(self._dia)

    @Property(str, notify=noticiaCambio)
    def noticia(self): return self._noticia

    # --- LÓGICA ---
    @Slot(bool)
    def toggle_simulacion(self, encendido):
        self.isPlaying = encendido
        if encendido:
            print("▶️ Iniciando Timer...")
            self.timer.start(1700)
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
             self._dia = "Día 1"
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
