import sys
import subprocess
import os

MCPORTER_CFG = os.environ.get("MCPORTER_CFG", "C:/Users/35864/.workbuddy/mcporter/mcporter.json")
NODE = "C:/Users/35864/.workbuddy/binaries/node/versions/22.22.2/node.exe"
MC = "C:/Users/35864/.workbuddy/binaries/node/workspace/node_modules/mcporter/dist/index.js"

sql_file = sys.argv[1]
chunk_name = os.path.basename(sql_file)

with open(sql_file, "r", encoding="utf-8") as f:
    sql = f.read()

result = subprocess.run(
    [NODE, MC, "--config", MCPORTER_CFG,
     "call", "cloudbase.managePgDatabase",
     "action=execute", f"sql={sql}", "confirm=true",
     "--output", "json"],
    capture_output=True, text=True, timeout=300
)

output = result.stdout + result.stderr
if "isError" in output and "false" in output.split("isError", 1)[1].split("\n", 1)[0]:
    print(f"{chunk_name}: OK")
elif "isError" in output and "true" in output.split("isError", 1)[1].split("\n", 1)[0]:
    # Extract error message
    for line in output.split("\n"):
        if "errorMessage" in line or "error" in line.lower() and "isError" not in line:
            print(f"{chunk_name}: FAIL - {line.strip()[:200]}")
            break
    else:
        print(f"{chunk_name}: FAIL (isError=true)")
else:
    # Try to find error info
    if "Argument list too long" in output:
        print(f"{chunk_name}: FAIL - Argument list too long ({len(sql)} bytes)")
    elif "Error" in output or "error" in output.lower():
        print(f"{chunk_name}: FAIL - {output[-300:]}")
    else:
        print(f"{chunk_name}: OK")