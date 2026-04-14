import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, redirect, jsonify
from playwright.sync_api import sync_playwright
import time


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
    deleted = request.args.get('deleted')

    return render_template('index.html', meals=meals, success=success, deleted=deleted)


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

    return redirect('/?deleted=1')


@app.route('/build_basket', methods=['POST'])
def build_basket_api():
    try:
        shopping_list = request.get_json()

        if not shopping_list:
            return jsonify({'error': 'No data provided'}), 400

        basket = build_basket(shopping_list, products)

        # Run Playwright to build basket on Waitrose
        basket_url = run_playwright(basket)

        return jsonify({
            'basket': basket,
            'basket_url': basket_url
        })

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
            'price': 4.75,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-slower-reared-2-chicken-breast-fillets/690849-260860-260861'
        },
        {
            'id': 'chicken_large',
            'search': 'Waitrose Slower Reared Chicken Breast Fillets',
            'size': 600,
            'unit': 'grams',
            'price': 5.5,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-slower-reared-chicken-breast-fillets/486988-707752-707753'
        },
        {
            'id': 'chicken_extra_large',
            'search': 'Waitrose Slower Reared Chicken Breast Fillets - XL Pack',
            'size': 1200,
            'unit': 'grams',
            'price': 9.5,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-slower-reared-chicken-breast-fillets-xl-pack/698580-750402-750403'
        }
    ],
    'Beef Mince': [
        {
            'id': 'beef_mince_small',
            'search': 'Waitrose British Native Breed Beef Mince 12% Fat',
            'size': 500,
            'unit': 'grams',
            'price': 5,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-british-native-breed-beef-mince-12-fat/400260-806217-806218'
        },
        {
            'id': 'beef_mince_large',
            'search': 'Waitrose British Native Breeds Beef Mince 15%',
            'size': 750,
            'unit': 'grams',
            'price': 7,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-british-native-breeds-beef-mince-15/977544-827968-827969'
        }
    ],
    'Diced Beef': [
        {
            'id': 'diced_beef',
            'search': 'Essential British Beef Diced Braising Steak',
            'size': 400,
            'unit': 'grams',
            'price': 4.5,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-british-native-breed-diced-beef-braising-steak/482510-806227-806228'
        }
    ],
    'Bacon': [
        {
            'id': 'bacon',
            'search': 'Waitrose 12 Made Without Nitrite Smoked Streaky Bacon Rashers',
            'size': 1,
            'unit': 'items',
            'price': 4,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-12-made-without-nitrite-smoked-streaky-bacon-rashers/848434-780197-780198'
        }
    ],
    'Sausages': [
        {
            'id': 'sausages',
            'search': 'Waitrose 6 Cumberland Pork Sausages',
            'size': 400,
            'unit': 'grams',
            'price': 4,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-6-cumberland-pork-sausages/657045-731320-731321'
        }
    ],
    'Chorizo': [
        {
            'id': 'chorizo',
            'search': 'Waitrose Spanish Hot & Spicy Chorizo Ring',
            'size': 1,
            'unit': 'items',
            'price': 3.75,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-spanish-hot-spicy-chorizo-ring/948990-846362-846363'
        }
    ],
    # VEGETABLES ################################
    'Broccoli': [
        {
            'id': 'broccoli',
            'search': 'Essential Broccoli',
            'size': 1,
            'unit': 'items',
            'price': 0.96,
            'url' : 'https://www.waitrose.com/ecom/products/essential-broccoli/085242-43323-43324'
        }
    ],
    'Carrot': [
        {
            'id': 'carrot',
            'search': 'Essential British Loose Carrots',
            'size': 1,
            'unit': 'items',
            'price': 0.1,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-british-loose-carrots/085125-43221-43222'
        }
    ],
    'Onion': [
        {
            'id': 'onion',
            'search': 'Essential Onions',
            'size': 1,
            'unit': 'items',
            'price': 0.16,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-onions/085115-43203-43204'
        }
    ],
    'Celery': [
        {
            'id': 'celery',
            'search': 'Essential Green Celery',
            'size': 1,
            'unit': 'items',
            'price': 0.9,
            'url' : 'https://www.waitrose.com/ecom/products/essential-green-celery/086445-44146-44147'
        }
    ],
    'Pepper': [
        {
            'id': 'bell_pepper',
            'search': 'Waitrose Red Peppers',
            'size': 1,
            'unit': 'items',
            'price': 0.72,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-red-peppers/086412-44120-44121'
        }
    ],
    'Potatoes': [
        {
            'id': 'potatoes',
            'search': 'Waitrose Maris Piper Potatoes',
            'size': 1,
            'unit': 'items',
            'price': 2.2,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-maris-piper-potatoes/085063-372142-43169'
        }
    ],
    'Peas': [
        {
            'id': 'peas',
            'search': 'Essential Frozen British Garden Peas',
            'size': 1,
            'unit': 'items',
            'price': 1.25,
            'url' : 'https://www.waitrose.com/ecom/products/essential-frozen-british-garden-peas/054003-27079-27080'
        }
    ],
    # OTHER ################################
    'Pasta': [
        {
            'id': 'pasta',
            'search': 'No.1 Italian Mafaldine Pasta',
            'size': 1,
            'unit': 'items',
            'price': 3,
            'url' : 'https://www.waitrose.com/ecom/products/no1-italian-mafaldine-pasta/567635-828951-828952'
        }
    ],
    'Birria Paste': [
        {
            'id': 'birria_paste',
            'search': 'Waitrose Birria Paste',
            'size': 1,
            'unit': 'items',
            'price': 2,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-birria-paste/923695-1-2'
        }
    ],
    'Tortilla': [
        {
            'id': 'tortilla',
            'search': 'Gran Luchito 10 Mexican Soft Taco Wraps',
            'size': 1,
            'unit': 'items',
            'price': 2.2,
            'url' : 'https://www.waitrose.com/ecom/products/gran-luchito-10-mexican-soft-taco-wraps/776278-703285-703286'
        }
    ],
    'Chopped Tomatoes': [
        {
            'id': 'chopped_tomatoes_small',
            'search': 'Essential Chopped Tomatoes in Natural Juice',
            'size': 400,
            'unit': 'grams',
            'price': 0.65,
            'url' : 'https://www.waitrose.com/ecom/products/essential-chopped-tomatoes-in-natural-juice/019706-9575-9576'
        },
        {
            'id': 'chopped_tomatoes_large',
            'search': 'Essential Chopped Tomatoes in Natural Juice',
            'size': 1600,
            'unit': 'grams',
            'price': 2.4,
            'url' : 'https://www.waitrose.com/ecom/products/essential-chopped-tomatoes-in-natural-juice/073892-37497-37497'
        }
    ],
    'Cheddar': [
        {
            'id': 'cheddar_small',
            'search': 'Cathedral City Mature Cheddar Cheese',
            'size': 350,
            'unit': 'grams',
            'price': 4.25,
            'url' : 'https://www.waitrose.com/ecom/products/cathedral-city-mature-cheddar-cheese/040136-19857-19858'
        },
        {
            'id': 'cheddar_large',
            'search': 'Cathedral City Mature Cheddar Cheese Large',
            'size': 550,
            'unit': 'grams',
            'price': 4.6,
            'url' : 'https://www.waitrose.com/ecom/products/cathedral-city-mature-cheddar-cheese-large/002463-816-817'
        }
    ],
    'Parmesan': [
        {
            'id': 'parmesan',
            'search': 'Waitrose Grana Padano DOP Cheese Strength 4',
            'size': 175,
            'unit': 'grams',
            'price': 3.3,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-grana-padano-dop-cheese-strength-4/605600-688808-688809'
        }
    ],
    'Eggs': [
        {
            'id': 'eggs_large',
            'search': 'Waitrose FR Mixed Size Eggs British Blacktail',
            'size': 1,
            'unit': 'items',
            'price': 3.4,
            'url' : 'https://www.waitrose.com/ecom/products/waitrose-fr-mixed-size-eggs-british-blacktail/082926-42143-42144'
        }
    ],
    'Microwave Rice': [
        {
            'id': 'microwave_rice',
            'search': 'Veetee Steam Filtered Sticky Rice',
            'size': 1,
            'unit': 'items',
            'price': 1.2,
            'url' : 'https://www.waitrose.com/ecom/products/veetee-steam-filtered-sticky-rice/501941-757307-757308'
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

def run_playwright(basket):
    STORAGE_FILE = 'waitrose_session.json'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        if os.path.exists(STORAGE_FILE):
            context = browser.new_context(storage_state=STORAGE_FILE)
        else:
            context = browser.new_context()

        page = context.new_page()
        page.goto('https://www.waitrose.com/')

        # قبول cookies if present
        try:
            page.locator("button:has-text('Accept')").click(timeout=3000)
        except:
            pass

        # First run → manual login
        if not os.path.exists(STORAGE_FILE):
            print("Please log in manually...")
            page.wait_for_timeout(60000)
            context.storage_state(path=STORAGE_FILE)
            print("Session saved.")

        for item in basket:
            url = item['url']
            quantity = item['quantity']

            print(f"Adding: {url} x{quantity}")

            page.goto(url)
            page.wait_for_load_state('domcontentloaded')
            time.sleep(2)

            try:
                # --- SET QUANTITY VIA INPUT BOX ---
                qty_input = page.locator("input[type='number']").first
                qty_input.fill(str(quantity))

                # --- CLICK ADD TO TROLLEY ---
                page.locator("button:has-text('Add to Trolley')").click(timeout=5000)

            except Exception as e:
                print(f"Failed for {url}: {e}")
                continue

            time.sleep(1.5)

        basket_url = "https://www.waitrose.com/ecom/shop/basket"
        page.goto(basket_url)

        context.storage_state(path=STORAGE_FILE)
        browser.close()

        return basket_url
