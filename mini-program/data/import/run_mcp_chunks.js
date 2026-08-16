const { spawn } = require("child_process");
const path = require("path");

const CLOUDBASE_MCP = "G:/codex/npm-cache/_npx/88d9f76c32260533/node_modules/@cloudbase/cloudbase-mcp/dist/cli.cjs";
const NODE = "C:/Users/35864/.workbuddy/binaries/node/versions/22.22.2/node.exe";

const CHUNK_DIR = "C:/Users/35864/Desktop/全国大学生18届/mini-program/data/import/chunks2";
const CHUNKS = process.argv.slice(2);

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function processChunk(fileName) {
  const filePath = path.join(CHUNK_DIR, fileName);
  const fs = require("fs");
  const sql = fs.readFileSync(filePath, "utf-8");

  return new Promise((resolve, reject) => {
    const proc = spawn(NODE, [CLOUDBASE_MCP], {
      stdio: ["pipe", "pipe", "pipe"]
    });

    let stdout = "";
    let stderr = "";
    let responseReceived = false;
    const timeout = setTimeout(() => {
      proc.kill();
      reject(new Error(`Timeout for ${fileName}`));
    }, 300000);

    proc.stdout.on("data", (data) => {
      stdout += data.toString();
      const lines = stdout.split("\n");
      for (const line of lines) {
        if (line.trim() && !responseReceived) {
          try {
            const msg = JSON.parse(line);
            if (msg.result && msg.id === 2) {
              responseReceived = true;
              clearTimeout(timeout);
              proc.kill();
              const result = msg.result;
              const isError = result.isError || result.content?.some(c => c.type === "text" && c.text?.includes("error"));
              if (isError) {
                resolve({ file: fileName, ok: false, msg: JSON.stringify(result).substring(0, 500) });
              } else {
                resolve({ file: fileName, ok: true });
              }
            }
          } catch (e) {
            // not JSON yet
          }
        }
      }
    });

    proc.stderr.on("data", (data) => { stderr += data.toString(); });

    // Initialize
    proc.stdin.write(JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        clientInfo: { name: "sql-runner", version: "1.0" }
      }
    }) + "\n");

    // Wait for initialize response, then send notifications/initialized and the tool call
    setTimeout(() => {
      proc.stdin.write(JSON.stringify({
        jsonrpc: "2.0",
        method: "notifications/initialized"
      }) + "\n");

      setTimeout(() => {
        proc.stdin.write(JSON.stringify({
          jsonrpc: "2.0",
          id: 2,
          method: "tools/call",
          params: {
            name: "managePgDatabase",
            arguments: {
              action: "execute",
              sql: sql,
              confirm: true
            }
          }
        }) + "\n");
      }, 500);
    }, 2000);
  });
}

async function main() {
  for (const f of CHUNKS) {
    try {
      const result = await processChunk(f);
      if (result.ok) {
        console.log(`${f}: OK`);
      } else {
        console.log(`${f}: FAIL - ${result.msg}`);
      }
    } catch (err) {
      console.log(`${f}: ERROR - ${err.message}`);
    }
    await sleep(1000);
  }
}

main().catch(console.error);