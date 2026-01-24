// повернення до студентського додатку
document.getElementById("to_student").href = location.origin
    .replace("7001","7004/disc/list")
    .replace("7071","7074/disc/list")
    

// ---------------------------- фільтр задач -----------------------------

const PROBLEM_FILTER_KEY = "problemset_problem_filter"
const problem_filter = document.getElementById("problem_filter");
problem_filter.value = getCookie(PROBLEM_FILTER_KEY);

problem_filter.addEventListener("change", async (e) => {
    setCookie(PROBLEM_FILTER_KEY, encodeURIComponent(problem_filter.value.trim()) )
    location.reload();
})

// ---------------------------- фільтр юзерів -----------------------------

const USER_FILTER_KEY = "problemset_user_filter";
const user_filter = document.getElementById("user_filter");
user_filter.value = getCookie(USER_FILTER_KEY);

user_filter.addEventListener("change", async (e) => {
    setCookie(USER_FILTER_KEY, encodeURIComponent(user_filter.value.trim()) )
    location.reload();
})

// ------------------------------------------------------

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