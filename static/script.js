function generateList() {
    const selects = document.querySelectorAll('.meal-select');
    const totals = {};

    selects.forEach(select => {
        const meal = select.value;

        if (meal && MEALS[meal]) {
            const ingredients = MEALS[meal];

            Object.keys(ingredients).forEach(item => {
                if (!totals[item]) {
                    totals[item] = 0;
                }
                totals[item] += ingredients[item];
            });
        }
    });

    const sorted = Object.keys(totals).sort();

    let output = 'Shopping List\n\n';

    sorted.forEach(item => {
        output += `${item}: ${totals[item]}\n`;
    });

    document.getElementById('output').innerText = output;

    // 👇 SHOW THE CARD
    document.getElementById('output-card').style.display = 'block';
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