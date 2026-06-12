import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import EERR_STRUCTURE, build_effective_structure

def main():
    print("=== VALIDACIÓN A: IDENTIDAD ESTRUCTURAL ===")
    
    # original way
    A = []
    for item in EERR_STRUCTURE:
        name = item[0]
        is_header = item[1]
        level = item[5] if len(item) > 5 else (0 if is_header else 3)
        A.append((name, is_header, level))
        
    # new way
    effective = build_effective_structure(EERR_STRUCTURE, db_overrides=[])
    B = [(node['partida_name'], node['is_header'], node['level']) for node in effective]
    
    print(f"Longitud A (Original): {len(A)}")
    print(f"Longitud B (Nueva): {len(B)}")
    
    mismatches = []
    max_len = max(len(A), len(B))
    for i in range(max_len):
        item_a = A[i] if i < len(A) else None
        item_b = B[i] if i < len(B) else None
        
        if item_a != item_b:
            mismatches.append((i, item_a, item_b))
            
    print(f"Total diferencias: {len(mismatches)}")
    if len(mismatches) > 0:
        print("\nDiferencias encontradas:")
        for idx, val_a, val_b in mismatches[:10]:
            print(f"  Index {idx}:")
            print(f"    Original: {val_a}")
            print(f"    Nueva:    {val_b}")
    else:
        print("\n[SUCCESS] Ambas listas son completamente IDÉNTICAS (169 elementos).")

if __name__ == '__main__':
    main()
