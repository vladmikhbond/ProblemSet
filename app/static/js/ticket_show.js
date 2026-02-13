const codeArea = document.getElementById("codeArea");
const timeRange = document.getElementById("timeRange");
const checkDiv = document.getElementById("checkDiv");

// константи LINK_SEP і CHECK_SEP у файлі trace_const.js

// decode track from track_in_base64
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

function unfold(track) {
    if (!track) 
        return [];
    let result = [];

    const chain = track.split(LINK_SEP);

    let screen = "";
    const regex = /(\d+)\|(.*)\|(\d+)/s

    for (let link of chain) {
        if (link) {
            const m = regex.exec(link);
            if (!m) {
                throw Error("ERROR: wrong format of trace");
            } 
            const l = +m[1];
            const r = +m[3];
            const left = screen.slice(0, l);
            const right = r ? screen.slice(-r) : "";
            screen = left + m[2] + right               
        } 
        result.push(screen);
    }
    return result;
}

function separate(screens) {
    let codes = [], checks = [];
    for (let screen of screens) {
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
  

