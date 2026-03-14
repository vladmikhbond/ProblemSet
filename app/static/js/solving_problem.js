const checkButton = document.getElementById("checkButton");
const checkImage = document.getElementById("checkImage");
const problemId = document.getElementById("problemId");
const message = document.getElementById("message");

// константа TRACE_INTERVAL, класс Trace у файлі Trace.js

let trace = new Trace();
trace.addText(editor.getValue());

setInterval(() => {
    trace.addText(editor.getValue());
}, TRACE_INTERVAL);

// ---------------- Перевірка рішення 

checkButton.addEventListener("click", check);
    
async function check() {

    trace.addText(editor.getValue());
    
    const data = {
        problem_id: problemId.value,
        solving: editor.getValue(),
        trace: trace.toJson()
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
        
        // clear trace   
        trace = new Trace();     

    } catch (err) {
        console.error("Request failed:", err);
        message.innerHTML = "Помилка: " + err.message;
    }
}

// ----------------------------------- втрати фокусу
let fcounter = 0;

document.addEventListener("visibilitychange", async () => 
{
    if (document.visibilityState === "hidden") {
       fcounter += 1;
       trace.addComment("FOCUS LOST " + fcounter )
       check();
    }
});