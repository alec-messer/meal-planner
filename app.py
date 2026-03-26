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

    # ===== MEAT (optimise) =====
    'chicken_breast': {
        'mode': 'optimise',
        'options': [
            {
                'id': 'chicken_small',
                'search': 'Waitrose Slower Reared 2 Chicken Breast Fillets',
                'size': 380,
                'price': 4.75
            },
            {
                'id': 'chicken_large',
                'search': 'Waitrose Slower Reared Chicken Breast Fillets',
                'size': 600,
                'price': 5.5
            },
            {
                'id': 'chicken_xl',
                'search': 'Waitrose Slower Reared Chicken Breast Fillets XL Pack',
                'size': 1200,
                'price': 9.5
            }
        ]
    },

    'beef_mince': {
        'mode': 'optimise',
        'options': [
            {
                'id': 'mince_500g',
                'search': 'Waitrose British Beef Mince 12% Fat 500g',
                'size': 500,
                'price': 4.50
            },
            {
                'id': 'mince_750g',
                'search': 'Waitrose British Beef Mince 15% Fat 750g',
                'size': 750,
                'price': 7.00
            }
        ]
    },

    'diced_beef': {
        'mode': 'optimise',
        'options': [
            {
                'id': 'diced_beef',
                'search': 'Essential British Beef Diced Braising Steak',
                'size': 400,
                'price': 4.5
            }
        ]
    },

    # ===== VEGETABLES (direct) =====
    'broccoli': {
        'mode': 'direct',
        'options': [
            {
                'id': 'broccoli',
                'search': 'Essential Broccoli'
            }
        ]
    },

    'carrot': {
        'mode': 'direct',
        'options': [
            {
                'id': 'carrot',
                'search': 'Essential British Loose Carrots'
            }
        ]
    },

    'onion': {
        'mode': 'direct',
        'options': [
            {
                'id': 'onion',
                'search': 'Essential Onions'
            }
        ]
    },

    'celery': {
        'mode': 'direct',
        'options': [
            {
                'id': 'celery',
                'search': 'Essential Green Celery'
            }
        ]
    },

    # ===== OTHER =====
    'pasta': {
        'mode': 'optimise',
        'options': [
            {
                'id': 'pasta',
                'search': 'No.1 Italian Mafaldine Pasta 500g',
                'size': 500,
                'price': 3
            }
        ]
    },

    'tortilla': {
        'mode': 'direct',
        'options': [
            {
                'id': 'tortilla',
                'search': 'Gran Luchito 10 Soft Taco Wraps'
            }
        ]
    },

    'chopped_tomatoes': {
        'mode': 'optimise',
        'options': [
            {
                'id': 'tomatoes_400g',
                'search': 'Waitrose Finely Chopped Tomatoes 400g',
                'size': 400,
                'price': 0.95
            },
            {
                'id': 'tomatoes_1600g',
                'search': 'Essential Chopped Tomatoes 1600g',
                'size': 1600,
                'price': 2.4
            }
        ]
    },

    'cheddar': {
        'mode': 'optimise',
        'options': [
            {
                'id': 'cheddar_350g',
                'search': 'Cathedral City Mature Cheddar 350g',
                'size': 350,
                'price': 4.25
            },
            {
                'id': 'cheddar_550g',
                'search': 'Cathedral City Mature Cheddar 550g',
                'size': 550,
                'price': 4.6
            }
        ]
    }
}

import math
import itertools

def optimise_ingredient(required, options):
    min_size = min(opt['size'] for opt in options)
    max_units = math.ceil(required / min_size) + 2

    best = None

    for counts in itertools.product(range(max_units), repeat=len(options)):
        total_size = sum(c * opt['size'] for c, opt in zip(counts, options))
        total_price = sum(c * opt['price'] for c, opt in zip(counts, options))

        if total_size >= required and total_size > 0:
            if (
                best is None or
                total_price < best['price'] or
                (total_price == best['price'] and total_size < best['size'])
            ):
                best = {
                    'counts': counts,
                    'price': total_price,
                    'size': total_size
                }

    result = []

    for count, opt in zip(best['counts'], options):
        if count > 0:
            result.append({
                'id': opt['id'],
                'search': opt['search'],
                'quantity': count
            })

    return result

def resolve_ingredient(name, qty, unit, config):
    mode = config['mode']
    options = config['options']

    # ===== DIRECT MODE =====
    if mode == 'direct':
        opt = options[0]

        return [{
            'id': opt['id'],
            'search': opt['search'],
            'quantity': qty
        }]

    # ===== OPTIMISE MODE =====
    elif mode == 'optimise':
        if unit != 'grams':
            raise ValueError(f"{name} requires grams but got {unit}")

        return optimise_ingredient(qty, options)

def build_basket(shopping_list, products):
    basket = []
    unresolved = []

    for item in shopping_list:
        key = item['key']          # canonical key
        qty = item['qty']
        unit = item['unit']

        if key not in products:
            unresolved.append(item)
            continue

        try:
            result = resolve_ingredient(key, qty, unit, products[key])
            basket.extend(result)
        except Exception:
            unresolved.append(item)

    return {
        'basket': basket,
        'unresolved': unresolved
    }
