import {readFile,writeFile,mkdtemp} from "node:fs/promises";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {pathToFileURL} from "node:url";
const cache=new Map(),directory=await mkdtemp(join(tmpdir(),"tvart-js-tests-"));let sequence=0;
export async function loadModule(url){const key=String(url);if(cache.has(key))return import(cache.get(key));let source=await readFile(url,"utf8");const imports=[...source.matchAll(/(?:from\s*|import\s*)["'](\.[^"']+)["']/g)];for(const match of imports){const dep=new URL(match[1],url);await loadModule(dep);source=source.replace(match[0],match[0].replace(match[1],cache.get(String(dep))));}const target=pathToFileURL(join(directory,String(sequence++)+".mjs")).href;await writeFile(new URL(target),source);cache.set(key,target);return import(target);}
