export interface CanvasOptions {fit?: "native"|"contain"|"cover";cellAspect?:number;cellHeight?:number;foreground?:string;background?:string;fontFamily?:string;}
export declare class CanvasFrameRenderer {constructor(target:HTMLCanvasElement,options?:CanvasOptions);options:CanvasOptions;render(frame:string|string[]):unknown;clear():void;}
