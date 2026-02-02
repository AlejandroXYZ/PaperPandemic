import pandas as pd
import sqlite3 as sql
import os
from typing import List, Dict, Optional

class Loader():
    """
        Encargada de todas las operaciones de carga, guardado y manejo de datos del Programa

    """

    def __init__(self, opt_instance) -> None:
        self.opt = opt_instance  # Carga de Configuraciones desde clase Options
        

    def _reparar_columnas(self, df: pd.Dataframe) -> pd.Dataframe:
        """Asegura que existan las columnas críticas en el DataFrame"""
        
        columnas_texto: List[str] = ["vuelo", "puerto", "vecinos", "Country Code", "Country Name"]
        for col in columnas_texto:
            if col not in df.columns:
                df[col]: str = "No"

        if "cooldown_vuelo" not in df.columns:
            df["cooldown_vuelo"]: int = 0
        if "cooldown_puerto" not in df.columns:
            df["cooldown_puerto"]: int = 0
        if "cooldown_frontera" not in df.columns:
            df["cooldown_frontera"]: int = 0
        return df


        
    def cargar_mapa(self, df: pd.Dataframe) -> Dict[str,int]:
        """Toma como parámetro el Dataframe para retornar un Diccionario con los nombres de los
           Países y sus índices mejorando la velocidad de operaciones y búsqueda de los datos
        """
        if "Country Name" not in df.columns: return {}
        return dict(zip(df["Country Name"], df.index))


    
    def cargar_df(self) -> pd.Dataframe:
        """Carga el archivo csv ubicado en la carpeta backend/data para generar los datos del mundo
        para la simulación"""
        # Intentar cargar CSV
        if not os.path.exists(self.opt.RUTA_CSV):
            print(f"❌ ERROR: No existe {self.opt.RUTA_CSV}")
            return pd.DataFrame(columns=["Country Name", "poblacion", "vuelo", "puerto", "vecinos", "S", "I", "R", "M", "beta", "gamma", "mu"])

        try:
            df: pd.Dataframe = pd.read_csv(self.opt.RUTA_CSV)
        except Exception as e:
            print(f"❌ ERROR leyendo CSV: {e}")
            return pd.DataFrame()
        
        # Limpieza y Tipos
        if "poblacion" in df.columns:
            if df["poblacion"].dtype == 'object':
                df["poblacion"]: pd.Series = df["poblacion"].astype(str).str.replace(",", "")
            df["poblacion"]: pd.Series = pd.to_numeric(df["poblacion"], errors='coerce').fillna(0).astype('int64')
            df : pd.Dataframe = df[df["poblacion"] > 0] # Eliminar países sin gente
        
        if "Country Name" in df.columns:
            df: pd.Dataframe = df.dropna(subset=["Country Name"])

        df: pd.Dataframe = self._reparar_columnas(df)

        # Inicialización de Modelo
        df["S"]: pd.Series = df["poblacion"].astype("int64")
        df["I"]: pd.Series = 0
        df["R"]: pd.Series = 0
        df["M"]: pd.Series = 0
        
        # Parámetros iniciales
        df["beta"]: pd.Series = self.opt.beta
        df["gamma"]: pd.Series = self.opt.gamma
        df["mu"]: pd.Series = self.opt.mu
        
        # Conversión a string segura
        df["vuelo"]: pd.Series = df["vuelo"].astype(str)
        df["puerto"]: pd.Series = df["puerto"].astype(str)
        
        return df

    def cargar_db(self) -> pd.Dataframe:
        """Carga base de datos existente"""
        try:
            conn: sql.Connection = sql.connect(self.opt.RUTA_DB_CREADA)
            df: pd.Dataframe = pd.read_sql("SELECT * FROM estado_actual", conn)
            conn.close()
            
            if df.empty: raise Exception("DB Vacía")
            
            df: pd.Dataframe = self._reparar_columnas(df)
            # Actualizar tasas con los sliders actuales
            df["beta"]: pd.Series = self.opt.beta
            df["gamma"]: pd.Series = self.opt.gamma
            df["mu"]: pd.Series = self.opt.mu
            return df
        except:
            print("⚠️ DB vacía o corrupta. Recargando desde CSV...")
            return self.cargar_df() # Fallback al CSV

    def historial(self) -> pd.dataframe:
        """Carga el Historial desde la Base de datos cargando la tabla historial
            donde tienen los registros de lo que pasó en la simulación ejecutada 
        """
        try:
            conn: sql.Connect = sql.connect(self.opt.RUTA_DB_CREADA)
            df: pd.Dataframe = pd.read_sql("SELECT * FROM historial", conn)
            conn.close()
            return df
        except Exception as e:
            print(e)
            return pd.DataFrame()
        
    def crear_db(self) -> bool:
        """Crea la db y la rellena inmediatamente con los datos dentro del archivo CSV"""
        os.makedirs(os.path.dirname(self.opt.RUTA_DB_CREADA), exist_ok=True)

        conn: sql.Connect = sql.connect(self.opt.RUTA_DB_CREADA)
        cursor: sql.Cursor = conn.cursor()
        
        # 1. Crear Tablas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estado_actual (
                'Country Name' TEXT, 'Country Code' TEXT, 'poblacion' INTEGER,
                'vuelo' TEXT, 'puerto' TEXT, 'vecinos' TEXT,
                'S' INTEGER, 'I' INTEGER, 'R' INTEGER, 'M' INTEGER,
                'beta' REAL, 'gamma' REAL, 'mu' REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial( 
                dia TEXT, total_I INTEGER, total_S INTEGER, 
                total_R INTEGER, total_M INTEGER, 
                Primer_pais TEXT, Paises_Infectados INTEGER
            )
        """)
        
        # 2. VERIFICAR SI ESTÁ VACÍA Y LLENARLA
        cursor.execute("SELECT count(*) FROM estado_actual")
        count: Optional[tuple] = cursor.fetchone()[0]
        
        exito = False
        if count == 0:
            df: pd.Dataframe = self.cargar_df()
            if not df.empty:
                df.to_sql("estado_actual", conn, if_exists="replace", index=False)
                exito = True
            else:
                print("❌ FATAL: El CSV está vacío o no se pudo leer.")
        else:
            exito = False # Ya existía

        conn.commit()
        cursor.close()
        conn.close()
        return exito



    def guardar_estados(self, datos: pd.Dataframe , pais: str) -> None:
        """
        Guarda todos los datos en la base de datos

        Args:
            datos: 
                Dataframe obtenido después de ejecutar la lógica del Modelo SIRD para avanzar un día
            pais:
                String con el nombre del primer país donde inició el virus
        """

        try:
            conn: sql.Connect = sql.connect(self.opt.RUTA_DB_CREADA)
            
            # Historial
            ultimo_dia: int = 0

            try:
                res: pd.Dataframe = pd.read_sql_query("SELECT dia FROM historial ORDER BY ROWID DESC LIMIT 1", conn)
                if not res.empty: ultimo_dia: int = int(res.iloc[0, 0])
            except: pass
            
            # CONVERSIÓN EXPLÍCITA A FLOAT PARA EVITAR OVERFLOW EN 32 BITS
            dicc: Dict[str,float] = {
                "total_S": float(datos["S"].astype(float).sum()), 
                "total_R": float(datos["R"].astype(float).sum()),            
                "total_I": float(datos["I"].astype(float).sum()), 
                "total_M": float(datos["M"].astype(float).sum()),
                "dia": ultimo_dia + 1, 
                "Primer_pais": pais,
                "Paises_Infectados": int((datos["I"] > 0).sum())
            }
            
            pd.DataFrame([dicc]).to_sql("historial", conn, if_exists="append", index=False)         
            datos.to_sql("estado_actual", conn, if_exists="replace", index=False)         
            conn.close()
        except Exception as e:
            if conn: conn.close()
            print(f"Error guardando: {e}")



    def limpiar_db(self) -> Dict[str,str] | bool:
        """
        Borra la base de datos al reiniciar la simulación desde el menú del programa
        """
        
        if os.path.exists(self.opt.RUTA_DB_CREADA):
            try:
                os.remove(self.opt.RUTA_DB_CREADA)
                return {"mensaje": "DB Borrada"}, True
            except: return {"error": "Fallo al borrar"}, False
        return {"mensaje": "No existía"}, False
