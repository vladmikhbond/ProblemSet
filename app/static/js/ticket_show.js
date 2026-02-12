function unfold(track, sep='\u0001') {
    if (!track) 
        return [];
    let result = [];
    const chain = track.split(sep);
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


const trackArea = document.getElementById("trackArea");
const screens = unfold(track);
trackArea.value = screens[screens.length - 1];

const timeRange = document.getElementById("timeRange");
timeRange.value = timeRange.max;
timeRange.addEventListener("change", (e) => {
    const i = screens.length * timeRange.value / timeRange.max | 0
    trackArea.value = screens[i];
})


