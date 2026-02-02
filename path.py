import sys
import os


def rutas(ruta_relativa):
    """Devuelve la ruta absoluta correcta, funcionando tanto como script o compilado"""
    ruta_base = getattr(sys,'_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(ruta_base, ruta_relativa)
