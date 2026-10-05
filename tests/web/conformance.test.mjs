import {test} from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {loadModule} from "./load-module.mjs";
const root=new URL("../../",import.meta.url);
const tva=await loadModule(new URL("web/src/lib/tva.js",root));
const {default:JSZip}=await loadModule(new URL("web/vendor/jszip.esm.js",root));
const fixture=JSON.parse(await readFile(new URL("tests/fixtures/conformance/cases.json",root),"utf8"));
for(const c of fixture.cases)test("conformance: "+c.id,async()=>{
 const zip=new JSZip();zip.file("manifest.json",c.manifestBytes?Buffer.from(c.manifestBytes,"base64"):c.rawManifest??JSON.stringify({...fixture.base,...c.manifest}));
 const frames=c.frames??["abc\ndef\n"];frames.forEach((f,i)=>zip.file(tva.framePath(i),f));if(c.frameBytes)zip.file(tva.framePath(0),Buffer.from(c.frameBytes,"base64"));for(const [n,s]of c.extra||[])zip.file(n,s);
 if(c.id==="duplicate"){
 zip.file("frames/000001.txt","abc\ndef\n");const bytes=await zip.generateAsync({type:"uint8array"});const needle=new TextEncoder().encode("frames/000001.txt");for(let p=0;p<bytes.length-needle.length;p++){if(needle.every((n,i)=>bytes[p+i]===n))bytes[p+12]=48;}await assert.rejects(tva.loadTvaArchive(bytes),/duplicate ZIP entry/);return;
 }
 const bytes=await zip.generateAsync({type:"uint8array"});if(c.corruptCrc){const view=new DataView(bytes.buffer);for(let p=0;p<bytes.length-46;p++)if(view.getUint32(p,true)===0x02014b50){view.setUint32(p+16,0,true);break;}}if(c.valid)await tva.loadTvaArchive(bytes);else await assert.rejects(tva.loadTvaArchive(bytes));
});
test("existing landing archive",async()=>{const result=await tva.loadTvaArchive(await readFile(new URL("web/samples/landing-demo.tva",root)));assert.ok(result.frames.length);});
test("reader entry limit before decompression",async()=>{const z=new JSZip();z.file("manifest.json"," ".repeat(tva.LIMITS.manifest+1));await assert.rejects(tva.loadTvaArchive(await z.generateAsync({type:"uint8array",compression:"DEFLATE"})),/reader entry limit/);});
