import {test} from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {loadModule} from "./load-module.mjs";
const root=new URL("../../",import.meta.url);
const tva=await loadModule(new URL("web/src/lib/tva.js",root));
const {default:JSZip}=await loadModule(new URL("web/vendor/jszip.esm.js",root));
const layout=await loadModule(new URL("web/src/lib/layout.js",root));
const conversion=await loadModule(new URL("web/src/lib/convert.js",root));
const layouts=JSON.parse(await readFile(new URL("tests/fixtures/layout_cases.json",root),"utf8"));for(const c of layouts)test("layout: "+c.fit,()=>{const l=layout.computeLayout({...c,surface:{width:c.width,height:c.height}});assert.deepEqual([l.x,l.y,l.cellWidth,l.cellHeight],c.expected);});
test("zero surface rejected",()=>assert.throws(()=>layout.computeLayout({columns:1,rows:1,surface:{width:0,height:10}})));
for(const c of JSON.parse(await readFile(new URL("tests/fixtures/conversion.json",root),"utf8")))test("brightness: "+JSON.stringify(c),()=>assert.equal(conversion.brightnessToChar(c.brightness,c.charset,c.invert),c.expected));
test("Sobel constant image and Unicode cells",()=>{const image={data:new Uint8ClampedArray([255,255,255,255,255,255,255,255])};assert.equal(conversion.imageDataToTextFrame(image,2,1,"😀😃",false,"raw"),"😃😃");assert.equal(conversion.imageDataToTextFrame(image,2,1," .#",false,"Edge"),"  ");});
test("canvas renderer draws code points and clips cover",async()=>{
 const {CanvasFrameRenderer}=await loadModule(new URL("web/src/lib/renderer-canvas.js",root));const calls=[];const ctx={setTransform(){},fillRect(){},save(){},beginPath(){},rect(){},clip(){calls.push("clip");},restore(){},clearRect(){calls.push("clear");},fillText(c,x,y){calls.push([c,x,y]);}};
 const renderer=new CanvasFrameRenderer({width:100,height:50,getContext:()=>ctx},{fit:"cover"});const l=renderer.render("😀a\n😀b\n");assert.equal(calls.filter(Array.isArray).length,4);assert.equal(calls[1][0],"😀");assert.ok(l.y<0);renderer.clear();assert.equal(calls.at(-1),"clear");
});

test("stage surface uses viewport and pixel density for native and cover",()=>{
 const surface=layout.canvasSurface(800,600,2);assert.deepEqual(surface,{width:1600,height:1200,ratio:2});
 const native=layout.computeLayout({columns:20,rows:10,cellHeight:32,surface,fit:"native"});
 assert.equal(native.cellHeight/surface.ratio,16);
 const cover=layout.computeLayout({columns:20,rows:10,cellHeight:32,surface,fit:"cover"});
 assert.ok(cover.width>=surface.width&&cover.height>=surface.height);assert.equal(layout.canvasSurface(0,600,2),null);
});
