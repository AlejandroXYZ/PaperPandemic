import pandas as pd
import sqlite3 as sql
import os

class Loader:
    def __init__(self, opt_instance):
        self.opt = opt_instance

    def _reparar_columnas(self, df):
        """Asegura que existan las columnas críticas"""
        columnas_texto = ["vuelo", "puerto", "vecinos", "Country Code", "Country Name"]
        for col in columnas_texto:
            if col not in df.columns:
                df[col] = "No"
        return df

    def cargar_mapa(self, df):
        if "Country Name" not in df.columns: return {}
        return dict(zip(df["Country Name"], df.index))
    
    def cargar_df(self):
        # Intentar cargar CSV
        if not os.path.exists(self.opt.RUTA_CSV):
            print(f"❌ ERROR: No existe {self.opt.RUTA_CSV}")
            return pd.DataFrame(columns=["Country Name", "poblacion", "vuelo", "puerto", "vecinos", "S", "I", "R", "M", "beta", "gamma", "mu"])

        try:
            df = pd.read_csv(self.opt.RUTA_CSV)
        except Exception as e:
            print(f"❌ ERROR leyendo CSV: {e}")
            return pd.DataFrame()
        
        # Limpieza y Tipos
        if "poblacion" in df.columns:
            if df["poblacion"].dtype == 'object':
                df["poblacion"] = df["poblacion"].astype(str).str.replace(",", "")
            df["poblacion"] = pd.to_numeric(df["poblacion"], errors='coerce').fillna(0).astype(int)
            df = df[df["poblacion"] > 0] # Eliminar países sin gente
        
        if "Country Name" in df.columns:
            df = df.dropna(subset=["Country Name"])

        df = self._reparar_columnas(df)

        # Inicialización de Modelo
        df["S"] = df["poblacion"]
        df["I"] = 0
        df["R"] = 0
        df["M"] = 0
        
        # Parámetros iniciales
        df["beta"] = self.opt.beta
        df["gamma"] = self.opt.gamma
        df["mu"] = self.opt.mu
        
        # Conversión a string segura
        df["vuelo"] = df["vuelo"].astype(str)
        df["puerto"] = df["puerto"].astype(str)
        
        return df

    def cargar_db(self):
        try:
            conn = sql.connect(self.opt.RUTA_DB_CREADA)
            df = pd.read_sql("SELECT * FROM estado_actual", conn)
            conn.close()
            
            if df.empty: raise Exception("DB Vacía")
            
            df = self._reparar_columnas(df)
            # Actualizar tasas con los sliders actuales
            df["beta"] = self.opt.beta
            df["gamma"] = self.opt.gamma
            df["mu"] = self.opt.mu
            return df
        except:
            print("⚠️ DB vacía o corrupta. Recargando desde CSV...")
            return self.cargar_df() # Fallback al CSV

    def historial(self):
        try:
            conn = sql.connect(self.opt.RUTA_DB_CREADA)
            df = pd.read_sql("SELECT * FROM historial", conn)
            conn.close()
            return df
        except:
            return pd.DataFrame()
        
    def crear_db(self):
        """Crea la DB y LA RELLENA INMEDIATAMENTE con el CSV"""
        os.makedirs(os.path.dirname(self.opt.RUTA_DB_CREADA), exist_ok=True)

        conn = sql.connect(self.opt.RUTA_DB_CREADA)
        cursor = conn.cursor()
        
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
        count = cursor.fetchone()[0]
        
        exito = False
        if count == 0:
            print("📥 Inicializando DB con datos del CSV...")
            df = self.cargar_df() # Leemos el CSV
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

    def guardar_estados(self, datos, pais):
        try:
            conn = sql.connect(self.opt.RUTA_DB_CREADA)
            
            # Historial
            ultimo_dia = 0
            try:
                res = pd.read_sql_query("SELECT dia FROM historial ORDER BY ROWID DESC LIMIT 1", conn)
                if not res.empty: ultimo_dia = int(res.iloc[0, 0])
            except: pass
            
            dicc = {
                "total_S": datos["S"].sum(), "total_R": datos["R"].sum(),            
                "total_I": datos["I"].sum(), "total_M": datos["M"].sum(),
                "dia": ultimo_dia + 1, "Primer_pais": pais,
                "Paises_Infectados": (datos["I"] > 0).sum()
            }
            pd.DataFrame([dicc]).to_sql("historial", conn, if_exists="append", index=False)         
            datos.to_sql("estado_actual", conn, if_exists="replace", index=False)         
            conn.close()
        except Exception as e:
            if conn: conn.close()
            print(f"Error guardando: {e}")

    def limpiar_db(self):
        if os.path.exists(self.opt.RUTA_DB_CREADA):
            try:
                os.remove(self.opt.RUTA_DB_CREADA)
                return {"mensaje": "DB Borrada"}, True
            except: return {"error": "Fallo al borrar"}, False
        return {"mensaje": "No existía"}, False
