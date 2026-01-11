from fastapi import FastAPI
from engine import avanzar_dia

app = FastAPI()




@app.get("/")
def leer_raiz():
    resultado = avanzar_dia()
    print("Ejecutado correctamente")
    return resultado
