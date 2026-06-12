with open(r"C:\Users\andre\Desktop\ultrax_app\app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'structure_with_levels' in line:
        print(f"Line {idx+1}: {line.strip()}")
