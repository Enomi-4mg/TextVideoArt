export const RECORDING_TYPES=["video/mp4;codecs=avc1.42E01E","video/mp4","video/webm;codecs=vp9","video/webm;codecs=vp8","video/webm"];
export function selectRecordingType(recorder){return recorder?.isTypeSupported ? RECORDING_TYPES.find(t=>recorder.isTypeSupported(t))||null : null;}
export function recordingFormat(mime){const type=mime.toLowerCase().split(";")[0];if(type==="video/mp4")return {extension:"mp4",label:"MP4"};if(type==="video/webm")return {extension:"webm",label:"WebM"};throw Error("Unknown recording container; save PNG instead");}
export function cardSize(aspect){if(aspect==="9:16")return {width:720,height:1280};if(aspect==="16:9")return {width:1280,height:720};if(aspect==="1:1")return {width:1080,height:1080};throw Error("Invalid card aspect");}
