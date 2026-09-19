import { defineConfig, devices } from "@playwright/test";
import { existsSync } from "node:fs";
import path from "node:path";

const repository = path.resolve(__dirname, "..");
const pythonCandidates = [path.join(repository, ".venv", "Scripts", "python.exe"), path.resolve(repository, "../../.venv/Scripts/python.exe"), path.join(repository, ".venv", "bin", "python")];
const python = process.env.PYTHON_EXECUTABLE || pythonCandidates.find(candidate => existsSync(candidate)) || "python";
const apiPort = Number(process.env.E2E_API_PORT || "8001");
const webPort = Number(process.env.E2E_WEB_PORT || "3001");

export default defineConfig({
  testDir: "./tests",
  timeout: 90_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: { baseURL: `http://127.0.0.1:${webPort}`, trace: "retain-on-failure", screenshot: "only-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `"${python}" -m uvicorn clausegraph.api:app --app-dir backend --host 127.0.0.1 --port ${apiPort}`,
      cwd: repository,
      url: `http://127.0.0.1:${apiPort}/api/health`,
      timeout: 60_000,
      reuseExistingServer: false,
      env: { ENVIRONMENT: "development", DATABASE_URL: "sqlite:///./.data/e2e.db", LOCAL_STORAGE_PATH: ".data/e2e-documents", PYTHONPATH: path.join(repository, "backend"), NVIDIA_API_KEY: "", GEMINI_API_KEY: "", ELEVENLABS_API_KEY: "", SPACES_BUCKET: "", SPACES_ACCESS_KEY_ID: "", SPACES_SECRET_ACCESS_KEY: "" },
    },
    {
      command: `npm run dev -- --port ${webPort}`,
      url: `http://127.0.0.1:${webPort}`,
      timeout: 120_000,
      reuseExistingServer: false,
      env: { API_INTERNAL_URL: `http://127.0.0.1:${apiPort}`, NEXT_TELEMETRY_DISABLED: "1" },
    },
  ],
});
