const checkButton = document.getElementById("checkButton");
const checkImage = document.getElementById("checkImage");
const problemId = document.getElementById("problemId");
const message = document.getElementById("message");

// константи LINK_SEP і CHECK_SEP у файлі trace_const.js

const TRACE_MSEC = 3000;

// Відстеження треку рішення
class SolveTracer {
    constructor() {
        this.prevSolving = "";
        this.track = "";
    }

    add(solving) {
        this.track += LINK_SEP + this.diff(solving);
        this.prevSolving = solving;
    }

    diff(s2)  {
        let s1 = this.prevSolving;
        // співпадіння 
        if (s1 === s2)
            return "";
        
        let l = 0, r = 0;
        while (s1[l] === s2[l]) l++;
        while (s1[s1.length - 1 - r] === s2[s2.length - 1 - r]) r++;
        let mid = r ? s2.slice(l, -r) : s2.slice(l);
        return `${l}|${mid}|${r}`;
    }

}

const tracer = new SolveTracer();

tracer.add(editor.getValue());

setInterval(() => {
    tracer.add(editor.getValue());
}, TRACE_MSEC)



// Перевірка рішення
checkButton.addEventListener("click", async () => {
    const data = {
        problem_id: problemId.value,
        solving: editor.getValue(),
        track: tracer.track,
    };

    try {
        const response = await fetch("/check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error("HTTP error " + response.status);
        }

        // display check answer
        let check_mes = await response.json();           
        const ok = check_mes.slice(0, 4).indexOf("OK") != -1;
        message.style.color = ok ? "green" : "red";
        message.innerHTML = check_mes;
        checkImage.style.display = ok ? "inline" : "none";

        // extraordinary tracing
        check_mes = check_mes.length > 30 ? check_mes.slice(0, 30) + "..." : check_mes
        tracer.add(data.solving + CHECK_SEP + check_mes)

    } catch (err) {
        console.error("Request failed:", err);
        message.innerHTML = "Помилка: " + err.message;
    }
});

