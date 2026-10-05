import {computeLayout} from "./layout.js";
export class CanvasFrameRenderer {
 constructor(target,options={}){this.target=target;this.options=options;this.frame="";}
 render(frame){this.frame=frame;const rows=Array.isArray(frame)?frame: String(frame).replace(/(?:\r\n|\r|\n)$/u,"").split(/\r\n|\r|\n/u);const chars=rows.map(s=>Array.from(s));const columns=Math.max(1,...chars.map(s=>s.length));const c=this.target.getContext("2d"),o=this.options;const l=computeLayout({columns,rows:rows.length,cellAspect:o.cellAspect||0.5,cellHeight:o.cellHeight||16,surface:{width:this.target.width,height:this.target.height},fit:o.fit||"contain"});
 c.setTransform(1,0,0,1,0,0);c.fillStyle=o.background||"#050505";c.fillRect(0,0,this.target.width,this.target.height);c.save();c.beginPath();c.rect(0,0,this.target.width,this.target.height);c.clip();c.font=(l.cellHeight*0.88)+"px "+(o.fontFamily||"monospace");c.fillStyle=o.foreground||"#ffffff";c.textAlign="center";c.textBaseline="middle";
 chars.forEach((row,y)=>row.forEach((char,x)=>c.fillText(char,l.x+(x+0.5)*l.cellWidth,l.y+(y+0.5)*l.cellHeight)));c.restore();return l;}
 clear(){this.frame="";this.target.getContext("2d").clearRect(0,0,this.target.width,this.target.height);}
}
