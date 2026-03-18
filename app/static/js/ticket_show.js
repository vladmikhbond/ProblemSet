
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
const checks = pairs.map(p => p[1]);


// готує слайдер
timeRange.max = pairs.length - 1;
timeRange.value = timeRange.max;
timeRange.focus();

// Slide show
timeRange.addEventListener("change", (e) => {
    let i = timeRange.value;
    // code
    codeArea.value = codes[i];
    checkDiv.innerHTML = checks[i];
    codeArea.className = checks[i].indexOf('OK') != -1 ? "ok" : "wrong";
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
  const n = pairs.length, canH = canvas1.height, cW = canvas1.width;
  const w = cW / n;
  const maxCodeLength = Math.max(...pairs.map(p => p[0].length));
  const dy = canH / maxCodeLength;

  const ctx = canvas1.getContext("2d");


  ctx.lineWidth = 0.5;
  ctx.fillStyle = "#0000FF40"; 
  ctx.strokeStyle = "#0000FFFF"; 

  for (let i = 0; i < n; i++) {
    // diagram
    const x = w * i, y = canH - dy * codes[i].length + 5;
    const h = i > 0 ? (codes[i].length - codes[i-1].length) * dy : 0;

    if (h) {
       ctx.fillRect(x, y, w, h);
    } else {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + w, y);
        ctx.stroke();
    }
    // checks
    if (checks[i]) {
        ctx.save()
        ctx.strokeStyle = 
            checks[i].indexOf("OK") > -1    ? "green" : 
            checks[i].indexOf("FOCUS") > -1 ? "black" :
            checks[i].indexOf("TAB") > -1   ? "blue" :
            /* else */                        "red";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x + w/2, canH * 0.75);
        ctx.lineTo(x + w/2, canH);
        ctx.stroke();
        ctx.restore();
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


