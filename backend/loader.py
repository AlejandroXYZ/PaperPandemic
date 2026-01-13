from dataclasses import dataclass
import pandas as pd
import sqlite3 as sql
import os

@dataclass
class Loader():
    csv : str

    def cargar_mapa(self,df):
        paises = dict(zip(df["Country Name"], df.index))
        return paises
    
    def cargar_df(self):
        print("Cargando el archivo csv")
        df = pd.read_csv("data/poblacion.csv")
        if df["poblacion"].dtype == 'object':
            df["poblacion"] = df["poblacion"].astype(str).str.replace(",", "")
        
        df["poblacion"] = pd.to_numeric(df["poblacion"], errors='coerce')
        df = df.dropna(subset=["poblacion"])
        df = df.dropna(subset=["Country Name"])
        df["poblacion"] = df["poblacion"].astype(int)


        df["S"] = df["poblacion"]
        df["I"] = 0.0
        df["R"] = 0.0
        df["beta"] = 0.3
        df["gamma"] = 0.1
        return df

    def cargar_db(self):
        conn = sql.connect("data/mundo.db")
        df = pd.read_sql("SELECT * FROM estado_actual",conn)
        conn.close()
        return df


    def historial(self):
        conn = sql.connect("data/mundo.db")
        df = pd.read_sql("SELECT * FROM historial",conn)
        conn.close()
        return df

        
    def crear_db(self):

        if os.path.exists("data/mundo.db"):
            print("Cargando base de datos...")
            return True
        else:
            print("Creado base de datos")
            conn = sql.connect("data/mundo.db")
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS estado_actual ( 'Country Name' TEXT PRIMARY KEY, 'poblacion' INTEGER,'S' INTEGER , 'I' INTEGER, 'R' INTEGER )")
            cursor.execute("CREATE TABLE IF NOT EXISTS historial( dia TEXT PRIMARY KEY, total_I INTEGER, total_S INTEGER, total_R INTEGER, Primer_pais TEXT)")        
            conn.commit()
            cursor.close()
            conn.close()
            print("Base de datos creada con éxito")
            return False

    def guardar_estados(self,datos,pais):
        try:
            conn = sql.connect("data/mundo.db")
            df_ultimo = pd.read_sql_query("SELECT dia FROM historial ORDER BY ROWID DESC LIMIT 1", conn)
            
            if not df_ultimo.empty:
                ultimo_dia = int(df_ultimo.iloc[0, 0])
            else:
                ultimo_dia = 0 
            
            diccionario = {
            "total_S": datos["S"].sum(),
            "total_R": datos["R"].sum(),            
            "total_I": datos["I"].sum(),
            "dia": ultimo_dia + 1,
            "Primer_pais": pais}
            df = pd.DataFrame([diccionario])
            df.to_sql("historial",conn,if_exists="append",index=False)         
            datos.to_sql("estado_actual",conn,if_exists="replace",index=False)         

 
            conn.close()

        except Exception as e:
            conn.close()
            print("Ha ocurrido un error mientras se guardaban los estados")
            raise e
