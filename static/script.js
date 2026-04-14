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
        dairy: {},
        fruit: {},
        veg: {},
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
                    totals[type][item] = {
                        qty: 0,
                        unit: data.unit
                    };
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
        console.log('Optimised basket:', data.basket);

        let output = '';

        // DATE
        const now = new Date();
        const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
        const dayName = days[now.getDay()];
        const date = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');

        output += `Shopping List\n${dayName} ${date}/${month}\n\n`;

        const typeOrder = ['meat', 'veg', 'fruit', 'dairy', 'other'];

        typeOrder.forEach(type => {
            const items = totals[type];
            if (Object.keys(items).length === 0) return;

            output += `${type.toUpperCase()}\n`;

            const rows = Object.keys(items).sort().map(item => {
                const { qty, unit } = items[item];
                return { name: item, left: `${qty} (${unit})` };
            });

            const maxLeftLength = Math.max(...rows.map(r => r.left.length));

            rows.forEach(row => {
                output += `${row.left.padEnd(maxLeftLength)}  ${row.name}\n`;
            });

            output += `\n`;
        });

        // OPTIMISED BASKET
        output += `OPTIMISED BASKET\n\n`;

        data.basket.forEach(item => {
            output += `${item.quantity} x ${item.search}\n`;
        });

        // LOGIN BUTTON
        output += `\nLOGIN TO WAITROSE:\n`;
        output += `${data.login_url}\n\n`;

        // BUILD BUTTON
        output += `CLICK BELOW TO BUILD BASKET\n`;

        document.getElementById('output').innerText = output;
        document.getElementById('output-card').classList.remove('hidden');

        // 👉 ADD BUTTON DYNAMICALLY
        const btn = document.createElement('button');
        btn.innerText = 'Build Waitrose Basket';
        btn.onclick = () => buildWaitroseBasket(data.basket);

        document.getElementById('output-card').appendChild(btn);
    })
    .catch(err => {
        console.error('API error:', err);
    });
}

function shareList() {
    const text = document.getElementById('output').innerText;

    if (navigator.share) {
        navigator.share({ title: 'Shopping List', text });
    }
}

function buildWaitroseBasket(basket) {
    alert('1. Log in to Waitrose in the opened tabs.\n2. Then run this again if needed.');

    basket.forEach(item => {
        for (let i = 0; i < item.quantity; i++) {
            window.open(item.url, '_blank');
        }
    });
}
