from PySide6.QtCore import QObject, Slot, Signal, Property, QTimer, QUrl
from typing import List
from backend.engine import Engine
from controllers.mapa_modelo import MapaModeloSIRD
from backend.options import Options
from collections import deque
import random
import os
import datetime
import pandas as pd


class ControladorSIRD(QObject):
    # Señales
    datosCambios = Signal()
    noticiaCambio = Signal(str)
    statsChanged = Signal()
    diaChanged = Signal(str)
    gameOver = Signal("QVariantMap")
    noticiasActualizadas = Signal()

    def __init__(self) -> None:
        super().__init__()

        # 1. Inicializar objetos
        self.opciones: Options = Options()
        self.mapa_modelo: MapaModeloSIRD = MapaModeloSIRD()
        self.motor: Engine = Engine(self.opciones)  # Pasamos opciones al motor

        # 2. Variables de estado
        self._dia: str = "1"
        self._sanos: float = 0
        self._infectados: float = 0
        self._recuperados: float = 0
        self._muertos: float = 0
        self._paisesInfectados: int = 0
        self._primerPais: str = "Esperando..."
        self._noticia: str = "Preparado. Pulsa Play."

        self.timer: QTimer = QTimer()
        self.timer.timeout.connect(self.tick_simulacion)
        self.isPlaying: bool = False
        self._intervalo_ms: int = 1000

        # 3. ¡IMPORTANTE! Cargar datos iniciales para no ver ceros
        # Esto ejecuta una actualización manual sin avanzar el tiempo
        self.actualizar_interfaz_desde_motor()

        self.noticias_data = deque(maxlen=self.opciones.MAX_NOTICIAS_HISTORIAL)

        # Países infectados (Se borra y actualiza cada tick)
        self.paises_infectados_set: set = set()

        #  Hitos/Logros
        self.hitos_reportados: set = set()

    @Property(QObject, constant=True)
    def config(self) -> Options:
        return self.opciones

    @Property(float, notify=statsChanged)
    def sanos(self):
        return float(self._sanos)

    @Property(float, notify=statsChanged)
    def infectados(self):
        return float(self._infectados)

    @Property(float, notify=statsChanged)
    def recuperados(self):
        return float(self._recuperados)

    @Property(float, notify=statsChanged)
    def muertos(self):
        return float(self._muertos)

    @Property(int, notify=statsChanged)
    def paisesInfectados(self):
        return self._paisesInfectados

    @Property(str, notify=statsChanged)
    def primerPais(self):
        return self._primerPais

    @Property(str, notify=diaChanged)
    def dia(self):
        return str(self._dia)

    @Property(str, notify=noticiaCambio)
    def noticia(self):
        return self._noticia

    @Property(list, constant=True)
    def listaNombresPaises(self) -> List[str] | str:
        """Devuelve la lista alfabética de países para el ComboBox de Configuración"""
        if hasattr(self.motor, "dataframe") and not self.motor.dataframe.empty:
            # Obtenemos nombres únicos y los ordenamos
            lista: List[str] = sorted(
                self.motor.dataframe["Country Name"].unique().tolist()
            )
            return lista
        return ["Cargando..."]

    @Slot(float)
    def cambiar_velocidad(self, valor: float) -> None:
        """
        Recibe valor del slider (0.0 a 2.0)
        Convierte a milisegundos (4000ms a 200ms)
        """

        ms_min: int = 200  # Lo más rápido (límite del hardware)
        ms_max: int = 4000  # Lo más lento
        slider_max: float = 2.0  # El valor 'maximo' colocado en QMl

        # Normaliza Convirtiendo el 0..2.0 a 0..1.0
        # Ejemplo: si entra 2.0, factor será 1.0. Si entra 1.0, factor será 0.5
        factor: float = valor / slider_max

        # Interpolación Lineal Inversa
        # Intervalo = Inicio + (Fin - Inicio) * factor
        # como se quiere ir de Mayor a Menor, se resta:
        rango: int = ms_max - ms_min
        nuevo_intervalo: int = int(ms_max - (factor * rango))

        # 3. Seguridad: Nunca bajar del mínimo del hardware
        nuevo_intervalo: int = max(ms_min, nuevo_intervalo)

        self._intervalo_ms: int = nuevo_intervalo

        # Aplicar inmediatamente si está corriendo
        if self.isPlaying:
            self.timer.setInterval(self._intervalo_ms)

    # --- LÓGICA ---
    @Slot(bool)
    def toggle_simulacion(self, encendido: bool) -> None:
        """Cambia el estado de la simulación: corriendo/pausado"""
        self.isPlaying = encendido
        if encendido:
            print("▶️ Iniciando Timer...")
            self.timer.start(self._intervalo_ms)
        else:
            print("⏸️ Pausando Timer...")
            self.timer.stop()

    @Slot()
    def pausar_simulacion(self) -> None:
        self.toggle_simulacion(False)

    @Slot()
    def reiniciar_simulacion(self) -> None:
        self.reiniciar()

    @Slot()
    def reiniciar(self) -> None:
        print("⟲ Reiniciando...")
        self.timer.stop()
        self.isPlaying: bool = False

        # Limpiar
        if hasattr(self, "motor"):
            try:
                self.motor.csv.limpiar_db()
            except:
                pass

        self.mapa_modelo._inicializar_vacio()
        self.motor: Engine = Engine(self.opciones)

        self.paises_infectados_set: set = set()
        self.hitos_reportados: set = set()
        self.noticias_data.clear()

        self._noticia: str = "Simulación Reiniciada."

        # Cargar estado inicial limpio
        self.actualizar_interfaz_desde_motor()

    def tick_simulacion(self) -> None:
        """Avanza la lógica de la simulación un día en un tiempo determinado"""
        if not self.isPlaying:
            return

        # Avanzar lógica
        resultado: pd.Dataframe = self.motor.avanzar_dia()
        self.procesar_resultado(resultado)

    def actualizar_interfaz_desde_motor(self) -> None:
        """Lee el estado actual del motor SIN avanzar el día"""
        # Fuerza una lectura del estado actual del dataframe
        if hasattr(self.motor, "dataframe"):
            # Construye un 'resultado' falso solo para actualizar la UI
            df: pd.Dataframe = self.motor.dataframe
            nombre: str = getattr(self.motor, "primer_pais", "Desconocido")

            if not nombre or nombre == "Desconocido":
                # INTENTO DE RESCATE, Si el motor no sabe, miramos si alguien tiene infectados
                infectados: pd.Series = df[df["I"] > 0]
                if not infectados.empty:
                    nombre: str = infectados.iloc[0]["Country Name"]
                else:
                    nombre: str = self.opciones.PAIS_INICIO

            self._primerPais: str = str(nombre) if nombre else "Desconocido"

            totales: Dict[str, int] = {
                "S": int(df["S"].sum()),
                "I": int(df["I"].sum()),
                "R": int(df["R"].sum()),
                "M": int(df["M"].sum()),
            }

            self._sanos: pd.Series = totales["S"]
            self._infectados: pd.Series = totales["I"]
            self._recuperados: pd.Series = totales["R"]
            self._muertos: pd.Series = totales["M"]
            self._dia: str = "1"
            self.statsChanged.emit()
            self.diaChanged.emit(self._dia)
            self.noticiaCambio.emit(self._noticia)

            self.mapa_modelo.actualizar_datos(df.to_dict(orient="records"))

    def procesar_resultado(self, resultado) -> None:
        status = resultado.get("status", "Jugando")
        datos: pd.Dataframe = resultado.get("datos", [])

        try:
            df: pd.Dataframe = self.motor.dataframe
            virus: str = getattr(self.opciones, "NOMBRE_VIRUS", "Virus-X")

            # DETECTA NUEVOS PAÍSES INFECTADOS
            infectados_ahora: set = set(df[df["I"] > 0]["Country Name"].tolist())
            nuevos: set = infectados_ahora - self.paises_infectados_set

            for pais_nombre in nuevos:
                culpable: str = "Desconocido"

                if len(self.paises_infectados_set) > 0:
                    lista_previos: list = list(self.paises_infectados_set)
                    if lista_previos:
                        culpable = random.choice(lista_previos)
                        frases: List[str] = [
                            f"¡{virus} llegó a {pais_nombre} desde {culpable}!",
                            f"Frontera rota: {culpable} contagió a {pais_nombre}.",
                            f"Turistas de {culpable} llevan el virus a {pais_nombre}.",
                            f"Detectado caso en {pais_nombre}. Origen: {culpable}.",
                        ]
                        msg: str = random.choice(frases)
                    else:
                        msg: str = f"¡{virus} aparece en {pais_nombre}!"
                else:
                    msg: str = f"☣️ ¡PACIENTE CERO detectado en {pais_nombre}!"

                self.generar_noticia(msg, "INFECT")

            # Actualizamos la lista de países (Esto borraba el 1M_INF antes)
            self.paises_infectados_set = infectados_ahora

            # 2. HITOS GLOBALES (Usamos la NUEVA memoria separada)
            # Hito: 1 Millón
            if self._infectados > 1000000 and "1M_INF" not in self.hitos_reportados:
                self.generar_noticia(
                    f"¡El mundo supera 1 Millón de infectados!", "INFO"
                )
                self.hitos_reportados.add("1M_INF")  # Guardamos en la memoria segura

            # Hito: 100 Millones
            if self._infectados > 100000000 and "100M_INF" not in self.hitos_reportados:
                self.generar_noticia(
                    f"¡CATASTROFE: 100 Millones de infectados!", "DEATH"
                )
                self.hitos_reportados.add("100M_INF")

            # Hito: 50% Población Mundial (aprox 4 billones)
            if (
                self._infectados > 4000000000
                and "HALF_WORLD" not in self.hitos_reportados
            ):
                self.generar_noticia(
                    f"¡La mitad de la humanidad ha contraído {virus}!", "DEATH"
                )
                self.hitos_reportados.add("HALF_WORLD")

        except Exception as e:
            print(f"⚠️ Error generando noticia: {e}")

        # --- FIN LÓGICA NOTICIAS ---

        if datos:
            self.mapa_modelo.actualizar_datos(datos)

        totales: Dict = resultado.get("totales", {})
        if totales:
            self._sanos: int = int(totales.get("S", 0))
            self._infectados: int = int(totales.get("I", 0))
            self._recuperados: int = int(totales.get("R", 0))
            self._muertos: int = int(totales.get("M", 0))

            self._dia: str = str(resultado.get("dia", self._dia))
            self._paisesInfectados: int | float = sum(
                1 for p in datos if p.get("I", 0) > 0
            )

            self.statsChanged.emit()
            self.diaChanged.emit(self._dia)

            if status != "PLAYING" and status != "Jugando":
                self.pausar_simulacion()
                self._noticia: str = f"🏁 FIN: {status}"
                self.noticiaCambio.emit(self._noticia)

                self.gameOver.emit(
                    {
                        "titulo": status,
                        "dia": self._dia,
                        "sanos": float(self._sanos),
                        "recuperados": float(self._recuperados),
                        "muertos": float(self._muertos),
                        "paises_afectados": int(self._paisesInfectados),
                    }
                )

    @Slot(result=list)
    def obtener_datos_historial(self) -> List:
        """
        Devuelve una lista de 5 listas: [Dias, S, I, R, M]
        Optimizado para graficar rápido.
        """
        if not hasattr(self.motor, "historial"):
            return []

        # Obtiene el DataFrame del historial
        # Si está vacío, intenta recargar de la DB
        df: pd.Dataframe = self.motor.historial
        if df.empty:
            df: pd.Dataframe = self.motor.csv.historial()

        if df.empty:
            return []

        # Extrae columnas como listas simples de Python (JSON compatible)
        try:
            # Convertir a numérico por seguridad
            dias: List[int] = df["dia"].astype(int).tolist()
            s: List[float] = df["total_S"].astype(float).tolist()
            i: List[float] = df["total_I"].astype(float).tolist()
            r: List[float] = df["total_R"].astype(float).tolist()
            m: List[float] = df["total_M"].astype(float).tolist()

            return [dias, s, i, r, m]
        except Exception as e:
            print(f"Error extrayendo historial: {e}")
            return []

    @Slot(str, result=list)
    def obtener_ranking_global(self, criterio: str = "I") -> List:
        """
        Devuelve el ranking ordenado según el criterio:
        'I': Infectados, 'M': Muertos, 'R': Recuperados, 'S': Sanos
        """
        if not hasattr(self.motor, "dataframe"):
            return []

        df: pd.Dataframe = self.motor.dataframe.copy()

        # Evitar división por cero
        df["poblacion"]: pd.Series = df["poblacion"].replace(0, 1)

        # Seleccionamos la columna clave para ordenar
        col_sort: int = "I"
        if criterio == "M":
            col_sort: str = "M"
        elif criterio == "R":
            col_sort: str = "R"
        elif criterio == "S":
            col_sort: str = "S"

        # Calculamos el ratio específico para la barra de progreso
        df["ratio"]: pd.Series = df[col_sort] / df["poblacion"]

        # Ordenamos de Mayor a Menor
        df_sorted: pd.Dataframe = df.sort_values(by=col_sort, ascending=False)

        # Extraemos Top 200
        resultado: List = [str, str | int | float]
        for index, row in df_sorted.iterrows():
            # Filtro visual: Si el valor es 0, quizás no queramos mostrarlo (opcional)
            # Pero para Sanos siempre habrá, así que lo dejamos pasar.

            resultado.append(
                {
                    "nombre": str(row["Country Name"]),
                    "codigo": str(row.get("Country Code", "???")),
                    "poblacion": int(row["poblacion"]),
                    "valor": int(row[col_sort]),  # El valor principal (ej. Muertos)
                    "ratio": float(row["ratio"]),  # Para la barra (0.0 a 1.0)
                    "infectados": int(row["I"]),  # Datos extra por si acaso
                    "muertos": int(row["M"]),
                    "recuperados": int(row["R"]),
                    "sanos": int(row["S"]),
                }
            )

        return resultado

    @Slot(str, result="QVariantMap")
    def obtener_detalle_pais(self, codigo_pais: str) -> Dict:
        """
        Calcula todos los datos necesarios para la gráfica de pastel en Python.
        Retorna un diccionario listo para QML.
        """
        # Buscamos en el modelo de mapa que ya tiene los datos frescos del último tick
        datos = next(
            (p for p in self.mapa_modelo.paises if p["codigo"] == codigo_pais), None
        )

        if not datos:
            return {"existe": False}

        pob: float = datos["poblacion"]
        i: float = datos["infectado"]
        r: float = datos["recuperado"]
        m: float = datos.get("muerto", 0)

        s: float = pob - i - r - m
        if s < 0:
            s = 0  # Corrección de seguridad

        return {
            "existe": True,
            "nombre": datos["nombre"],
            "poblacion": pob,
            "valS": s,
            "valI": i,
            "valR": r,
            "valM": m,
            # Pre-calculamos porcentajes para tooltips
            "pctS": (s / pob) * 100,
            "pctI": (i / pob) * 100,
            "pctR": (r / pob) * 100,
            "pctM": (m / pob) * 100,
        }

    @Slot()
    def activar_cheat_fin(self):
        """Función de debugging, presiona la tecla K y se termina la simulación automaticamente"""
        print("😈 CHEAT ACTIVADO: Apocalipsis instantáneo")
        self.motor.cheat_fin_rapido()

        # Actualiza los números visuales
        self.actualizar_interfaz_desde_motor()

        # Fuerza un avance de día MANUAL para que el motor detecte el fin
        # Así no se tiene que esperar al Timer ni darle a Play
        resultado: pd.Dataframe = self.motor.avanzar_dia()
        self.procesar_resultado(resultado)

    @Slot(result=list)
    def obtener_historial_noticias(self) -> List:
        # Convierte a lista para que QML lo entienda
        return list(self.noticias_data)

    def generar_noticia(self, mensaje: str, tipo: str = "INFO"):
        """
        Tipos: 'INFECT' (Rojo), 'DEATH' (Negro), 'CURE' (Azul), 'INFO' (Gris)
        """
        item: Dict[str, str] = {"dia": self._dia, "mensaje": mensaje, "tipo": tipo}

        # Añade al principio
        self.noticias_data.appendleft(item)

        # Envia solo el texto a la barra inferior
        self._noticia: str = mensaje
        self.noticiaCambio.emit(mensaje)
        # Avisa a la lista completa
        self.noticiasActualizadas.emit()

    @Slot(str)
    def exportar_datos_excel(self, file_url: str):
        """
        Genera DOS archivos CSV basados en la ruta elegida por el usuario:
        1. [Nombre]_Estado_Actual.csv (Datos por país)
        2. [Nombre]_Historial_Global.csv (Datos temporales de la DB)
        """
        try:
            if not hasattr(self.motor, "dataframe"):
                return

            # 1. LIMPIEZA DE RUTA (Cross-Platform)
            ruta_limpia = QUrl(file_url).toLocalFile()

            # Separa nombre y extensión para insertar los sufijos
            # Ej: "/home/user/Datos.csv" -> base="/home/user/Datos", ext=".csv"
            base, ext = os.path.splitext(ruta_limpia)
            if not ext:
                ext = ".csv"  # Por si el usuario no puso extensión

            # ---------------------------------------------------------
            # ARCHIVO 1: ESTADO ACTUAL (Tabla de Países)
            # ---------------------------------------------------------
            ruta_estado: str = f"{base}_Estado_Actual{ext}"
            self.motor.dataframe.to_csv(ruta_estado, index=False, encoding="utf-8-sig")

            # ---------------------------------------------------------
            # ARCHIVO 2: HISTORIAL (Tabla de Tiempo)
            # ---------------------------------------------------------
            ruta_historial: str = f"{base}_Historial_Global{ext}"

            # Intenta obtener el historial fresco desde la base de datos
            df_historial: pd.DataFrame = pd.DataFrame()
            try:
                df_historial: pd.Dataframe = self.motor.csv.historial()
            except Exception as e:
                print(f"⚠️ Error leyendo historial DB: {e}")

            if not df_historial.empty:
                df_historial.to_csv(ruta_historial, index=False, encoding="utf-8-sig")
                mensaje_extra: str = " y Historial"
            else:
                mensaje_extra: str = " (Historial vacío)"

            # ---------------------------------------------------------
            # NOTIFICACIÓN
            # ---------------------------------------------------------
            nombre_base: str = os.path.basename(base)
            self.generar_noticia(
                f"💾 Guardado: {nombre_base}_Estado{ext} y {nombre_base}_Historial{ext}",
                "INFO",
            )

            print(f"✅ Exportación exitosa:")
            print(f"   📄 {ruta_estado}")
            print(f"   📄 {ruta_historial}")

        except Exception as e:
            self.generar_noticia("❌ Error crítico al exportar.", "DEATH")
            print(f"Error exportando: {e}")

    @Slot(list)
    def cambiar_tema_mapa(self, lista_colores: List):
        """Recibe ['#RRGGBB', ...] y actualiza el modelo del mapa"""
        print(f"🎨 Cambiando paleta del mapa: {lista_colores}")
        self.mapa_modelo.actualizar_paleta_colores(lista_colores)
