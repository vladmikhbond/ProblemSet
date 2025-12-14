// ---------------------------- фільтр задач -----------------------------
// В шаблоні:
// <input name="problem_filter" style="width: 120px" id="problem_filter" title="Фільтр задач"> 
// В роутері
// PROBLEM_FILTER_KEY = "problemset_problem_filter";
// filter = unquote(request.cookies.get(PROBLEM_FILTER_KEY, "")).strip()

const key = "problemset_problem_filter";
const inp = document.getElementById("problem_filter");

inp.value = getCookie(key);

inp.addEventListener("change", async (e) => {
    console.log("change")
    setCookie(key, encodeURIComponent(inp.value.trim()) )
})

// Встановлення або видалення кукі
function setCookie(key, value) {
    if (value) {
        const maxAge = 60 * 60 * 24 * 365; // seconds
        document.cookie = `${key}=${value}; max-age=${maxAge}; path=/; SameSite=Lax;`;
    } else {
        document.cookie = `${key}=; max-age=0; path=/`;
    }
}

// Отримання кукі
function getCookie(key) {
    const pairs = document.cookie.split('; ').map(v => v.split('='));
    const pair = pairs.find(([k]) => k === key);
    return pair ? decodeURIComponent(pair[1]) : "";
}   
