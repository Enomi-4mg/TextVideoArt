export function brightnessToChar(brightness,charset,invert=false){const chars=Array.from(charset);if(chars.length<2||!Number.isFinite(brightness))throw Error("invalid conversion input");const i=Math.floor(Math.max(0,Math.min(255,brightness))/255*(chars.length-1));return chars[invert?chars.length-1-i:i];}
export function imageDataToTextFrame(imageData,width,height,charset,invert=false,preset="raw"){
 if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1||imageData.data.length!==width*height*4)throw Error("invalid image dimensions");
 const gray=new Float64Array(width*height);for(let i=0;i<gray.length;i++){const d=imageData.data;gray[i]=0.299*d[i*4]+0.587*d[i*4+1]+0.114*d[i*4+2];}
 const sample=(x,y)=>gray[Math.max(0,Math.min(height-1,y))*width+Math.max(0,Math.min(width-1,x))];
 const rows=[];for(let y=0;y<height;y++){let row="";for(let x=0;x<width;x++){let b=gray[y*width+x];if(preset==="Clean")b=Math.max(0,Math.min(255,(b-128)*1.1+128));if(preset==="Edge"){const gx=-sample(x-1,y-1)+sample(x+1,y-1)-2*sample(x-1,y)+2*sample(x+1,y)-sample(x-1,y+1)+sample(x+1,y+1);const gy=-sample(x-1,y-1)-2*sample(x,y-1)-sample(x+1,y-1)+sample(x-1,y+1)+2*sample(x,y+1)+sample(x+1,y+1);b=Math.min(255,Math.hypot(gx,gy));}row+=brightnessToChar(b,charset,invert);}rows.push(row);}return rows.join("\n");
}
