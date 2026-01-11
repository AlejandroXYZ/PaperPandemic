import csv
import json
import urllib.request
import urllib.error

def obtener_clima(latitud):
    """Determina el clima aproximado basado en la latitud."""
    if latitud is None:
        return "Templado"
    lat = abs(latitud)
    if lat < 23.5:
        return "Cálido"
    elif lat < 50:
        return "Templado"
    else:
        return "Frío"

def generar_csv_paises():
    print("⏳ Conectando a la API con los filtros específicos...")
    
    # CORRECCIÓN: Agregamos ?fields= para pedir solo lo necesario y evitar el error 400
    campos = "name,cca3,population,borders,latlng,landlocked,translations"
    url = f"https://restcountries.com/v3.1/all?fields={campos}"
    
    try:
        # Hacemos la petición a la API
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        respuesta = urllib.request.urlopen(req)
        datos = json.loads(respuesta.read().decode())
        
        # Diccionario para mapear códigos de país (CCA3) a nombres en español
        codigo_a_nombre = {}
        for pais in datos:
            codigo = pais.get("cca3", "N/A")
            try:
                nombre = pais["translations"]["spa"]["common"]
            except KeyError:
                nombre = pais["name"]["common"]
            codigo_a_nombre[codigo] = nombre

        filas = []
        
        print(f"⚙️  Procesando {len(datos)} países...")

        for pais in datos:
            # 1. Country Name y Code
            try:
                nombre = pais["translations"]["spa"]["common"]
            except KeyError:
                nombre = pais["name"]["common"]
            
            codigo = pais.get("cca3", "N/A")
            
            # 2. Población (Dato real de la API)
            poblacion_base = pais.get("population", 0)
            
            # 3. Clima
            latlng = pais.get("latlng", [])
            latitud = latlng[0] if len(latlng) > 0 else None
            clima = obtener_clima(latitud)
            
            # 4. Vecinos (Frontera terrestre)
            bordes_codigos = pais.get("borders", [])
            vecinos_nombres = [codigo_a_nombre.get(b, b) for b in bordes_codigos]
            vecinos_str = ", ".join(vecinos_nombres) if vecinos_nombres else "Ninguno (Isla/Aislado)"
            
            # 5. Puerto
            sin_salida_mar = pais.get("landlocked", False)
            if sin_salida_mar:
                puerto = "Sin acceso directo (Uso de puertos vecinos)"
            else:
                puerto = "Acceso a Océano/Mar"
                
            # 6. Vuelo
            vuelo = "Accesible (Rutas Internacionales)"

            filas.append([
                nombre,
                codigo,
                poblacion_base,
                clima,
                vecinos_str,
                puerto,
                vuelo
            ])
            
        # Ordenar alfabéticamente
        filas.sort(key=lambda x: x[0])

        # Escribir el CSV
        nombre_archivo = "paises_mundo_2025.csv"
        encabezados = ["Country Name", "Country Code", "población", "clima", "vecinos", "puerto", "vuelo"]
        
        with open(nombre_archivo, mode='w', newline='', encoding='utf-8-sig') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(encabezados)
            escritor.writerows(filas)
            
        print(f"✅ ¡Éxito! Archivo creado: {nombre_archivo}")

    except urllib.error.HTTPError as e:
        print(f"❌ Error HTTP de la API: {e.code} - {e.reason}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    generar_csv_paises()
