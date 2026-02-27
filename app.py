from flask import Flask, render_template, request, jsonify, redirect, session
from flask_cors import CORS
import oracledb
import hashlib

app = Flask(__name__)
CORS(app)

app.secret_key = "supersecretkey"
app.config['SESSION_PERMANENT'] = False

# ===== ORACLE CONNECTION =====
connection = oracledb.connect(
    user="system",
    password="sugi123",
    dsn="localhost:1521/XE"
)

cursor = connection.cursor()

# ==============================
#           HOME
# ==============================
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    # Get username to display
    cursor.execute("SELECT name FROM users WHERE id = :1", (session["user_id"],))
    user = cursor.fetchone()

    return render_template("index.html", username=user[0])


# ==============================
#         REGISTER
# ==============================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form

        hashed_password = hashlib.sha256(
            data["password"].encode()
        ).hexdigest()

        query = """
        INSERT INTO users (id, name, email, phone, password)
        VALUES (user_seq.NEXTVAL, :1, :2, :3, :4)
        """

        cursor.execute(query, (
            data["name"],
            data["email"],
            data["phone"],
            hashed_password
        ))
        connection.commit()

        return redirect("/login")

    return render_template("register.html")


# ==============================
#           LOGIN
# ==============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form

        hashed_password = hashlib.sha256(
            data["password"].encode()
        ).hexdigest()

        query = """
        SELECT id FROM users
        WHERE email = :1 AND password = :2
        """

        cursor.execute(query, (data["email"], hashed_password))
        user = cursor.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Invalid Credentials"

    return render_template("login.html")


# ==============================
#          LOGOUT
# ==============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ==============================
#         ADD TASK
# ==============================
@app.route("/addTask", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    query = """
    INSERT INTO tasks (id, task, due_date, user_id)
    VALUES (task_seq.NEXTVAL, :1, TO_DATE(:2, 'YYYY-MM-DD'), :3)
    """

    cursor.execute(query, (
        data["task"],
        data["dueDate"],
        session["user_id"]
    ))
    connection.commit()

    return jsonify({"message": "Task Added"})


# ==============================
#         GET TASKS
# ==============================
@app.route("/getTasks", methods=["GET"])
def get_tasks():
    if "user_id" not in session:
        return jsonify([])

    query = """
    SELECT id, task, due_date, status
    FROM tasks
    WHERE user_id = :1
    ORDER BY id DESC
    """

    cursor.execute(query, (session["user_id"],))
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


# ==============================
#        UPDATE STATUS
# ==============================
@app.route("/updateStatus/<int:id>", methods=["PUT"])
def update_status(id):
    data = request.json

    query = """
    UPDATE tasks
    SET status = :1
    WHERE id = :2 AND user_id = :3
    """

    cursor.execute((query), (
        data["status"],
        id,
        session["user_id"]
    ))
    connection.commit()

    return jsonify({"message": "Status Updated"})


# ==============================
#        DELETE TASK
# ==============================
@app.route("/deleteTask/<int:id>", methods=["DELETE"])
def delete_task(id):
    query = """
    DELETE FROM tasks
    WHERE id = :1 AND user_id = :2
    """

    cursor.execute(query, (id, session["user_id"]))
    connection.commit()

    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    app.run(debug=True)