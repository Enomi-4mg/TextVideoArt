import JSZip from "../../vendor/jszip.esm.js";
export const LIMITS = Object.freeze({manifest:1048576, frame:4194304, archive:67108864, total:134217728, cells:16777216});
const object = v => v !== null && typeof v === "object" && !Array.isArray(v);
export const forbiddenText = s => /[\u0000-\u001f\u007f-\u009f]/u.test(s) || Array.from(s).some(c => {const n=c.codePointAt(0);return n>=0xd800&&n<=0xdfff;});
const finiteTree = v => typeof v==="number" ? Number.isFinite(v) : Array.isArray(v) ? v.every(finiteTree) : object(v) ? Object.values(v).every(finiteTree) : true;
const surrogate = v => typeof v === "string" ? Array.from(v).some(c=>{const n=c.codePointAt(0);return n>=0xd800&&n<=0xdfff;}) : Array.isArray(v) ? v.some(surrogate) : object(v) ? Object.entries(v).some(([k,w])=>surrogate(k)||surrogate(w)) : false;
export function framePath(i) {if(!Number.isInteger(i)||i<0||i>999999)throw Error("frame index out of range");return "frames/"+String(i).padStart(6,"0")+".txt";}
export function normalizeFrameText(s){s=s.replace(/(?:\r\n|\r|\n)$/u, "");return s ? s.split(/\r\n|\r|\n/u) : [];}
export function validateManifest(m){
 const e=[]; if(!object(m))return ["manifest must be an object"];if(!finiteTree(m))return ["manifest contains non-finite numbers"];if(surrogate(m))return ["manifest contains an invalid Unicode scalar"];
 const required={format:"string",format_name:"string",version:"string",width:"number",height:"number",fps:"number",frame_count:"number",duration:"number",charset:"string",invert:"boolean",encoding:"string",color_mode:"string",frame_format:"string",frames_path:"string"};
 for(const [k,t] of Object.entries(required)){if(!Object.hasOwn(m,k))e.push("missing manifest field: "+k);else if(typeof m[k]!==t)e.push("manifest field "+k+" must be a "+t);}
 for(const k of ["title","created_by","author","description","license","created_at"])if(k in m && typeof m[k]!=="string")e.push(k+" must be a string");
 for(const k of ["source","conversion"])if(k in m&&!object(m[k]))e.push(k+" must be an object");
 for(const k of ["tags","markers"])if(k in m&&!Array.isArray(m[k]))e.push(k+" must be an array");
 if(e.length)return e;
 for(const [k,v] of Object.entries({format:"TVA",format_name:"Text Video Art",version:"0.1.0",encoding:"utf-8",color_mode:"none",frame_format:"plain_text",frames_path:"frames/"}))if(m[k]!==v)e.push(k+" must be "+JSON.stringify(v));
 for(const k of ["width","height","frame_count"])if(!Number.isSafeInteger(m[k])||m[k]<=0)e.push(k+" must be a positive integer");
 for(const k of ["fps","duration"])if(!Number.isFinite(m[k])||m[k]<=0)e.push(k+" must be finite and positive");
 if(m.frame_count>1000000)e.push("frame_count limit exceeded");
 if(m.width>4096||m.height>4096||m.width*m.height*m.frame_count>LIMITS.cells)e.push("reader cell limit exceeded");
 if(Array.from(m.charset).length<2||forbiddenText(m.charset))e.push("invalid charset");
 for(const t of m.tags||[])if(typeof t!=="string"||!t)e.push("tags must contain non-empty strings");
 for(const marker of m.markers||[]){if(!object(marker)){e.push("marker must be an object");continue;}if(typeof marker.label!=="string"||!marker.label)e.push("marker label must be non-empty");if(!Number.isInteger(marker.frame)||marker.frame<0||marker.frame>=m.frame_count)e.push("marker frame out of range");}
 return e;
}
export function validateFrame(text,m,name="frame"){
 const rows=normalizeFrameText(text), e=[];
 if(rows.length!==m.height)e.push(name+" has "+rows.length+" lines, expected "+m.height+".");
 for(const [i,row] of rows.entries()){if(forbiddenText(row))e.push(name+" contains forbidden control characters");if(Array.from(row).length!==m.width)e.push(name+" line "+(i+1)+" has "+Array.from(row).length+" characters, expected "+m.width+".");}return e;
}
// Read the central directory before JSZip can sanitize paths or collapse duplicates.
export function inspectZip(bytes){
 const d=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);let end=-1;
 for(let i=bytes.length-22;i>=Math.max(0,bytes.length-65557);i--)if(d.getUint32(i,true)===0x06054b50 && i+22+d.getUint16(i+20,true)===bytes.length){end=i;break;}
 if(end<0)throw Error("invalid ZIP directory");
 const count=d.getUint16(end+10,true), size=d.getUint32(end+12,true), offset=d.getUint32(end+16,true);
 if(d.getUint16(end+4,true)||d.getUint16(end+6,true)||d.getUint16(end+8,true)!==count||count===65535||offset+size!==end)throw Error("unsupported ZIP directory");
 let p=offset,total=0;const names=new Set();names.crcs=new Map();const decoder=new TextDecoder("utf-8",{fatal:true,ignoreBOM:true});
 for(let i=0;i<count;i++){
 if(p+46>end||d.getUint32(p,true)!==0x02014b50)throw Error("invalid ZIP entry");
 const n=d.getUint16(p+28,true), extra=d.getUint16(p+30,true), comment=d.getUint16(p+32,true), unpacked=d.getUint32(p+24,true);
 if(p+46+n+extra+comment>end)throw Error("invalid ZIP entry length");
 const name=decoder.decode(bytes.subarray(p+46,p+46+n));
 if(!name||name.startsWith("/")||name.includes("\\")||/^[a-z]:/i.test(name)||name.replace(/\/$/,"").split("/").some(s=>!s||s==="."||s===".."))throw Error("unsafe ZIP path: "+name);
 if(names.has(name))throw Error("duplicate ZIP entry: "+name);names.add(name);names.crcs.set(name,d.getUint32(p+16,true));
 if(d.getUint16(p+8,true)&1)throw Error("encrypted ZIP is unsupported");
 if(unpacked>(name==="manifest.json"?LIMITS.manifest:LIMITS.frame))throw Error("reader entry limit exceeded");total+=unpacked;
 p+=46+n+extra+comment;
 }
 if(p!==end||total>LIMITS.total)throw Error("reader archive limit exceeded");return names;
}
const crcTable = Uint32Array.from({length:256}, (_, n) => {for(let k=0;k<8;k++)n=(n&1)?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
async function readEntry(entry,limit,expectedCrc){
 return new Promise((resolve,reject)=>{let total=0,chunks=[],crc=0xffffffff;const stream=entry.internalStream("uint8array");stream.on("data",chunk=>{total+=chunk.length;if(total>limit){stream.pause();chunks=[];reject(Error("reader entry limit exceeded"));}else {for(const byte of chunk)crc=crcTable[(crc^byte)&255]^(crc>>>8);chunks.push(chunk);}});stream.on("error",reject);stream.on("end",()=>{if(total>limit)return;if(((crc^0xffffffff)>>>0)!==expectedCrc){reject(Error("ZIP CRC mismatch"));return;}const b=new Uint8Array(total);let p=0;for(const c of chunks){b.set(c,p);p+=c.length;}try{resolve(new TextDecoder("utf-8",{fatal:true,ignoreBOM:true}).decode(b));}catch(e){reject(Error("entry is not valid UTF-8"));}});stream.resume();});
}
export async function loadTvaArchive(input){
 if(typeof Blob!=="undefined" && input instanceof Blob){if(input.size>LIMITS.archive)throw Error("reader archive limit exceeded");input=await input.arrayBuffer();}
 const bytes=input instanceof Uint8Array?input:new Uint8Array(input);if(bytes.length>LIMITS.archive)throw Error("reader archive limit exceeded");
 const names=inspectZip(bytes);const zip=await JSZip.loadAsync(bytes);for(const [name,item] of Object.entries(zip.files)){if(!item.dir && (!names.has(name) || (item.unsafeOriginalName && item.unsafeOriginalName!==name)))throw Error("ZIP name differs from central directory: "+name);}const entry=zip.file("manifest.json");if(!entry)throw Error("manifest.json is missing");
 const manifest=JSON.parse(await readEntry(entry,LIMITS.manifest,names.crcs.get("manifest.json")));const errors=validateManifest(manifest);if(errors.length)throw Error(errors.join("\n"));
 for(const name of names){if(name.startsWith("frames/")&&name!=="frames/"){const m=/^frames\/([0-9]{6})\.txt$/.exec(name);if(!m)throw Error("invalid frame file name: "+name);if(Number(m[1])>=manifest.frame_count)throw Error("out-of-range frame: "+name);}}
 const frames=[];for(let i=0;i<manifest.frame_count;i++){const name=framePath(i),entry=zip.file(name);if(!entry)throw Error("missing frame: "+name);const text=await readEntry(entry,LIMITS.frame,names.crcs.get(name));const e=validateFrame(text,manifest,name);if(e.length)throw Error(e.join("\n"));frames.push(text);}return {manifest,frames};
}
export const validateArchive=loadTvaArchive;
export const loadTvaFile=loadTvaArchive;
export async function loadTvaUrl(url){const response=await fetch(url);if(!response.ok)throw Error("failed to load TVA archive: "+response.status);const reader=response.body?.getReader();if(!reader)return loadTvaArchive(await response.arrayBuffer());let size=0,chunks=[];for(;;){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>LIMITS.archive){await reader.cancel();throw Error("reader archive limit exceeded");}chunks.push(value);}const bytes=new Uint8Array(size);let p=0;for(const c of chunks){bytes.set(c,p);p+=c.length;}return loadTvaArchive(bytes);}
