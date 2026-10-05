export function computeLayout({columns,rows,cellAspect=0.5,cellHeight=16,surface,fit="contain",alignX=0.5,alignY=0.5}) {
 if(!Number.isInteger(columns)||columns<1||!Number.isInteger(rows)||rows<1||![cellAspect,cellHeight,surface.width,surface.height].every(v=>Number.isFinite(v)&&v>0)||![alignX,alignY].every(v=>Number.isFinite(v)&&v>=0&&v<=1)||!["native","contain","cover"].includes(fit))throw Error("invalid layout");
 const w=columns*cellHeight*cellAspect,h=rows*cellHeight;
 const scale=fit==="native"?1:Math[fit==="cover"?"max":"min"](surface.width/w,surface.height/h);
 return {x:(surface.width-w*scale)*alignX,y:(surface.height-h*scale)*alignY,width:w*scale,height:h*scale,cellWidth:cellHeight*cellAspect*scale,cellHeight:cellHeight*scale};
}

export function canvasSurface(width, height, ratio = 1) {
 if (![width, height, ratio].every(v => Number.isFinite(v) && v > 0)) return null;
 return {width: Math.max(1, Math.round(width * ratio)), height: Math.max(1, Math.round(height * ratio)), ratio};
}
