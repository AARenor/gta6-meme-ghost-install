import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const postPath = fileURLToPath(new URL("./POST.json", import.meta.url));
const outDir = process.env.OUTPUT_DIR ?? "/output";

let bytes: Buffer;
try {
	bytes = await readFile(postPath);
} catch (cause) {
	if ((cause as NodeJS.ErrnoException).code !== "ENOENT") throw cause;
	throw new Error(`POST.json is missing: no file at ${postPath}`, { cause });
}

const target = join(outDir, "POST.json");

await mkdir(outDir, { recursive: true });
await writeFile(target, bytes);

console.log(`copied ${bytes.length} bytes of POST.json to ${target}`);
