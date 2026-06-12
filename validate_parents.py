import sys
import os

# Añadir el path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import EERR_STRUCTURE, build_effective_structure

def verify_parents():
    print("=== INICIANDO VERIFICACIÓN DE INTEGRIDAD DE PADRES ===")
    
    # 1. Obtener la estructura extendida
    effective_struct = build_effective_structure()
    print(f"Total de nodos en la estructura extendida: {len(effective_struct)}")
    
    all_names = [node['partida_name'] for node in effective_struct]
    orphans = []
    multiple_matches = []
    
    # Verificar cada nodo
    for node in effective_struct:
        partida = node['partida_name']
        parent = node['parent_name']
        
        if parent is not None:
            # Buscar coincidencia exacta
            matches = [name for name in all_names if name == parent]
            
            if len(matches) == 0:
                orphans.append((partida, parent))
            elif len(matches) > 1:
                multiple_matches.append((partida, parent, len(matches)))
                
    print("\n--- RESULTADO DE LA VERIFICACIÓN ---")
    print(f"Huérfanos detectados: {len(orphans)}")
    for partida, parent in orphans:
        print(f"  [HUÉRFANO] Nodo: '{partida}' -> parent_name '{parent}' no existe.")
        
    print(f"Nodos con múltiples padres candidatos: {len(multiple_matches)}")
    for partida, parent, count in multiple_matches:
        print(f"  [DUPLICADO] Nodo: '{partida}' -> parent_name '{parent}' coincide con {count} nodos.")
        
    if len(orphans) == 0 and len(multiple_matches) == 0:
        print("\n[PASS] ¡Verificación completada con éxito! 0 huérfanos detectados.")
        return True, orphans
    else:
        print("\n[FAIL] Se detectaron inconsistencias en parent_name.")
        return False, orphans

if __name__ == '__main__':
    verify_parents()
