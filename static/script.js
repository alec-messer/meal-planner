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
    `;

    container.appendChild(row);
}

function generateList() {
    const selects = document.querySelectorAll('.meal-select');
    const totals = {};

    selects.forEach(select => {
        const meal = select.value;

        if (meal && MEALS[meal]) {
            const ingredients = MEALS[meal];

            Object.keys(ingredients).forEach(item => {
                totals[item] = (totals[item] || 0) + ingredients[item];
            });
        }
    });

    const sorted = Object.keys(totals).sort();

    // 📅 GET FORMATTED DATE
    const now = new Date();

    const days = [
        'Sunday','Monday','Tuesday','Wednesday',
        'Thursday','Friday','Saturday'
    ];

    const dayName = days[now.getDay()];

    const date = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');

    const dateHeader = `${dayName} ${date}/${month}`;

    // 🧾 BUILD OUTPUT
    let output = `Shopping List\n${dateHeader}\n\n`;

    sorted.forEach(item => {
        output += `${item}: ${totals[item]}\n`;
    });

    document.getElementById('output').innerText = output;
    document.getElementById('output-card').classList.remove('hidden');
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

/* ✅ FORM VALIDATION */
document.addEventListener('input', () => {
    const name = document.getElementById('mealName').value.trim();
    const names = document.querySelectorAll('input[name="ingredient_name[]"]');
    const qtys = document.querySelectorAll('input[name="ingredient_qty[]"]');

    let valid = name.length > 0;

    names.forEach((n, i) => {
        if (!n.value.trim() || !qtys[i].value) {
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
            </div>
        `;
    }, 50);
});
