// Capture frames of a host page that runs an original component snippet.
// Chrome is the renderer. This file does not reimplement the component.

import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";

const [htmlUrl, outDir, framesStr, fpsStr, timelineName, portStr] = process.argv.slice(2);
const frames = Number(framesStr);
const fps = Number(fpsStr);
const port = Number(portStr);
mkdirSync(outDir, { recursive: true });

const chrome = spawn(
  "google-chrome",
  [
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--hide-scrollbars",
    "--no-first-run",
    "--disable-extensions",
    "--disable-background-networking",
    "--allow-file-access-from-files",
    "--force-device-scale-factor=1",
    "--window-size=1080,1128",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${outDir}/chrome-profile`,
    "about:blank",
  ],
  { stdio: ["ignore", "pipe", "pipe"] },
);

let chromeLog = "";
chrome.stderr.on("data", (buf) => {
  chromeLog += buf.toString();
});
chrome.stdout.on("data", (buf) => {
  chromeLog += buf.toString();
});

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForDebugger() {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) return await response.json();
    } catch {
      // Chrome is still starting.
    }
    await sleep(100);
  }
  throw new Error(`chrome debugger did not start\n${chromeLog.slice(-800)}`);
}

const version = await waitForDebugger();
const browser = new WebSocket(version.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  browser.addEventListener("open", resolve, { once: true });
  browser.addEventListener("error", () => reject(new Error("devtools websocket failed")), { once: true });
});

let nextId = 0;
const pending = new Map();
browser.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (!message.id || !pending.has(message.id)) return;
  const { resolve, reject } = pending.get(message.id);
  pending.delete(message.id);
  if (message.error) reject(new Error(JSON.stringify(message.error)));
  else resolve(message.result || {});
});

function send(method, params = {}, sessionId) {
  const id = ++nextId;
  const payload = { id, method, params };
  if (sessionId) payload.sessionId = sessionId;
  browser.send(JSON.stringify(payload));
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
  });
}

try {
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  await send("Page.enable", {}, sessionId);
  await send("Runtime.enable", {}, sessionId);
  await send(
    "Emulation.setDeviceMetricsOverride",
    { width: 1080, height: 1128, deviceScaleFactor: 1, mobile: false },
    sessionId,
  );
  await send(
    "Emulation.setDefaultBackgroundColorOverride",
    { color: { r: 0, g: 0, b: 0, a: 0 } },
    sessionId,
  );
  await send("Page.navigate", { url: htmlUrl }, sessionId);
  const ready = await send(
    "Runtime.evaluate",
    {
      expression:
        "document.fonts.ready.then(() => { if (!window.__hfReady) throw new Error('host not ready'); return true; })",
      awaitPromise: true,
      returnByValue: true,
    },
    sessionId,
  );
  if (ready.exceptionDetails) {
    throw new Error(JSON.stringify(ready.exceptionDetails));
  }
  for (let index = 0; index < frames; index += 1) {
    const time = index / fps;
    const sought = await send(
      "Runtime.evaluate",
      {
        expression: `(() => { window.__timelines[${JSON.stringify(timelineName)}].seek(${time}); return true; })()`,
        returnByValue: true,
      },
      sessionId,
    );
    if (sought.exceptionDetails) throw new Error(JSON.stringify(sought.exceptionDetails));
    const shot = await send("Page.captureScreenshot", { format: "png" }, sessionId);
    writeFileSync(`${outDir}/f${String(index).padStart(4, "0")}.png`, Buffer.from(shot.data, "base64"));
  }
  writeFileSync(`${outDir}/chrome-version.txt`, `${version.Browser || ""}\n`);
} finally {
  browser.close();
  chrome.kill("SIGKILL");
}
