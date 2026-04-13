import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, redirect, jsonify


def init_firestore():
    if not firebase_admin._apps:
        cred_json = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
        cred = credentials.Certificate(cred_json)
        firebase_admin.initialize_app(cred)

    return firestore.client()


db = init_firestore()

app = Flask(__name__)


@app.route('/')
def index():
    docs = db.collection('meals').stream()
    meals = {doc.id: doc.to_dict()['ingredients'] for doc in docs}

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

    # Firestore write (replaces INSERT + ON CONFLICT DO NOTHING)
    doc_ref = db.collection('meals').document(name)
    if not doc_ref.get().exists:
        doc_ref.set({
            'ingredients': ingredients
        })

    # reload meals (same logic preserved)
    docs = db.collection('meals').stream()
    meals = {doc.id: doc.to_dict()['ingredients'] for doc in docs}

    return redirect('/?success=1')


@app.route('/delete_meal', methods=['POST'])
def delete_meal():
    name = request.form['name']

    try:
        db.collection('meals').document(name).delete()
    except Exception as e:
        print("DELETE ERROR:", e)
        return "Error deleting meal", 500

    return redirect('/')


@app.route('/build_basket', methods=['POST'])
def build_basket_api():
    try:
        shopping_list = request.get_json()

        if not shopping_list:
            return jsonify({'error': 'No data provided'}), 400

        basket = build_basket(shopping_list, products)

        return jsonify({'basket': basket})

    except Exception as e:
        print('API ERROR:', e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

products = {
    # MEAT ################################
    'Chicken Breast': [
        {
            'id': 'chicken_small',
            'search': 'Waitrose Slower Reared 2 Chicken Breast Fillets',
            'size': 380,
            'unit': 'grams',
            'price': 4.75
        },
        {
            'id': 'chicken_large',
            'search': 'Waitrose Slower Reared Chicken Breast Fillets',
            'size': 600,
            'unit': 'grams',
            'price': 5.5
        },
        {
            'id': 'chicken_extra_large',
            'search': 'Waitrose Slower Reared Chicken Breast Fillets - XL Pack',
            'size': 1200,
            'unit': 'grams',
            'price': 9.5
        }
    ],
    'Beef Mince': [
        {
            'id': 'beef_mince_small',
            'search': 'Waitrose British Native Breed Beef Mince 12% Fat',
            'size': 500,
            'unit': 'grams',
            'price': 4.50
        },
        {
            'id': 'beef_mince_large',
            'search': 'Waitrose British Native Breeds Beef Mince 15%',
            'size': 750,
            'unit': 'grams',
            'price': 7
        }
    ],
    'Diced Beef': [
        {
            'id': 'diced_beef',
            'search': 'Essential British Beef Diced Braising Steak',
            'size': 400,
            'unit': 'grams',
            'price': 4.5
        }
    ],
    'Bacon': [
        {
            'id': 'bacon',
            'search': 'Waitrose 12 Made Without Nitrite Smoked Streaky Bacon Rashers',
            'size': 1,
            'unit': 'items',
            'price': 4
        }
    ],
    'Sausages': [
        {
            'id': 'sausages',
            'search': 'Waitrose 6 Cumberland Pork Sausages',
            'size': 400,
            'unit': 'grams',
            'price': 4
        }
    ],
    'Chorizo': [
        {
            'id': 'chorizo',
            'search': 'Waitrose Spanish Hot & Spicy Chorizo Ring',
            'size': 1,
            'unit': 'items',
            'price': 3.75
        }
    ],
    # VEGETABLES ################################
    'Broccoli': [
        {
            'id': 'broccoli',
            'search': 'Essential Broccoli',
            'size': 1,
            'unit': 'items',
            'price': 0.96
        }
    ],
    'Carrot': [
        {
            'id': 'carrot',
            'search': 'Essential British Loose Carrots',
            'size': 1,
            'unit': 'items',
            'price': 0.1
        }
    ],
    'Onion': [
        {
            'id': 'onion',
            'search': 'Essential Onions',
            'size': 1,
            'unit': 'items',
            'price': 0.16
        }
    ],
    'Celery': [
        {
            'id': 'celery',
            'search': 'Essential Green Celery',
            'size': 1,
            'unit': 'items',
            'price': 0.9
        }
    ],
    'Pepper': [
        {
            'id': 'bell_pepper',
            'search': 'Waitrose Red Peppers',
            'size': 1,
            'unit': 'items',
            'price': 0.72
        }
    ],
    'Potatoes': [
        {
            'id': 'potatoes',
            'search': 'Waitrose Maris Piper Potatoes',
            'size': 1,
            'unit': 'items',
            'price': 2.2
        }
    ],
    'Peas': [
        {
            'id': 'peas',
            'search': 'Essential Frozen British Garden Peas',
            'size': 1,
            'unit': 'items',
            'price': 1.25
        }
    ],
    # OTHER ################################
    'Pasta': [
        {
            'id': 'pasta',
            'search': 'No.1 Italian Mafaldine Pasta',
            'size': 1,
            'unit': 'items',
            'price': 3
        }
    ],
    'Birria Paste': [
        {
            'id': 'birria_paste',
            'search': 'Waitrose Birria Paste',
            'size': 1,
            'unit': 'items',
            'price': 2
        }
    ],
    'Spag Bol Seasoning': [
        {
            'id': 'spag_bol_paste',
            'search': 'Jamie Oliver Brilliant Bolognese Paste',
            'size': 1,
            'unit': 'items',
            'price': 2.5
        }
    ],
    'Tortilla': [
        {
            'id': 'tortilla',
            'search': 'Gran Luchito 10 Mexican Soft Taco Wraps',
            'size': 1,
            'unit': 'items',
            'price': 2.2
        }
    ],
    'Chopped Tomatoes': [
        {
            'id': 'chopped_tomatoes_small',
            'search': 'Waitrose Finely Chopped Italian Tomatoes',
            'size': 400,
            'unit': 'grams',
            'price': 0.95
        },
        {
            'id': 'chopped_tomatoes_large',
            'search': 'Essential Chopped Tomatoes in Natural Juice',
            'size': 1600,
            'unit': 'grams',
            'price': 2.4
        }
    ],
    'Cheddar': [
        {
            'id': 'cheddar_small',
            'search': 'Cathedral City Mature Cheddar Cheese',
            'size': 350,
            'unit': 'grams',
            'price': 4.25
        },
        {
            'id': 'cheddar_large',
            'search': 'Cathedral City Mature Cheddar Cheese Large',
            'size': 550,
            'unit': 'grams',
            'price': 4.6
        }
    ],
    'Parmesan': [
        {
            'id': 'parmesan',
            'search': 'Waitrose Grana Padano DOP Cheese Strength 4',
            'size': 175,
            'unit': 'grams',
            'price': 3.3
        }
    ],
    'Eggs': [
        {
            'id': 'eggs_large',
            'search': 'Waitrose FR Mixed Size Eggs British Blacktail',
            'size': 1,
            'unit': 'items',
            'price': 3.4
        }
    ],
    'Microwave Rice': [
        {
            'id': 'microwave_rice',
            'search': 'Veetee Steam Filtered Sticky Rice',
            'size': 1,
            'unit': 'items',
            'price': 1.2
        }
    ]
}

def optimise_grams(required_grams, options):
    """
    options: list of dicts with keys:
        id, search, size (grams), unit, price
    """

    max_pack = max(o['size'] for o in options)
    max_grams = required_grams + max_pack

    # dp[g] = (cost, combo_dict)
    dp = [None] * (max_grams + 1)
    dp[0] = (0, {})

    for g in range(1, max_grams + 1):
        best = None

        for opt in options:
            size = opt['size']

            if g - size >= 0 and dp[g - size] is not None:
                prev_cost, prev_combo = dp[g - size]

                new_cost = prev_cost + opt['price']
                new_combo = prev_combo.copy()
                new_combo[opt['id']] = new_combo.get(opt['id'], 0) + 1

                if best is None or new_cost < best[0]:
                    best = (new_cost, new_combo)

        dp[g] = best

    # find cheapest solution where grams >= required
    best_solution = None

    for g in range(required_grams, max_grams + 1):
        if dp[g] is not None:
            if best_solution is None or dp[g][0] < best_solution[0]:
                best_solution = dp[g]

    return best_solution

def build_basket(shopping_list, products):
    """
    shopping_list: [
        { 'key': str, 'qty': int, 'unit': 'grams' | 'items' }
    ]

    products: your full product dict
    """

    basket = []

    for item in shopping_list:
        key = item['name']
        qty = item['qty']
        unit = item['unit']

        if key not in products:
            continue

        options = products[key]

        # --- ITEMS ---
        if unit == 'items':
            opt = options[0]  # assume single option

            basket.append({
                'id': opt['id'],
                'search': opt['search'],
                'quantity': qty,
                'total_price': round(qty * opt['price'], 2)
            })

        # --- GRAMS ---
        elif unit == 'grams':
            result = optimise_grams(qty, options)

            if result is None:
                continue

            total_cost, combo = result

            for opt_id, count in combo.items():
                opt = next(o for o in options if o['id'] == opt_id)

                basket.append({
                    'id': opt['id'],
                    'search': opt['search'],
                    'quantity': count,
                    'total_price': round(count * opt['price'], 2)
                })

    return basket
