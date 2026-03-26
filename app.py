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

    success = request.args.get('success')

    return render_template('index.html', meals=meals, success=success)


@app.route('/add_meal', methods=['POST'])
def add_meal():
    name = request.form['name']

    ingredient_names = request.form.getlist('ingredient_name[]')
    ingredient_qtys = request.form.getlist('ingredient_qty[]')
    ingredient_units = request.form.getlist('ingredient_unit[]')
    ingredient_types = request.form.getlist('ingredient_type[]')
    
    ingredients = {}
    
    for i in range(len(ingredient_names)):
        n = ingredient_names[i].strip()
        q = ingredient_qtys[i]
        u = ingredient_units[i]
        t = ingredient_types[i]
    
        if n and q and u and t:
            try:
                ingredients[n] = {
                    "qty": float(q),
                    "unit": u,
                    "type": t
                }
            except ValueError:
                continue

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

    # return render_template('index.html', meals=meals, success=True)
    return redirect('/?success=1')

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

products = {
    # MEAT ################################
    'Chicken Breast' : [
        {
            'id' : 'chicken_small',
            'search' : 'Waitrose Slower Reared 2 Chicken Breast Fillets',
            'size' : 380,
            'unit' : 'grams',
            'price' : 4.75
        },
        {
            'id' : 'chicken_large',
            'search' : 'Waitrose Slower Reared Chicken Breast Fillets',
            'size' : 600,
            'unit' : 'grams',
            'price' : 5.5
        },
        {
            'id' : 'chicken_extra_large',
            'search' : 'Waitrose Slower Reared Chicken Breast Fillets - XL Pack',
            'size' : 1200,
            'unit' : 'grams',
            'price' : 9.5
        },
    ],
    'Beef Mince' : [
        {
            'id' : 'beef_mince_small',
            'search' : 'Waitrose British Native Breed Beef Mince 12% Fat',
            'size' : 500,
            'unit' : 'grams',
            'price' : 4.50
        },
        {
            'id' : 'beef_mince_large',
            'search' : 'Waitrose British Native Breeds Beef Mince 15%',
            'size' : 750,
            'unit' : 'grams',
            'price' : 7
        }
    ],
    'Diced Beef' : [
        {
            'id' : 'diced_beef',
            'search' : 'Essential British Beef Diced Braising Steak',
            'size' : 400,
            'unit' : 'grams',
            'price' : 4.5
        }
    ],
    'Bacon' : [
        {
            'id' : 'bacon',
            'search' : 'Waitrose 12 Made Without Nitrite Smoked Streaky Bacon Rashers',
            'size' : 250,
            'unit' : 'grams',
            'price' : 4
        }
    ],
    'Sausages' : [
        {
            'id' : 'sausages',
            'search' : 'Waitrose 6 Cumberland Pork Sausages',
            'size' : 400,
            'unit' : 'grams',
            'price' : 4
        }
    ],
    'Chorizo' : [
        {
            'id' : 'chorizo',
            'search' : 'Waitrose Spanish Hot & Spicy Chorizo Ring',
            'size' : 225,
            'unit' : 'grams',
            'price' : 3.75
        }
    ],
    # VEGETABLES ################################
    'Broccoli' : [
        {
            'id' : 'broccoli',
            'search' : 'Essential Broccoli',
            'size' : 400,
            'unit' : 'grams',
            'price' : 0.96
        }
    ],
    'Carrot' : [
        {
            'id' : 'carrot',
            'search' : 'Essential British Loose Carrots',
            'size' : 140,
            'unit' : 'grams',
            'price' : 0.1
        }
    ],
    'Onion' : [
        {
            'id' : 'onion',
            'search' : 'Essential Onions',
            'size' : 150,
            'unit' : 'grams',
            'price' : 0.16
        }
    ],
    'Celery' : [
        {
            'id' : 'celery',
            'search' : 'Essential Green Celery',
            'size' : 375,
            'unit' : 'grams',
            'price' : 0.9
        }
    ],
    'Pepper' : [
        {
            'id' : 'bell_pepper',
            'search' : 'Waitrose Red Peppers',
            'size' : 160,
            'unit' : 'grams',
            'price' : 0.72
        }
    ],
    'Potatoes' : [
        {
            'id' : 'potatoes',
            'search' : 'Waitrose Maris Piper Potatoes',
            'size' : 2000,
            'unit' : 'grams',
            'price' : 2.2
        }
    ],
    'Peas' : [
        {
            'id' : 'peas',
            'search' : 'Essential Frozen British Garden Peas',
            'size' : 725,
            'unit' : 'grams',
            'price' : 1.25
        }
    ],
    # OTHER ################################
    'Pasta' : [
        {
            'id' : 'pasta',
            'search' : 'No.1 Italian Mafaldine Pasta',
            'size' : 500,
            'unit' : 'grams',
            'price' : 3
        }
    ],
    'Birria Paste' : [
        {
            'id' : 'birria_paste',
            'search' : 'Waitrose Birria Paste',
            'size' : 90,
            'unit' : 'grams',
            'price' : 2
        }
    ],
    'Spag Bol Seasoning' : [
        {
            'id' : 'spag_bol_paste',
            'search' : 'Jamie Oliver Brilliant Bolognese Paste',
            'size' : 180,
            'unit' : 'grams',
            'price' : 2.5
        }
    ],
    'Tortilla' : [
        {
            'id' : 'tortilla',
            'search' : 'Gran Luchito 10 Mexican Soft Taco Wraps',
            'size' : 300,
            'unit' : 'grams',
            'price' : 2.2
        }
    ],
    'Chopped Tomatoes' : [
        {
            'id' : 'chopped_tomatoes_small',
            'search' : 'Waitrose Finely Chopped Italian Tomatoes',
            'size' : 400,
            'unit' : 'grams',
            'price' : 0.95
        },
        {
            'id' : 'chopped_tomatoes_large',
            'search' : 'Essential Chopped Tomatoes in Natural Juice',
            'size' : 1600,
            'unit' : 'grams',
            'price' : 2.4
        }
    ],
    'Cheddar' : [
        {
            'id' : 'cheddar_small',
            'search' : 'Cathedral City Mature Cheddar Cheese',
            'size' : 350,
            'unit' : 'grams',
            'price' : 4.25
        },
        {
            'id' : 'cheddar_large',
            'search' : 'Cathedral City Mature Cheddar Cheese Large',
            'size' : 550,
            'unit' : 'grams',
            'price' : 4.6
        }
    ],
    'Parmesan' : [
        {
            'id' : 'parmesan',
            'search' : 'Waitrose Grana Padano DOP Cheese Strength 4',
            'size' : 175,
            'unit' : 'grams',
            'price' : 3.3
        }
    ],
    'Eggs' : [
        {
            'id' : 'eggs_large',
            'search' : 'Waitrose FR Mixed Size Eggs British Blacktail',
            'size' : 700,
            'unit' : 'grams',
            'price' : 3.4
        }
    ],
    'Microwave Rice' : [
        {
            'id' : 'microwave_rice',
            'search' : 'Veetee Steam Filtered Sticky Rice',
            'size' : 260,
            'unit' : 'grams',
            'price' : 1.2
        }
    ],
}
