// При зміні чекбоксу будь-якого задачі оновлює список задач в елементі problem_ids
//
function reset_problem_ids(e) 
{   
    const input = e.target;
    const line = input.parentElement.textContent.trim();

    let arr = problem_ids.value.split('\n');
    arr = arr.filter(a => a).map(a => a.trim())  // remove empy strings
    if (input.checked) {
        // додати рядок
        arr.push(line);
    } else {
        // прибрати рядок
        let i = arr.indexOf(line);
        if (i != -1) arr.splice(i, 1);
    }
    problem_ids.value = arr.join('\n');
}


const openTime = document.getElementById("openTime");
const buttonNow = document.getElementById("buttonNow");

// Встановити в елемент openTime поточний київский час (формат YYYY-MM-DD HH:MM)
//
buttonNow.addEventListener("click", (e) => {
    e.preventDefault();
    const now = new Date();

    const parts = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Europe/Kyiv",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false
    }).formatToParts(now).reduce((acc, p) => {
        if (p.type !== "literal") acc[p.type] = p.value;
        return acc;
    }, {});
    const value = `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`;
    openTime.value = value;
})