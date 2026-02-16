
const timeRange = document.getElementById("timeRange");
const checkDiv = document.getElementById("checkDiv");
const stepTime = document.getElementById("stepTime");
const codeArea = document.getElementById('codeArea');
const canvas1 = document.getElementById('canvas1');

// константи TRACE_INTERVAL, LINK_SEP і CHECK_SEP у файлі trace_const.js
// константа track_in_base64 на веб сторінці

// Розгортає трек у масив знімків.
//
class TrackDecoder {

    constructor(track) {
        this.track = track;
    }

    decode() {
        if (!this.track) 
            return [];

        let shots = [];
        const chain = this.track.split(LINK_SEP);

        let shot = "";
        const regex = /(\d+)\|(.*)\|(\d+)/s

        for (let link of chain) {
            if (link) {
                const match = regex.exec(link);
                if (!match) {
                    throw Error("ERROR: wrong format of trace");
                } 
                const l = +match[1];
                const r = +match[3];
                const left = shot.slice(0, l);
                const right = r ? shot.slice(-r) : "";
                shot = left + match[2] + right;       
            } 
            shots.push(shot);
        }
        return shots;
    }

    decode2() {
        return TrackDecoder.separate(this.decode());
    }

    // Розділяє масив знімків на масив кодів і масив повідомлень.
    static separate(shots) {
        let codes = [], checks = [];
        for (let screen of shots) {
            if (screen.indexOf(CHECK_SEP) != -1) {
                let [co, ch] = screen.split(CHECK_SEP);
                codes.push(co);
                checks.push(ch);
            } else {
                codes.push(screen);
                checks.push("");
            }
        }
        return [codes, checks];
    }
}


// декодує трек 
const bytes = Uint8Array.from(atob(track_in_base64), c => c.charCodeAt(0));
const track =  new TextDecoder("utf-8").decode(bytes);

const tracer = new TrackDecoder(track);

// розділяє трек на код и відповідь перевірки
const [codes, checks] = tracer.decode2();

// додає в трек останню ланку
codes.push(codeArea.value);
checks.push(checkDiv.innerHTML);

// готує слайдер
timeRange.max = codes.length - 1;
timeRange.value = timeRange.max;
timeRange.focus();

// Anime
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
  const n = codes.length, cH = canvas1.height, cW = canvas1.width;
  const w = cW / n;
  const maxCodeLength = Math.max(...codes.map(x => x.length));
  const dy = cH / maxCodeLength;

  const ctx = canvas1.getContext("2d");
  ctx.fillStyle = "#ff000040"; 
  ctx.strokeStyle = "#ff0000ff"; 
  ctx.lineWidth = 0.25;

  for (let i = 0; i < n; i++) {
    const x = w * i, y = cH - dy * codes[i].length + 5;
    const h = i > 0 ? (codes[i].length - codes[i-1].length) * dy : 0;
    if (h) {
       ctx.fillRect(x, y, w, h);
    } else {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + w, y);
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


