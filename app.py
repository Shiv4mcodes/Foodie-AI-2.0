import os
import sqlite3
try:
    from flask import Flask, request, jsonify, session, redirect, url_for, render_template  # type: ignore[reportMissingImports]
except ImportError as exc:
    raise ImportError("Flask is required to run this application. Install it with `pip install flask`.") from exc

app = Flask(__name__)
app.secret_key = 'food_recommendation_system_secret_key_123!'

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'food.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            diet TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            calories INTEGER NOT NULL,
            taste TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            scientific_backing TEXT NOT NULL,
            image_url TEXT NOT NULL
        )
    ''')
    conn.commit()
    
    # Check if empty, then pre-populate
    cursor.execute('SELECT COUNT(*) FROM recipes')
    if cursor.fetchone()[0] == 0:
        default_recipes = [
            ("Chana Masala", "Veg", "Indian", 280, "Spicy",
             "Chickpeas, Onion, Tomatoes, Ginger, Garlic, Garam Masala, Chili Powder, Coriander",
             "Sauté onions, ginger, and garlic. Add tomatoes and spices. Mix in boiled chickpeas and simmer. Garnish with fresh coriander.",
             "Rich in plant protein and dietary fiber. Spices like ginger and chili contain capsaicin and gingerols which help boost metabolism and regulate blood sugar levels.",
             "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500&auto=format&fit=crop"),
            
            ("Paneer Tikka", "Veg", "Indian", 320, "Spicy",
             "Paneer (Cottage cheese), Bell Peppers, Onion, Yogurt, Lemon Juice, Tandoori Masala",
             "Marinate paneer cubes and veggies in spiced yogurt. Skewer them and grill or bake until charred.",
             "High-quality dairy protein and calcium. Capsicum adds Vitamin C, which enhances calcium absorption.",
             "https://images.unsplash.com/photo-1567188040759-fb8a883ea6d8?w=500&auto=format&fit=crop"),
            
            ("Carrot Halwa (Healthy Version)", "Veg", "Indian", 240, "Sweet",
             "Grated Carrots, Skimmed Milk, Stevia/Honey, Cardamom Powder, Almonds",
             "Cook grated carrots in milk until soft. Sweeten with stevia or raw honey, flavor with cardamom, and garnish with sliced almonds.",
             "Extremely high in Beta-Carotene (Vitamin A precursor) for eye health. Reduced fat milk keeps calorie counts low.",
             "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?w=500&auto=format&fit=crop"),
            
            ("Moong Dal Payasam / Kheer", "Veg", "Indian", 190, "Sweet",
             "Yellow Moong Dal, Coconut Milk (Light), Jaggery (Minimal), Cardamom",
             "Roast and boil moong dal. Stir in light coconut milk and a dash of jaggery. Simmer with cardamom.",
             "Lentils provide essential amino acids. Light coconut milk yields medium-chain triglycerides (MCTs) which provide clean energy.",
             "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop"),
            
            ("Chicken Tikka Masala (Healthy)", "Non-Veg", "Indian", 420, "Spicy",
             "Chicken Breast, Tomato Puree, Greek Yogurt, Garlic, Ginger, Garam Masala",
             "Grill marinated chicken breast. Simmer in a light tomato-based yogurt sauce (no heavy cream).",
             "Lean protein source supporting muscle recovery. Greek yogurt replaces cream to cut saturated fat content by 75%.",
             "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&auto=format&fit=crop"),
            
            ("Spicy Tomato Bruschetta", "Veg", "Italian", 150, "Spicy",
             "Whole Wheat Sourdough, Ripe Tomatoes, Garlic, Fresh Basil, Red Chili Flakes, Extra Virgin Olive Oil",
             "Toast sourdough. Toss diced tomatoes with minced garlic, basil, chili flakes, and olive oil. Spoon onto toast.",
             "Lycopene in cooked/ripe tomatoes is a powerful antioxidant. Monounsaturated fats in olive oil support cardiovascular health.",
             "https://images.unsplash.com/photo-1572656631137-7935297eff55?w=500&auto=format&fit=crop"),
            
            ("Penne Arrabiata (Low Carb)", "Veg", "Italian", 290, "Spicy",
             "Lentil Penne Pasta, Spicy Tomato Sauce, Chili Flakes, Garlic, Fresh Oregano, Basil",
             "Cook lentil pasta. Sauté garlic and chili flakes in olive oil, add tomato sauce. Toss pasta in sauce and garnish with herbs.",
             "Lentil pasta reduces the glycemic index and provides double the protein of traditional wheat-based pasta.",
             "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop"),
            
            ("Healthy Berry Panna Cotta", "Veg", "Italian", 180, "Sweet",
             "Almond Milk, Agar-Agar (Vegetarian Gelatin), Honey, Vanilla Extract, Mixed Berries",
             "Dissolve agar-agar in almond milk, add vanilla and honey. Pour into molds and set. Top with mixed berry compote.",
             "Agar-agar is a soluble fiber that aids digestion. Berries are packed with anthocyanins (antioxidants) that combat oxidative stress.",
             "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=500&auto=format&fit=crop"),
            
            ("Tiramisu Oats Cup", "Veg", "Italian", 250, "Sweet",
             "Rolled Oats, Espresso Coffee, Chia Seeds, Greek Yogurt, Cocoa Powder, Honey",
             "Soak oats and chia seeds in espresso and milk overnight. Layer with honey-sweetened Greek yogurt and dust with cocoa powder.",
             "Chia seeds and oats provide beta-glucans which lower LDL cholesterol. Greek yogurt delivers probiotics for gut health.",
             "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&auto=format&fit=crop"),
            
            ("Chicken Diavola", "Non-Veg", "Italian", 390, "Spicy",
             "Chicken Breast, Cayenne Pepper, Lemon Juice, Garlic, Rosemary, Olive Oil",
             "Marinate chicken in lemon juice, cayenne, rosemary, and garlic. Grill on high heat until cooked through.",
             "Cayenne pepper contains capsaicin which acts as an anti-inflammatory agent. Low cooking fat makes it heart-healthy.",
             "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=500&auto=format&fit=crop"),
            
            ("Mapo Tofu (Healthy Veg)", "Veg", "Chinese", 230, "Spicy",
             "Silken Tofu, Mushrooms, Szechuan Peppercorns, Garlic, Chili Bean Paste, Soy Sauce",
             "Sauté mushrooms and garlic. Add chili bean paste, soy sauce, and water. Fold in tofu cubes and Szechuan peppercorns.",
             "Tofu is a complete plant protein containing all nine essential amino acids. Szechuan peppercorns improve digestive enzyme activity.",
             "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop"),
            
            ("Kung Pao Cauliflower", "Veg", "Chinese", 210, "Spicy",
             "Cauliflower Florets, Peanuts, Green Onions, Dried Chilies, Low-Sodium Tamari, Sesame Oil",
             "Roast cauliflower florets. Stir-fry dried chilies and scallions in sesame oil, toss with cauliflower, tamari, and roasted peanuts.",
             "Cauliflower is rich in choline and glucosinolates (cancer-fighting compounds). Peanuts supply healthy unsaturated fats.",
             "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&auto=format&fit=crop"),
            
            ("Fried Bananas with Honey", "Veg", "Chinese", 220, "Sweet",
             "Bananas, Raw Honey, Sesame Seeds, Coconut Oil (minimal)",
             "Lightly pan-fry banana slices in coconut oil until caramelized. Drizzle with raw honey and sprinkle with toasted sesame seeds.",
             "Bananas are high in potassium, helping to regulate blood pressure. Sesame seeds provide zinc and magnesium.",
             "https://images.unsplash.com/photo-1566393028639-d108a42c46a7?w=500&auto=format&fit=crop"),
            
            ("Kung Pao Chicken (Light)", "Non-Veg", "Chinese", 410, "Spicy",
             "Chicken Breast, Bell Peppers, Zucchini, Dried Chilies, Light Soy Sauce, Ginger, Peanuts",
             "Stir-fry chicken cubes in minimal oil with ginger and dried chilies. Add bell peppers, zucchini, soy sauce, and toasted peanuts.",
             "High protein, low glycemic load. Incorporating zucchini and bell peppers reduces overall caloric density while adding fiber.",
             "https://images.unsplash.com/photo-1525755662778-989d0524087e?w=500&auto=format&fit=crop"),
            
            ("Sweet and Sour Chicken (Baked)", "Non-Veg", "Chinese", 380, "Sweet",
             "Chicken Breast, Pineapple Chunks, Bell Peppers, Vinegar, Ketchup (No Added Sugar), Honey",
             "Bake chicken breast cubes. Make sauce with honey, vinegar, and sugar-free ketchup. Toss chicken, pineapples, and peppers in sauce.",
             "Bromelain in fresh pineapples assists in protein digestion. Baking instead of deep-frying reduces fat intake by 60%.",
             "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format&fit=crop")
        ]
        cursor.executemany('''
            INSERT INTO recipes (name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_recipes)
        conn.commit()
    conn.close()

