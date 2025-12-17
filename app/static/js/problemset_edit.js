let ids = problem_ids.innerHTML.trim().split(/\s+/);
paint()

function toggle(problemId) {
    let i = ids.indexOf(problemId)
    if(i == -1) {
        ids.push(problemId)
    } else {
        ids.splice(i, 1)
    }
    problem_ids.innerHTML = ids.join('\n');
    paint()
}

function paint() {
  for (let child of problem_headers.children) {
    if (ids.indexOf(child.id) > -1) {
      child.style.fontWeight = "700";
    } else {
      child.style.fontWeight = "400";
    }
  }
}


