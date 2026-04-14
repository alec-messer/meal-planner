function toggleDeletePanel() {
    document.getElementById('deletePanel').classList.toggle('open');
}

function togglePanel() {
    const panel = document.getElementById('sidePanel');
    panel.classList.toggle('open');
}

function addIngredient() {
    const container = document.getElementById('ingredients-container');

    const row = document.createElement('div');
    row.className = 'ingredient-row';

    row.innerHTML = `
        <input name="ingredient_name[]" placeholder="Ingredient" required>
        <input name="ingredient_qty[]" placeholder="Qty" type="number" step="any" required>

        <select name="ingredient_unit[]" required>
            <option value="">Unit</option>
            <option value="grams">grams</option>
            <option value="items">items</option>
        </select>

        <select name="ingredient_type[]" required>
            <option value="">Type</option>
            <option value="meat">meat</option>
            <option value="dairy">dairy</option>
            <option value="fruit">fruit</option>
            <option value="veg">veg</option>
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

            items.push({
                name,
                qty,
                unit
            });
        });
    });

    return items; // ← return array directly (matches Python)
}

function appendBasketToOutput(basket) {
    let text = '\nOPTIMISED BASKET\n\n';

    basket.forEach(item => {
        text += `${item.quantity} x ${item.search} (£${item.total_price})\n`;
    });

    document.getElementById('output').innerText += text;
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
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(shoppingJSON)
    })
    .then(res => res.json())
    .then(data => {
        console.log('Optimised basket:', data.basket);

        let output = '';

        // 📅 DATE
        const now = new Date();
        const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

        const dayName = days[now.getDay()];
        const date = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');

        const dateHeader = `${dayName} ${date}/${month}`;

        output += `Shopping List\n${dateHeader}\n\n`;

        const typeOrder = ['meat', 'veg', 'fruit', 'dairy', 'other'];

        typeOrder.forEach(type => {
            const items = totals[type];

            if (Object.keys(items).length === 0) return;

            output += `${type.toUpperCase()}\n`;

            const rows = Object.keys(items).sort().map(item => {
                const { qty, unit } = items[item];
                const left = `${qty} (${unit})`;
                return { name: item, left };
            });

            const maxLeftLength = Math.max(...rows.map(r => r.left.length));

            rows.forEach(row => {
                const paddedLeft = row.left.padEnd(maxLeftLength, ' ');
                output += `${paddedLeft}  ${row.name}\n`;
            });

            output += `\n`;
        });

        // Add optimised basket
        output += `OPTIMISED BASKET\n\n`;

        data.basket.forEach(item => {
            output += `${item.quantity} x ${item.search} (£${item.total_price})\n`;
        });

        // Add basket link
        if (data.basket_url) {
            output += `\nOpen basket:\n${data.basket_url}\n`;
        }

        document.getElementById('output').innerText = output;
        document.getElementById('output-card').classList.remove('hidden');
    })
    .catch(err => {
        console.error('API error:', err);
    });
}

function shareList() {
    const text = document.getElementById('output').innerText;

    if (!text.trim()) {
        alert('Generate a list first');
        return;
    }

    if (navigator.share) {
        navigator.share({
            title: 'Shopping List',
            text: text
        });
    } else {
        alert('Sharing not supported');
    }
}

/* FORM VALIDATION */
document.addEventListener('input', () => {
    const name = document.getElementById('mealName').value.trim();
    const names = document.querySelectorAll('input[name="ingredient_name[]"]');
    const qtys = document.querySelectorAll('input[name="ingredient_qty[]"]');
    const units = document.querySelectorAll('select[name="ingredient_unit[]"]');
    const types = document.querySelectorAll('select[name="ingredient_type[]"]');

    let valid = name.length > 0;

    names.forEach((n, i) => {
        if (
            !n.value.trim() ||
            !qtys[i].value ||
            !units[i].value ||
            !types[i].value
        ) {
            valid = false;
        }
    });

    document.getElementById('submitMeal').disabled = !valid;
});

document.getElementById('mealForm').addEventListener('submit', () => {
    setTimeout(() => {
        document.getElementById('mealForm').reset();

        const container = document.getElementById('ingredients-container');

        container.innerHTML = `
            <div class="ingredient-row">
                <input name="ingredient_name[]" placeholder="Ingredient" required>
                <input name="ingredient_qty[]" placeholder="Qty" type="number" step="any" required>

                <select name="ingredient_unit[]" required>
                    <option value="">Unit</option>
                    <option value="grams">grams</option>
                    <option value="items">items</option>
                </select>

                <select name="ingredient_type[]" required>
                    <option value="">Type</option>
                    <option value="meat">meat</option>
                    <option value="dairy">dairy</option>
                    <option value="fruit">fruit</option>
                    <option value="veg">veg</option>
                    <option value="other">other</option>
                </select>
            </div>
        `;
    }, 50);
});

['successBanner', 'deleteBanner'].forEach(id => {
    const banner = document.getElementById(id);

    if (banner) {
        setTimeout(() => {
            banner.remove();
        }, 4500);
    }
});
