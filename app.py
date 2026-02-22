from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import oracledb

app = Flask(__name__)
CORS(app)

# ===== ORACLE CONNECTION (THIN MODE) =====
connection = oracledb.connect(
    user="system",              # your username
    password="sugi123",    # your password
    dsn="localhost:1521/XE"     # host:port/service
)

cursor = connection.cursor()

# ===== HOME =====
@app.route("/")
def home():
    return render_template("index.html")

# ===== ADD TASK =====
@app.route("/addTask", methods=["POST"])
def add_task():
    data = request.json

    query = """
    INSERT INTO tasks (id, task, due_date)
    VALUES (task_seq.NEXTVAL, :1, TO_DATE(:2, 'YYYY-MM-DD'))
    """

    cursor.execute(query, (data["task"], data["dueDate"]))
    connection.commit()

    return jsonify({"message": "Task Added"})

# ===== GET TASKS =====
@app.route("/getTasks", methods=["GET"])
def get_tasks():
    cursor.execute("SELECT id, task, due_date, status FROM tasks ORDER BY id DESC")
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "task": row[1],
            "due_date": row[2].strftime("%Y-%m-%d"),
            "status": row[3]
        })

    return jsonify(result)

# ===== UPDATE STATUS =====
@app.route("/updateStatus/<int:id>", methods=["PUT"])
def update_status(id):
    data = request.json
    query = "UPDATE tasks SET status = :1 WHERE id = :2"
    cursor.execute(query, (data["status"], id))
    connection.commit()

    return jsonify({"message": "Status Updated"})

# ===== DELETE TASK =====
@app.route("/deleteTask/<int:id>", methods=["DELETE"])
def delete_task(id):
    query = "DELETE FROM tasks WHERE id = :1"
    cursor.execute(query, (id,))
    connection.commit()

    return jsonify({"message": "Deleted"})

if __name__ == "__main__":
    app.run(debug=True)