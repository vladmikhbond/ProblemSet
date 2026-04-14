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

// Стерти час в полі openTime
//
buttonNow.addEventListener("click", (e) => {
    e.preventDefault();
    openTime.value = "";
})