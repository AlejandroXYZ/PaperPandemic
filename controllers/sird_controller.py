from PySide6.QtCore import QObject, QTimer, Property, Signal, Slot
from backend.engine import Engine 
from controllers.mapa_modelo import MapaModeloSIRD 
import time


class ControladorSIRD(QObject):
    # ==========================================================
    # SEÑALES (Avisan a QML cuando hay que actualizar la pantalla)
    # ==========================================================
    diaCambiado = Signal()
    datosCambiados = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        print("Iniciando Motor SIRD...")
        
        # 1. Instanciamos tu modelo matemático y el mapa
        self.motor = Engine() 
        self.mapa_modelo = MapaModeloSIRD() 
        
        # 2. Variables iniciales (Día 1)
        self._dia = 1
        self._noticia = "Día 1: Se ha detectado el paciente cero."
        self._paises_infectados = 1 
        
        # 3. Cargamos los datos reales del Día 1 desde tu base de datos
        self._actualizar_estadisticas_iniciales()
        self.mapa_modelo.actualizar_datos(self.motor.dataframe.to_dict(orient="records"))

        # 4. Configuramos el Temporizador (QTimer)
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick_simulacion)
        self.velocidad_ms = 1500 # 1000ms = 1 segundo por día


    def _calcular_color_hex(self, infectados, poblacion):
        """Convierte gravedad de infección a color HEX (Verde -> Rojo)"""
        if infectados == 0:
            return "#D1D5DB" # Gris (Sano)
        
        porcentaje = infectados / poblacion
        
        # LÓGICA DE COLORES (Aquí puedes poner la complejidad que quieras, es Python!)
        if porcentaje < 0.01: return "#FCD34D" # Amarillo (Brote inicial)
        if porcentaje < 0.10: return "#F97316" # Naranja (Contagio)
        if porcentaje < 0.30: return "#EF4444" # Rojo Claro (Peligro)
        return "#7F1D1D" # Rojo Sangre Oscuro (Colapso)


    def _actualizar_estadisticas_iniciales(self):
        """Lee los totales directamente del DataFrame inicial de Pandas"""
        df = self.motor.dataframe
        self._sanos = int(df["S"].sum())
        self._infectados = int(df["I"].sum())
        self._recuperados = int(df["R"].sum())
        self._muertos = int(df["M"].sum())
        self._paises_infectados = len(df[df["I"] > 0]) # Países con al menos 1 infectado

    def tick_simulacion(self):
        """Se ejecuta cada vez que el Timer hace 'Tick' (Avanza 1 día)"""
        tiempo_inicio = time.perf_counter()
        resultado = self.motor.avanzar_dia() 
        tiempo_fin = time.perf_counter()
        milisegundos = (tiempo_fin - tiempo_inicio) * 1000
        print(f"⏱️ Backend tardó: {milisegundos:.2f} ms") # Muestra el tiempo en terminal
        totales = resultado["totales"]
        datos_paises = resultado["datos"] # Lista de diccionarios
        for pais in datos_paises:
            color = self._calcular_color_hex(pais["I"], pais["poblacion"])
            pais["color_calculado"] = color
        
        # Actualizamos variables de estado
        self._dia += 1
        self._sanos = totales["S"]
        self._infectados = totales["I"]
        self._recuperados = totales["R"]
        self._muertos = totales["M"]
        self._paises_infectados = sum(1 for pais in datos_paises if pais["I"] > 0)

        # Actualizamos el color de los países en el mapa
        self.mapa_modelo.actualizar_datos(datos_paises)

        # Lógica para cambiar la noticia del Ticker inferior
        if self._infectados > 1000000 and "ALERTA" not in self._noticia:
            self._noticia = "¡ALERTA MUNDIAL! Los infectados superan el millón."

        # Emitimos señales para que QML sepa que debe redibujar
        self.diaCambiado.emit()
        self.datosCambiados.emit()

        

    # ==========================================================
    # SLOTS (Conectados a los botones de QML)
    # ==========================================================
    @Slot(bool, name="toggle_simulacion")
    def toggle_simulacion(self, is_playing):
        if is_playing:
            print("▶ Simulación Iniciada")
            self.timer.start(self.velocidad_ms)
        else:
            print("⏸ Simulación Pausada")
            self.timer.stop()

    @Slot(name="reiniciar")
    def reiniciar(self):
        print("⟲ Reiniciando simulación desde cero...")
        self.timer.stop()
        
        # 1. Destruimos y recreamos el motor desde cero
        self.motor = Engine() 
        
        # 2. Reseteamos los datos al estado inicial
        self._dia = 1
        self._actualizar_estadisticas_iniciales()
        self._noticia = "Día 1: Se ha detectado el paciente cero."
        
        # 3. Restauramos el mapa al color original
        self.mapa_modelo.actualizar_datos(self.motor.dataframe.to_dict(orient="records"))

        # 4. Refrescamos la pantalla
        self.diaCambiado.emit()
        self.datosCambiados.emit()

    # ==========================================================
    # PROPERTIES (Variables accesibles desde la barra inferior de QML)
    # ==========================================================
    @Property(int, notify=diaCambiado)
    def dia(self): return self._dia

    @Property(float, notify=datosCambiados)
    def sanos(self): return self._sanos

    @Property(float, notify=datosCambiados)
    def infectados(self): return self._infectados

    @Property(float, notify=datosCambiados)
    def recuperados(self): return self._recuperados

    @Property(float, notify=datosCambiados)
    def muertos(self): return self._muertos

    @Property(str, notify=datosCambiados)
    def noticia(self): return self._noticia

    @Property(int, notify=datosCambiados)
    def paisesInfectados(self): return self._paises_infectados
