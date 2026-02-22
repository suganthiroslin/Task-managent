window.onload = fetchTasks;

function addTask() {
    const task = document.getElementById("taskInput").value;
    const dueDate = document.getElementById("dueDate").value;

    fetch("/addTask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: task, dueDate: dueDate })
    })
    .then(res => res.json())
    .then(() => {
        fetchTasks();
        document.getElementById("taskInput").value = "";
    });
}

function fetchTasks() {
    fetch("/getTasks")
    .then(res => res.json())
    .then(data => {
        const taskList = document.getElementById("taskList");
        taskList.innerHTML = "";

        data.forEach(task => {
            const div = document.createElement("div");
            div.className = "task-card";

            div.innerHTML = `
                <h3>${task.task}</h3>
                <p>Due: ${task.due_date}</p>
                <p>Status: ${task.status}</p>

                <div class="task-buttons">
                    <button class="complete" onclick="updateStatus(${task.id}, 'Completed')">Completed</button>
                    <button class="yet" onclick="updateStatus(${task.id}, 'Yet to Complete')">Yet</button>
                    <button class="notdone" onclick="updateStatus(${task.id}, 'Not Done')">Not Done</button>
                    <button class="delete" onclick="deleteTask(${task.id})">Delete</button>
                </div>
            `;

            taskList.appendChild(div);
        });
    });
}

function updateStatus(id, status) {
    fetch(`/updateStatus/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: status })
    })
    .then(res => res.json())
    .then(() => fetchTasks());
}

function deleteTask(id) {
    fetch(`/deleteTask/${id}`, {
        method: "DELETE"
    })
    .then(res => res.json())
    .then(() => fetchTasks());
}