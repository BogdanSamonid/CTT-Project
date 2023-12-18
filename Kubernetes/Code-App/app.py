from flask import (
    Flask,
    render_template,
    session, redirect,
    request,
    url_for,
)
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "2ba02fd05a3575debeb1bf055aa4f8f6747058055c15600e3ab0f2a6b6adfce4"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'test'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'projectdb'
app.config['MYSQL_UNIX_SOCKET'] = None

mysql = MySQL(app)

PLACEHOLDER_CODE = "print('Hello, World!')"

def create_table_if_not_exists():
    try:
        connection = mysql.connection
        cursor = connection.cursor()

        table_check_query = "SHOW TABLES LIKE 'entries'"
        cursor.execute(table_check_query)
        table_exists = cursor.fetchone()

        if not table_exists:
            create_table_query = """
                CREATE TABLE entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    code VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Table created successfully.")

        cursor.close()

    except Exception as e:
        print(f"Error: {e}")

@app.route("/save_code", methods=["POST"])
def save_code():
    create_table_if_not_exists()

    if request.method == 'POST':
        code = str(request.form.get("code"))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO entries (code) VALUES (%s)", (code,))
        mysql.connection.commit()
        cur.close()
        print('Data inserted successfully')

    session["code"] = code
    return redirect(url_for("code"))

@app.route("/reset_session", methods=["POST"])
def reset_session():
    session.clear()
    session["code"] = PLACEHOLDER_CODE
    return redirect(url_for("code"))

@app.route("/", methods=["GET"])
def code():
    if session.get("code") is None:
        session["code"] = PLACEHOLDER_CODE
    lines = session["code"].split("\n")
    context = {
        "message": "Paste Your Python Code 🐍",
        "code": session["code"],
        "num_lines": len(lines),
        "max_chars": len(max(lines, key=len))
    }
    return render_template("code_input.html", **context)