# Initialize DB on import/startup
init_db()

def serialize_recipe(row):
    return {
        'id': row['id'],
        'name': row['name'],
        'diet': row['diet'],
        'cuisine': row['cuisine'],
        'calories': row['calories'],
        'taste': row['taste'],
        'ingredients': row['ingredients'],
        'instructions': row['instructions'],
        'scientific_backing': row['scientific_backing'],
        'image_url': row['image_url']
    }

# ----------------- ROUTES -----------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Invalid Username or Password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html')

# ----------------- RECOMMENDATION ENGINE -----------------

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    data = request.json or {}
    diet = data.get('diet')
    cuisine = data.get('cuisine')
    max_calories = int(data.get('calories', 500))
    taste = data.get('taste')
    
    logs = []
    recommendations = []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # RULE 1: Exact match
    logs.append(f"Evaluating Rule 1 (Exact Match): IF diet = '{diet}' AND cuisine = '{cuisine}' AND taste = '{taste}' AND calories <= {max_calories}")
    cursor.execute('''
        SELECT * FROM recipes 
        WHERE diet = ? AND cuisine = ? AND taste = ? AND calories <= ?
    ''', (diet, cuisine, taste, max_calories))
    rows = cursor.fetchall()
    
    if rows:
        logs.append(f"-> [SUCCESS] Rule 1 triggered. Found {len(rows)} exact match(es).")
        recommendations = [serialize_recipe(r) for r in rows]
    else:
        logs.append(f"-> [FAILED] No recipes matched Rule 1 criteria.")
        
        # RULE 2: Calorie Relaxation (Up to 25% extra calories)
        relaxed_calories = int(max_calories * 1.25)
        logs.append(f"Evaluating Rule 2 (Calorie Relaxation): IF no exact match THEN relax calorie limit by 25% (up to {relaxed_calories} kcal) for diet = '{diet}', cuisine = '{cuisine}', taste = '{taste}'")
        cursor.execute('''
            SELECT * FROM recipes 
            WHERE diet = ? AND cuisine = ? AND taste = ? AND calories <= ?
        ''', (diet, cuisine, taste, relaxed_calories))
        rows = cursor.fetchall()
        
        if rows:
            logs.append(f"-> [SUCCESS] Rule 2 triggered. Found {len(rows)} match(es) with relaxed calorie limits.")
            recommendations = [serialize_recipe(r) for r in rows]
        else:
            logs.append(f"-> [FAILED] No recipes matched under Rule 2.")
            
            # RULE 3: Taste Shifting (Alternative Taste)
            logs.append(f"Evaluating Rule 3 (Taste Broadening): IF no match with relaxed calories THEN broaden taste profile to match ANY taste for cuisine = '{cuisine}' and diet = '{diet}' within calorie limit <= {max_calories}")
            cursor.execute('''
                SELECT * FROM recipes 
                WHERE diet = ? AND cuisine = ? AND calories <= ?
            ''', (diet, cuisine, max_calories))
            rows = cursor.fetchall()
            
            if rows:
                logs.append(f"-> [SUCCESS] Rule 3 triggered. Found {len(rows)} match(es) by shifting taste preference.")
                recommendations = [serialize_recipe(r) for r in rows]
            else:
                logs.append(f"-> [FAILED] No recipes matched under Rule 3.")
                
                # RULE 4: Cuisine Generalization
                logs.append(f"Evaluating Rule 4 (Cuisine Generalization): IF no match in '{cuisine}' cuisine THEN generalize search across all cuisines for diet = '{diet}', taste = '{taste}', calories <= {max_calories}")
                cursor.execute('''
                    SELECT * FROM recipes 
                    WHERE diet = ? AND taste = ? AND calories <= ?
                ''', (diet, taste, max_calories))
                rows = cursor.fetchall()
                
                if rows:
                    logs.append(f"-> [SUCCESS] Rule 4 triggered. Found {len(rows)} match(es) in other cuisines.")
                    recommendations = [serialize_recipe(r) for r in rows]
                else:
                    logs.append(f"-> [FAILED] No recipes matched under Rule 4.")
                    
                    # RULE 5: Diet and Calorie Match (Global Fallback)
                    logs.append(f"Evaluating Rule 5 (Global Fallback): IF no specific match found THEN fallback to any '{diet}' recipe under calorie limit <= {max_calories}")
                    cursor.execute('''
                        SELECT * FROM recipes 
                        WHERE diet = ? AND calories <= ?
                    ''', (diet, max_calories))
                    rows = cursor.fetchall()
                    
                    if rows:
                        logs.append(f"-> [SUCCESS] Rule 5 triggered. Found {len(rows)} fallback recipe(s).")
                        recommendations = [serialize_recipe(r) for r in rows]
                    else:
                        logs.append(f"-> [FAILED] No recipes found under {max_calories} kcal for '{diet}' diet.")
                        
                        # RULE 6: Absolute Lowest Calorie Recipe (Emergency Match)
                        logs.append(f"Evaluating Rule 6 (Lowest Calorie Fallback): Find the absolute lowest calorie recipe for '{diet}' diet.")
                        cursor.execute('''
                            SELECT * FROM recipes 
                            WHERE diet = ? 
                            ORDER BY calories ASC LIMIT 1
                        ''', (diet,))
                        row = cursor.fetchone()
                        if row:
                            logs.append(f"-> [SUCCESS] Rule 6 triggered. Recommending lowest calorie recipe: '{row['name']}' ({row['calories']} kcal).")
                            recommendations = [serialize_recipe(row)]
                        else:
                            logs.append(f"-> [FAILED] No recipes found at all.")
    
    conn.close()
    return jsonify({
        'recommendations': recommendations,
        'logs': logs
    })

