function toggleDeletePanel() {
    document.getElementById('deletePanel').classList.toggle('open');
}

function togglePanel() {
    document.getElementById('sidePanel').classList.toggle('open');
}

function addIngredient() {
    const container = document.getElementById('ingredients-container');

    const row = document.createElement('div');
    row.className = 'ingredient-row';

    row.innerHTML = `
        <input name="ingredient_name[]" placeholder="Ingredient" required>
        <input name="ingredient_qty[]" type="number" step="any" placeholder="Qty" required>

        <select name="ingredient_unit[]" required>
            <option value="">Unit</option>
            <option value="grams">grams</option>
            <option value="items">items</option>
        </select>

        <select name="ingredient_type[]" required>
            <option value="">Type</option>
            <option value="meat">meat</option>
            <option value="veg">veg</option>
            <option value="dairy">dairy</option>
            <option value="fruit">fruit</option>
            <option value="other">other</option>
        </select>
    `;

    container.appendChild(row);
}

function buildShoppingJSON(totals) {
    const items = [];

    Object.keys(totals).forEach(type => {
        Object.keys(totals[type]).forEach(name => {
            const { qty, unit } = totals[type][name];

            items.push({ name, qty, unit });
        });
    });

    return items;
}

function generateList() {
    const selects = document.querySelectorAll('.meal-select');

    const totals = {
        meat: {},
        veg: {},
        fruit: {},
        dairy: {},
        other: {}
    };

    selects.forEach(select => {
        const meal = select.value;

        if (meal && MEALS[meal]) {
            const ingredients = MEALS[meal];

            Object.keys(ingredients).forEach(item => {
                const data = ingredients[item];
                const type = data.type || 'other';

                if (!totals[type][item]) {
                    totals[type][item] = { qty: 0, unit: data.unit };
                }

                totals[type][item].qty += data.qty;
            });
        }
    });

    const shoppingJSON = buildShoppingJSON(totals);

    fetch('/build_basket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(shoppingJSON)
    })
    .then(res => res.json())
    .then(data => {

        let output = '';

        const now = new Date();
        const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

        output += `Shopping List\n${days[now.getDay()]} ${now.getDate()}/${now.getMonth()+1}\n\n`;

        const typeOrder = ['meat','veg','fruit','dairy','other'];

        typeOrder.forEach(type => {
            const items = totals[type];
            if (!Object.keys(items).length) return;

            output += `${type.toUpperCase()}\n`;

            Object.keys(items).forEach(name => {
                const { qty, unit } = items[name];
                output += `${qty} (${unit}) ${name}\n`;
            });

            output += `\n`;
        });

        output += `OPTIMISED BASKET\n\n`;

        data.basket.forEach(item => {
            output += `${item.quantity} x ${item.search} (£${item.total_price})\n`;
        });

        output += `\nOPEN ITEMS:\n`;

        data.basket.forEach(item => {
            output += `${item.url}\n`;
        });

        document.getElementById('output').innerText = output;
        document.getElementById('output-card').classList.remove('hidden');

        // optional auto-run mode
        window.currentBasket = data.basket;
    })
    .catch(err => console.error(err));
}

function shareList() {
    const text = document.getElementById('output').innerText;

    if (navigator.share) {
        navigator.share({ title: 'Shopping List', text });
    }
}
