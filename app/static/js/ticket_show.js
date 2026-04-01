
const timeRange = document.getElementById("timeRange");
const checkDiv = document.getElementById("checkDiv");
const stepTime = document.getElementById("stepTime");
const codeArea = document.getElementById('codeArea');
const canvas1 = document.getElementById('canvas1');

// константа TRACE_INTERVAL, класс Trace у файлі Trace.js
// константа track_in_base64 на веб сторінці ticket/show.html


// декодує трек з base64
const bytes = Uint8Array.from(atob(track_in_base64), c => c.charCodeAt(0));
let str =  new TextDecoder("utf-8").decode(bytes);

const trace = Trace.fromDifferences(JSON.parse(str));

// розділяє трек на код и відповідь перевірки
const pairs = trace.decode();
const codes = pairs.map(p => p[0]);
const comments = pairs.map(p => p[1]);


// готує слайдер
timeRange.max = pairs.length - 1;
timeRange.value = timeRange.max;
timeRange.focus();

// Slide show
timeRange.addEventListener("change", (e) => {
    let i = timeRange.value;
    // code
    codeArea.value = codes[i];
    checkDiv.innerHTML = comments[i];
    codeArea.className = comments[i].indexOf('OK') != -1 ? "ok" : "wrong";
    // time
    let s = i * 3 % 60, m = i * 3 / 60 | 0;
    stepTime.innerHTML = `+${m}' ${s}"`;
})

// Синхронізує розміри textarea і canvas
new ResizeObserver(syncSize).observe(codeArea);
syncSize();
window.addEventListener('resize', syncSize);

setTimeout(diagram, 0);

// малює діаграму на канвасі
function diagram() {
  const n = pairs.length, canvasH = canvas1.height, cW = canvas1.width;
  const w = cW / n;
  const maxCodeLength = Math.max(...pairs.map(p => p[0].length));
  const dy = canvasH / maxCodeLength;

  const ctx = canvas1.getContext("2d");


  ctx.lineWidth = 0.5;
  ctx.fillStyle = "#0000FF40"; 
  ctx.strokeStyle = "#0000FFFF"; 

  for (let i = 0; i < n; i++) {
    // diagram
    const x = w * i;
    const y = canvasH - dy * codes[i].length + 5;
    const h = i > 0 ? (codes[i].length - codes[i-1].length) * dy : 0;

    if (h) {
       ctx.fillRect(x, y, w, h);
    } else {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + w, y);
        ctx.stroke();
    }
    // comments
    if (comments[i]) {
        ctx.save()   
        if (comments[i].indexOf("OK") > -1) {
            drawCheck(x + w/2, canvasH * 0.9, "green");
        } else if (comments[i].indexOf("Wrong") > -1 || comments[i].indexOf("Error") > -1) {
            drawCheck(x + w/2, canvasH * 0.9, "red");
        } else if (comments[i].indexOf("FOCUS") > -1) {
            drawFocus(x + w/2, canvasH * 0.7, "darkred");
        } else if (comments[i].indexOf("TAB") > -1) {
            drawFocus(x + w/2, canvasH * 0.8, "black");
        } 
        ctx.restore();
    }
    // ----------------- inner functions --------------
    function drawCheck(x, y, color) {
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI*2);
        ctx.fill();
    }

    function drawFocus(x,  y, color) {
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x, canvasH);
        ctx.stroke();
    } 


  }  
  


}
  
// Синхронізує розміри textarea і canvas
//  
function syncSize() {
    const rect = codeArea.getBoundingClientRect();
    canvas1.width = codeArea.offsetWidth;
    canvas1.height = codeArea.offsetHeight;
    // CSS-розмір
    canvas1.style.width = codeArea.offsetWidth + 'px';
    canvas1.style.height = codeArea.offsetHeight + 'px';
    diagram();
}


