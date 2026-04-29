import pathlib

root = pathlib.Path(r"d:/PROJECTS/TraceFind/backend/src")
count = 0
for p in root.rglob("*.py"):
    txt = p.read_text(encoding="utf-8")
    new = txt.replace("from src.", "from ")
    if new != txt:
        p.write_text(new, encoding="utf-8")
        print(f"Fixed: {p.relative_to(root)}")
        count += 1
print(f"\nDone. Fixed {count} files.")
