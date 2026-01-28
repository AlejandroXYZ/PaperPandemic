import xml.etree.ElementTree as ET
import json
import re
import os

# --- CONFIGURACIÓN ---
INPUT_FILE = "mapa_full.svg"       # Tu archivo original pesado (el de 1.2MB)
OUTPUT_FILE = "nuevo.json"

def optimizar_svg():
    print(f"🔧 Generando mapa en Calidad Balanceada (HD)...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ ERROR: No encuentro '{INPUT_FILE}'.")
        return

    # 1. Limpieza de namespaces (igual que antes, esto es vital)
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        contenido_raw = f.read()
    
    contenido_limpio = re.sub(r'(mapsvg|inkscape|sodipodi):\w+="[^"]+"', '', contenido_raw)

    try:
        root = ET.fromstring(contenido_limpio)
    except ET.ParseError as e:
        print(f"❌ Error leyendo XML: {e}")
        return

    data_final = {}
    
    # Namespaces estándar del SVG
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    paths = root.findall(".//svg:path", ns)
    if not paths:
        paths = root.findall(".//path")

    print(f"⚙️ Procesando {len(paths)} países...")
    
    for path in paths:
        # Intentamos obtener el código de 3 letras (AFG)
        codigo = path.get("title") 
        if not codigo:
            codigo = path.get("id") # Fallback a 2 letras si no hay title
            
        d_string = path.get("d")

        if codigo and d_string:
            codigo = codigo.split(" ")[0].strip().upper()

            # --- AQUÍ ESTÁ EL CAMBIO DE CALIDAD ---
            # Antes: r'(\d+\.\d{1})\d+' (1 decimal -> Muy cuadrado)
            # Ahora: r'(\d+\.\d{3})\d+' (3 decimales -> Curvas suaves)
            # Esto es un equilibrio perfecto para tu Atom.
            d_optimizado = re.sub(r'(\d+\.\d{3})\d+', r'\1', d_string)
            
            data_final[codigo] = d_optimizado

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data_final, f)

    print(f"✅ ¡LISTO! Mapa HD generado en {OUTPUT_FILE}")

if __name__ == "__main__":
    optimizar_svg()
