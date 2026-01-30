import os

# Archivos que QUEREMOS incluir (rutas relativas)
archivos_clave = [
    "main.py",
    "backend/engine.py",
    "backend/sir_model.py",
    "backend/loader.py",
    "backend/options.py",
    "controllers/sird_controller.py",
    "controllers/mapa_modelo.py",
    "ui/main.qml",
    "ui/components/Mapa.qml",
    "ui/components/BarraInferior.qml",
    "ui/components/BarraSuperior.qml",
    "ui/components/MenuOpciones.qml",
    "ui/components/PieChartPopup.qml",
    "ui/components/GameOverModal.qml",
    "ui/components/VistaGrafica.qml",
    "ui/components/VistaNoticias.qml",
    "ui/components/VistaRanking.qml"

]

output_file = "contexto_proyecto.txt"

def crear_contexto():
    with open(output_file, "w", encoding="utf-8") as salida:
        salida.write("ESTE ES EL CÓDIGO ACTUAL DEL PROYECTO:\n")
        salida.write("========================================\n\n")
        
        for ruta in archivos_clave:
            if os.path.exists(ruta):
                salida.write(f"--- INICIO DE ARCHIVO: {ruta} ---\n")
                try:
                    with open(ruta, "r", encoding="utf-8") as entrada:
                        salida.write(entrada.read())
                except Exception as e:
                    salida.write(f"\n[Error leyendo archivo: {e}]\n")
                salida.write(f"\n--- FIN DE ARCHIVO: {ruta} ---\n\n")
            else:
                print(f"⚠️ No encontré: {ruta}")

    print(f"✅ ¡Listo! Archivo '{output_file}' creado.")
    print("Ahora arrastra ese archivo al chat de la IA.")

if __name__ == "__main__":
    crear_contexto()