# ----------------- ADMIN API ENDPOINTS -----------------

@app.route('/api/admin/recipes', methods=['GET'])
def api_admin_recipes():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recipes ORDER BY id DESC')
    rows = cursor.fetchall()
    recipes = [serialize_recipe(r) for r in rows]
    conn.close()
    return jsonify(recipes)

@app.route('/api/admin/add', methods=['POST'])
def api_admin_add():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json or {}
    name = data.get('name')
    diet = data.get('diet')
    cuisine = data.get('cuisine')
    calories = data.get('calories')
    taste = data.get('taste')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')
    scientific_backing = data.get('scientific_backing')
    image_url = data.get('image_url')
    
    if not all([name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        calories = int(calories)
    except ValueError:
        return jsonify({'error': 'Calories must be an integer'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recipes (name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Recipe added successfully!'})

@app.route('/api/admin/edit', methods=['POST'])
def api_admin_edit():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json or {}
    recipe_id = data.get('id')
    name = data.get('name')
    diet = data.get('diet')
    cuisine = data.get('cuisine')
    calories = data.get('calories')
    taste = data.get('taste')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')
    scientific_backing = data.get('scientific_backing')
    image_url = data.get('image_url')
    
    if not all([recipe_id, name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        calories = int(calories)
    except ValueError:
        return jsonify({'error': 'Calories must be an integer'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE recipes 
        SET name = ?, diet = ?, cuisine = ?, calories = ?, taste = ?, ingredients = ?, instructions = ?, scientific_backing = ?, image_url = ?
        WHERE id = ?
    ''', (name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url, recipe_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Recipe updated successfully!'})

@app.route('/api/admin/delete/<int:recipe_id>', methods=['DELETE'])
def api_admin_delete(recipe_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Recipe deleted successfully!'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
