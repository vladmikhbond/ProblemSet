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




// ------------- вибір або скасування задач зі списку ----------------------

// let ids = problem_ids.innerHTML.trim().split(/\s+/);
// paint()

// function toggle(problemId) {
//     let i = ids.indexOf(problemId)
//     if(i == -1) {
//         ids.push(problemId)
//     } else {
//         ids.splice(i, 1)
//     }
//     problem_ids.innerHTML = ids.join('\n');
//     paint()
// }

// function paint() {
//   for (let child of problem_headers.children) {
//     if (ids.indexOf(child.id) > -1) {
//       child.style.fontWeight = "700";
//     } else {
//       child.style.fontWeight = "400";
//     }
//   }
// }


