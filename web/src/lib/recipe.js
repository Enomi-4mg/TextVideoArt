import {PRESETS} from "./presets.js";
import {forbiddenText} from "./tva.js";
export const DEFAULT_RECIPE={format:"tvart-recipe",version:1,preset:"Clean",columns:100,charset:PRESETS.Clean.charset,invert:false,aspect_correction:0.5,theme:{foreground:PRESETS.Clean.foreground,background:PRESETS.Clean.background},fit:"contain",motion:{aspect:"1:1",seconds:5}};
export function validateRecipe(v){
 if(!v||typeof v!=="object"||Array.isArray(v)||v.format!=="tvart-recipe"||v.version!==1)throw Error("Unsupported recipe format or version");
 if(!Object.hasOwn(PRESETS,v.preset)||!Number.isInteger(v.columns)||v.columns<4||v.columns>240||typeof v.charset!=="string"||Array.from(v.charset).length<2||Array.from(v.charset).length>256||forbiddenText(v.charset)||typeof v.invert!=="boolean"||!Number.isFinite(v.aspect_correction)||v.aspect_correction<0.25||v.aspect_correction>1)throw Error("Invalid recipe conversion settings");
 if(!v.theme||![v.theme.foreground,v.theme.background].every(c=>typeof c==="string"&&/^#[0-9a-f]{6}$/i.test(c))||!["native","contain","cover"].includes(v.fit)||!v.motion||!["1:1","9:16","16:9"].includes(v.motion.aspect)||!Number.isFinite(v.motion.seconds)||v.motion.seconds<0.1||v.motion.seconds>5)throw Error("Invalid recipe output settings");
 // Explicit allowlist: source material, names, paths and unknown fields never escape.
 return {format:"tvart-recipe",version:1,preset:v.preset,columns:v.columns,charset:v.charset,invert:v.invert,aspect_correction:v.aspect_correction,theme:{foreground:v.theme.foreground.toLowerCase(),background:v.theme.background.toLowerCase()},fit:v.fit,motion:{aspect:v.motion.aspect,seconds:v.motion.seconds}};
}
export function parseRecipe(text){if(new TextEncoder().encode(text).length>8192)throw Error("Recipe is too large");return validateRecipe(JSON.parse(text));}
export function encodeRecipe(v){const bytes=new TextEncoder().encode(JSON.stringify(validateRecipe(v)));return btoa(String.fromCharCode(...bytes)).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");}
export function decodeRecipe(encoded){if(encoded.length>11000||!/^[A-Za-z0-9_-]+$/.test(encoded))throw Error("Invalid recipe link");return parseRecipe(new TextDecoder("utf-8",{fatal:true}).decode(Uint8Array.from(atob(encoded.replace(/-/g,"+").replace(/_/g,"/")),c=>c.charCodeAt(0))));}
