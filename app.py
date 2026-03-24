import os
import json
import psycopg2
from flask import Flask, render_template, request, redirect

def get_db():
    try:
        print("Connecting to DB...")
        return psycopg2.connect(
            os.environ['DATABASE_URL'],
            sslmode='require'
        )
    except Exception as e:
        print("DB ERROR:", e)
        raise


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            ingredients JSONB NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

app = Flask(__name__)

init_db()

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name, ingredients FROM meals")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    meals = {name: ingredients for name, ingredients in rows}
    return render_template('index.html', meals=meals)


@app.route('/add_meal', methods=['POST'])
def add_meal():
    name = request.form['name']

    ingredient_names = request.form.getlist('ingredient_name[]')
    ingredient_qtys = request.form.getlist('ingredient_qty[]')

    ingredients = {}

    for i in range(len(ingredient_names)):
        n = ingredient_names[i].strip()
        q = ingredient_qtys[i]

        if n and q:
            ingredients[n] = float(q)

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO meals (name, ingredients)
        VALUES (%s, %s)
        ON CONFLICT (name) DO NOTHING
        """,
        (name, json.dumps(ingredients))
    )

    conn.commit()
    cur.close()
    conn.close()

    # ✅ RELOAD meals here (this fixes your error)
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name, ingredients FROM meals")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    meals = {name: ingredients for name, ingredients in rows}

    return render_template('index.html', meals=meals, success=True)

@app.route('/delete_meal', methods=['POST'])
def delete_meal():
    name = request.form['name']

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "DELETE FROM meals WHERE name = %s",
            (name,)
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        print("DELETE ERROR:", e)
        return "Error deleting meal", 500

    finally:
        cur.close()
        conn.close()

    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
