let tg = window.Telegram.WebApp;
tg.expand();

function searchTask() {
    let q = document.getElementById("search-task").value;
    searchUserTasks(q)
}

function searchUserTasks(q) {
    $.ajax({
        url: `/tasks?q=${q}`,
        method: "GET",
        dataType: "json",
        headers: {
            "Authorization": tg.initData,
        },
        success: function (data) {
            let task_list = document.getElementById("task-list")
            task_list.innerHTML = ""
            data.forEach(function (task) {
                console.log(task.title)
                task_list.innerHTML += `<tr><td><a href="#" class="text-reset" tabindex="-1">${task.title}</a></td><td>${task.end_date}</td><td><span class="badge bg-${task.is_done ? 'success' : 'warning'} me-1"></span></td></tr>`;
            })
        }
    })
}

function getUserTasks() {
    $.ajax({
        url: `/tasks`,
        method: "GET",
        dataType: "json",
        headers: {
            "Authorization": tg.initDataUnsafe,
        },
        success: function (data) {
            let task_list = document.getElementById("task-list")
            task_list.innerHTML = ""
            data.forEach(function (task) {
                task_list.innerHTML += `<tr><td><a href="#" class="text-reset" tabindex="-1">${task.title}</a></td><td>${task.end_date}</td><td><span class="badge bg-${task.is_done ? 'success' : 'warning'} me-1"></span></td></tr>`;
            })
        }
    })
}

$(document).ready(getUserTasks)

$("#create-task").on("submit", function (e) {
    e.preventDefault();
    $.ajax(
        {
            url: "/",
            contentType: "application/json",
            dataType: "json",
            method: "POST",
            headers: {
                "Authorization": tg.initDataUnsafe,
            },
            data: JSON.stringify({
                title: this.title.value,
                description: this.description.value,
                end_date: this.end_date.value,
                user_id: tg.initDataUnsafe.user.id
            }),
            success: function (data) {
                form = document.getElementById("create-task");
                form.title.value = "";
                form.description.value = "";
                form.end_date.value = "";
                getUserTasks()
            }
        }
    );
})