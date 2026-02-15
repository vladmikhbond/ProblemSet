
const timeRange = document.getElementById("timeRange");
const checkDiv = document.getElementById("checkDiv");
const stepTime = document.getElementById("stepTime");
const codeArea = document.getElementById('codeArea');
const canvas1 = document.getElementById('canvas1');

// константи LINK_SEP і CHECK_SEP у файлі trace_const.js
// константа track_in_base64 на веб сторінці

// розділяє трек на код и відповідь перевірки
const bytes = Uint8Array.from(atob(track_in_base64), c => c.charCodeAt(0));
const track =  new TextDecoder("utf-8").decode(bytes);
const screens = unfold(track);
const [codes, checks] = separate(screens);
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

// малює діаграму на канвасі
  let ctx = canvas1.getContext("2d");
  ctx.fillRect(10, 10, 100, 100);

// Розгортає трек у масив знімків.
//
function unfold(track) {
    if (!track) 
        return [];

    let shots = [];
    track = track.slice(1);  // remove 1-st selector
    const chain = track.split(LINK_SEP);

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
            shot = left + match[2] + right               
        } 
        shots.push(shot);
    }
    return shots;
}

// Розділяє кожен знімок на код і повідомлення перевірки.
//
function separate(shots) {
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


  
  // Синхронізує розміри textarea і canvas
  //  
  function syncSize() {
    const rect = codeArea.getBoundingClientRect();
    canvas1.width = codeArea.offsetWidth;
    canvas1.height = codeArea.offsetHeight;
    // CSS-розмір
    canvas1.style.width = codeArea.offsetWidth + 'px';
    canvas1.style.height = codeArea.offsetHeight + 'px';
  }


