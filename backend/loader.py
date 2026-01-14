from dataclasses import dataclass
import pandas as pd
import sqlite3 as sql
import os
from options import Options as opt

opt = opt()

@dataclass
class Loader():
    csv : str

    def cargar_mapa(self,df):
        paises = dict(zip(df["Country Name"], df.index))
        return paises
    
    def cargar_df(self):
        print("Cargando el archivo csv")
        df = pd.read_csv(opt.RUTA_CSV)
        if df["poblacion"].dtype == 'object':
            df["poblacion"] = df["poblacion"].astype(str).str.replace(",", "")
        
        df["poblacion"] = pd.to_numeric(df["poblacion"], errors='coerce')
        df = df.dropna(subset=["poblacion"])
        df = df.dropna(subset=["Country Name"])
        df["poblacion"] = df["poblacion"].astype(int)


        df["S"] = df["poblacion"]
        df["I"] = 0.0
        df["R"] = 0.0
        df["M"] = 0.0
        df["beta"] = opt.BETA
        df["gamma"] = opt.GAMMA
        df["mu"] = opt.MU
        return df

    def cargar_db(self):
        conn = sql.connect(opt.RUTA_DB_CREADA)
        df = pd.read_sql("SELECT * FROM estado_actual",conn)
        conn.close()
        return df


    def historial(self):
        conn = sql.connect(opt.RUTA_DB_CREADA)
        df = pd.read_sql("SELECT * FROM historial",conn)
        conn.close()
        return df

        
    def crear_db(self):

        if os.path.exists(opt.RUTA_DB_CREADA):
            print("Cargando base de datos...")
            return True
        else:
            print("Creado base de datos")
            conn = sql.connect(opt.RUTA_DB_CREADA)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS estado_actual ( 'Country Name' TEXT PRIMARY KEY, 'poblacion' INTEGER,'S' INTEGER , 'I' INTEGER, 'R' INTEGER,'M' INTEGER)")
            cursor.execute("CREATE TABLE IF NOT EXISTS historial( dia TEXT PRIMARY KEY, total_I INTEGER, total_S INTEGER, total_R INTEGER, total_M INTEGER, Primer_pais TEXT, Paises_Infectados INTEGER)")        
            conn.commit()
            cursor.close()
            conn.close()
            print("Base de datos creada con éxito")
            return False

    def guardar_estados(self,datos,pais):
        try:
            conn = sql.connect(opt.RUTA_DB_CREADA)
            df_ultimo = pd.read_sql_query("SELECT dia FROM historial ORDER BY ROWID DESC LIMIT 1", conn)
            
            if not df_ultimo.empty:
                ultimo_dia = int(df_ultimo.iloc[0, 0])
            else:
                ultimo_dia = 0 
            
            print(datos.loc[datos["I"] > 0]["I"].sum().round())
            diccionario = {
            "total_S": datos["S"].sum().round(),
            "total_R": datos["R"].sum().round(),            
            "total_I": datos["I"].sum().round(),
            "total_M": datos["M"].sum().round(),
            "dia": ultimo_dia + 1,
            "Primer_pais": pais,
            "Paises_Infectados": datos.loc[datos["I"] > 0]["I"].sum().round()}
            df = pd.DataFrame([diccionario])
            df.to_sql("historial",conn,if_exists="append",index=False)         
            datos.to_sql("estado_actual",conn,if_exists="replace",index=False)         

            conn.close()

        except Exception as e:
            conn.close()
            print("Ha ocurrido un error mientras se guardaban los estados")
            raise e
