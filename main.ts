import { copyFile, mkdir } from "node:fs/promises";

await mkdir("/output", { recursive: true });
await copyFile(new URL("./POST.json", import.meta.url), "/output/POST.json");
