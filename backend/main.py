from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from engine import Engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print("Iniciando Motor Simulación")
motor = Engine()


@app.get("/")
def home():
    return {"mensaje": "Simulador Pandemia Funcionando"}


@app.get("/resumen")
def obtener_resumen():
    """Devuelve los datos actuales de la simulación para pintar el mapa por primera vez"""
    df = motor.sir.df
    total_paises_infectados = len(df[df["I"] > 0])
    total_paises = len(df)
    total_infectados = int(df["I"].sum())
    primer_pais = motor.primer_pais

    estado = "En curso" if total_infectados > 0 else "Sin iniciar / Extinto"
    
    return {
        "estado": estado,
        "paises_infectados": total_paises_infectados,
        "total_poblacion_infectada": total_infectados,
        "primer_pais_origen": primer_pais,
        "total_paises_mundo": total_paises
    }


@app.post("/avanzar_dia")
def avanzar():
    """Avanza un día en la simulación y devuelve los cambios"""
    resultado = motor.avanzar_dia()
    return {
        "mensaje": "Día avanzado correctamente",
        "datos": resultado
    }


@app.get("/reiniciar")
def reiniciar():
    """Reinicia la simulación desde el estado inicial"""
    global motor
    motor = Engine()
    return {"mensaje": "Simulación reiniciada"}
