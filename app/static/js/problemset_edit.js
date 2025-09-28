lang_js.addEventListener('click', f)
lang_py.addEventListener('click', f)
lang_cs.addEventListener('click', f)

async function f(e) {
  await fetch_problems(this.value);
}

let ids = problem_ids.innerHTML.trim().split(/\s+/);

async function fetch_problems(lang) 
{
  const response = await fetch(`/problems/lang/${lang}`);
  if (!response.ok) {
      error_message.innerHTML = response.statusText;
      return 
  }
  const headers_json = await response.json();
  problem_headers.innerHTML = "";
  for (const  h of headers_json) {
    const el = document.createElement("div");
    el.addEventListener('click', toggle);
    el.id = h.id;
    el.innerHTML = `${h.title} - ${h.attr}`;
    problem_headers.append(el);
  }
  paint();
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

function toggle(e) {
    let i = ids.indexOf(this.id)
    if(i == -1) {
        ids.push(this.id)
    } else {
        ids.splice(i, 1)
    }
    problem_ids.innerHTML = ids.join('\n');
    paint()
    
    
}


