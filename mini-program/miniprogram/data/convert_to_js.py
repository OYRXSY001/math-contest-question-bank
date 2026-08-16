"""Convert JSON data files to JS modules for WeChat mini-program compatibility."""
import json, os

base = os.path.dirname(__file__)

for name in ["papers", "questions", "knowledge_points", "qkp"]:
    json_path = os.path.join(base, f"{name}.json")
    js_path = os.path.join(base, f"{name}.js")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(js_path, "w", encoding="utf-8") as f:
        f.write("module.exports = ")
        json.dump(data, f, ensure_ascii=False)
        f.write(";\n")

    size_kb = os.path.getsize(js_path) / 1024
    print(f"✓ {name}.js  ({size_kb:.0f} KB, {len(data)} items)")

print("\nDone. Now update request.js to load .js instead of .json.")