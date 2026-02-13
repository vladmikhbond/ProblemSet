const codeArea = document.getElementById("codeArea");
const timeRange = document.getElementById("timeRange");
const checkDiv = document.getElementById("checkDiv");

// константи LINK_SEP і CHECK_SEP у файлі trace_const.js
// константа track_in_base64 на веб сторінці

const bytes = Uint8Array.from(atob(track_in_base64), c => c.charCodeAt(0));
const track =  new TextDecoder("utf-8").decode(bytes);

const screens = unfold(track);
const [codes, checks] = separate(screens);
codes.push(codeArea.value);
checks.push(checkDiv.innerHTML);

timeRange.max = codes.length - 1;
timeRange.value = timeRange.max;

timeRange.addEventListener("change", (e) => {
    codeArea.value = codes[timeRange.value];
    checkDiv.innerHTML = checks[timeRange.value];
})

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
  

