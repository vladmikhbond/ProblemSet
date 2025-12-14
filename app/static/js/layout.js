// ---------------------------- фільтр задач -----------------------------

const key = "problemset_problem_filter";
const inp = document.getElementById("problem_filter");
const btn = document.getElementById("problem_filter_btn");

inp.value = getCookie(key);

btn.addEventListener("click", async (e) => {
    e.preventDefault();
    setCookie(key, encodeURIComponent(inp.value.trim()) )
})

// Встановлення-видалення кукі
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
