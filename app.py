import os
import sqlite3
from flask import Flask, request, jsonify, session, redirect, url_for, render_template

app = Flask(__name__)
app.secret_key = 'food_recommendation_system_secret_key_123!'

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'food.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if 'protein' column exists, otherwise reset DB to apply schema upgrade
    try:
        cursor.execute('SELECT protein FROM recipes LIMIT 1')
    except sqlite3.OperationalError:
        cursor.execute('DROP TABLE IF EXISTS recipes')
        
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
            image_url TEXT NOT NULL,
            protein INTEGER NOT NULL,
            fiber INTEGER NOT NULL,
            carbs INTEGER NOT NULL,
            fat INTEGER NOT NULL,
            health_goals TEXT NOT NULL
        )
    ''')
    
    # Check if empty, then pre-populate with 24 healthy recipes
    cursor.execute('SELECT COUNT(*) FROM recipes')
    if cursor.fetchone()[0] == 0:
        default_recipes = [
            # 1. Chana Masala
            ("Chana Masala", "Veg", "Indian", 280, "Spicy",
             "Chickpeas, Onion, Tomatoes, Ginger, Garlic, Garam Masala, Chili Powder, Coriander",
             "Sauté onions, ginger, and garlic. Add tomatoes and spices. Mix in boiled chickpeas and simmer. Garnish with fresh coriander.",
             "Rich in plant protein and dietary fiber. Spices like ginger and chili contain capsaicin and gingerols which help boost metabolism and regulate blood sugar levels.",
             "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500&auto=format&fit=crop",
             12, 8, 45, 6, "Weight Loss, Diabetes-Friendly, Heart-Healthy"),
            
            # 2. Paneer Tikka
            ("Paneer Tikka", "Veg", "Indian", 320, "Spicy",
             "Paneer (Cottage cheese), Bell Peppers, Onion, Yogurt, Lemon Juice, Tandoori Masala",
             "Marinate paneer cubes and veggies in spiced yogurt. Skewer them and grill or bake until charred.",
             "High-quality dairy protein and calcium. Capsicum adds Vitamin C, which enhances calcium absorption.",
             "https://images.unsplash.com/photo-1567188040759-fb8a883ea6d8?w=500&auto=format&fit=crop",
             18, 3, 10, 22, "Muscle Gain, Diabetes-Friendly"),
            
            # 3. Carrot Halwa
            ("Carrot Halwa (Healthy Version)", "Veg", "Indian", 240, "Sweet",
             "Grated Carrots, Skimmed Milk, Stevia/Honey, Cardamom Powder, Almonds",
             "Cook grated carrots in milk until soft. Sweeten with stevia or raw honey, flavor with cardamom, and garnish with sliced almonds.",
             "Extremely high in Beta-Carotene (Vitamin A precursor) for eye health. Reduced fat milk keeps calorie counts low.",
             "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?w=500&auto=format&fit=crop",
             6, 4, 35, 8, "Weight Loss, Heart-Healthy"),
            
            # 4. Moong Dal Payasam
            ("Moong Dal Payasam / Kheer", "Veg", "Indian", 190, "Sweet",
             "Yellow Moong Dal, Coconut Milk (Light), Jaggery (Minimal), Cardamom",
             "Roast and boil moong dal. Stir in light coconut milk and a dash of jaggery. Simmer with cardamom.",
             "Lentils provide essential amino acids. Light coconut milk yields medium-chain triglycerides (MCTs) which provide clean energy.",
             "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop",
             5, 3, 28, 6, "Weight Loss"),
            
            # 5. Chicken Tikka Masala
            ("Chicken Tikka Masala (Healthy)", "Non-Veg", "Indian", 420, "Spicy",
             "Chicken Breast, Tomato Puree, Greek Yogurt, Garlic, Ginger, Garam Masala",
             "Grill marinated chicken breast. Simmer in a light tomato-based yogurt sauce (no heavy cream).",
             "Lean protein source supporting muscle recovery. Greek yogurt replaces cream to cut saturated fat content by 75%.",
             "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&auto=format&fit=crop",
             35, 2, 12, 15, "Muscle Gain, Diabetes-Friendly"),
            
            # 6. Spicy Tomato Bruschetta
            ("Spicy Tomato Bruschetta", "Veg", "Italian", 150, "Spicy",
             "Whole Wheat Sourdough, Ripe Tomatoes, Garlic, Fresh Basil, Red Chili Flakes, Extra Virgin Olive Oil",
             "Toast sourdough. Toss diced tomatoes with minced garlic, basil, chili flakes, and olive oil. Spoon onto toast.",
             "Lycopene in cooked/ripe tomatoes is a powerful antioxidant. Monounsaturated fats in olive oil support cardiovascular health.",
             "https://images.unsplash.com/photo-1572656631137-7935297eff55?w=500&auto=format&fit=crop",
             4, 3, 22, 5, "Weight Loss, Heart-Healthy, Diabetes-Friendly"),
            
            # 7. Penne Arrabiata
            ("Penne Arrabiata (Low Carb)", "Veg", "Italian", 290, "Spicy",
             "Lentil Penne Pasta, Spicy Tomato Sauce, Chili Flakes, Garlic, Fresh Oregano, Basil",
             "Cook lentil pasta. Sauté garlic and chili flakes in olive oil, add tomato sauce. Toss pasta in sauce and garnish with herbs.",
             "Lentil pasta reduces the glycemic index and provides double the protein of traditional wheat-based pasta.",
             "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop",
             14, 6, 40, 4, "Weight Loss, Diabetes-Friendly, Heart-Healthy"),
            
            # 8. Healthy Berry Panna Cotta
            ("Healthy Berry Panna Cotta", "Veg", "Italian", 180, "Sweet",
             "Almond Milk, Agar-Agar (Vegetarian Gelatin), Honey, Vanilla Extract, Mixed Berries",
             "Dissolve agar-agar in almond milk, add vanilla and honey. Pour into molds and set. Top with mixed berry compote.",
             "Agar-agar is a soluble fiber that aids digestion. Berries are packed with anthocyanins (antioxidants) that combat oxidative stress.",
             "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=500&auto=format&fit=crop",
             3, 4, 20, 10, "Weight Loss, Heart-Healthy"),
            
            # 9. Tiramisu Oats Cup
            ("Tiramisu Oats Cup", "Veg", "Italian", 250, "Sweet",
             "Rolled Oats, Espresso Coffee, Chia Seeds, Greek Yogurt, Cocoa Powder, Honey",
             "Soak oats and chia seeds in espresso and milk overnight. Layer with honey-sweetened Greek yogurt and dust with cocoa powder.",
             "Chia seeds and oats provide beta-glucans which lower LDL cholesterol. Greek yogurt delivers probiotics for gut health.",
             "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&auto=format&fit=crop",
             12, 7, 32, 8, "Weight Loss, Diabetes-Friendly, Heart-Healthy"),
            
            # 10. Chicken Diavola
            ("Chicken Diavola", "Non-Veg", "Italian", 390, "Spicy",
             "Chicken Breast, Cayenne Pepper, Lemon Juice, Garlic, Rosemary, Olive Oil",
             "Marinate chicken in lemon juice, cayenne, rosemary, and garlic. Grill on high heat until cooked through.",
             "Cayenne pepper contains capsaicin which acts as an anti-inflammatory agent. Low cooking fat makes it heart-healthy.",
             "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=500&auto=format&fit=crop",
             38, 1, 4, 18, "Muscle Gain, Diabetes-Friendly"),
            
            # 11. Mapo Tofu
            ("Mapo Tofu (Healthy Veg)", "Veg", "Chinese", 230, "Spicy",
             "Silken Tofu, Mushrooms, Szechuan Peppercorns, Garlic, Chili Bean Paste, Soy Sauce",
             "Sauté mushrooms and garlic. Add chili bean paste, soy sauce, and water. Fold in tofu cubes and Szechuan peppercorns.",
             "Tofu is a complete plant protein containing all nine essential amino acids. Szechuan peppercorns improve digestive enzyme activity.",
             "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop",
             16, 4, 15, 12, "Muscle Gain, Weight Loss, Diabetes-Friendly, Heart-Healthy"),
            
            # 12. Kung Pao Cauliflower
            ("Kung Pao Cauliflower", "Veg", "Chinese", 210, "Spicy",
             "Cauliflower Florets, Peanuts, Green Onions, Dried Chilies, Low-Sodium Tamari, Sesame Oil",
             "Roast cauliflower florets. Stir-fry dried chilies and scallions in sesame oil, toss with cauliflower, tamari, and roasted peanuts.",
             "Cauliflower is rich in choline and glucosinolates (cancer-fighting compounds). Peanuts supply healthy unsaturated fats.",
             "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&auto=format&fit=crop",
             6, 5, 18, 12, "Weight Loss, Heart-Healthy"),
            
            # 13. Fried Bananas with Honey
            ("Fried Bananas with Honey", "Veg", "Chinese", 220, "Sweet",
             "Bananas, Raw Honey, Sesame Seeds, Coconut Oil (minimal)",
             "Lightly pan-fry banana slices in coconut oil until caramelized. Drizzle with raw honey and sprinkle with toasted sesame seeds.",
             "Bananas are high in potassium, helping to regulate blood pressure. Sesame seeds provide zinc and magnesium.",
             "https://images.unsplash.com/photo-1566393028639-d108a42c46a7?w=500&auto=format&fit=crop",
             3, 4, 48, 2, "Weight Loss"),
            
            # 14. Kung Pao Chicken
            ("Kung Pao Chicken (Light)", "Non-Veg", "Chinese", 410, "Spicy",
             "Chicken Breast, Bell Peppers, Zucchini, Dried Chilies, Light Soy Sauce, Ginger, Peanuts",
             "Stir-fry chicken cubes in minimal oil with ginger and dried chilies. Add bell peppers, zucchini, soy sauce, and toasted peanuts.",
             "High protein, low glycemic load. Incorporating zucchini and bell peppers reduces overall caloric density while adding fiber.",
             "https://images.unsplash.com/photo-1525755662778-989d0524087e?w=500&auto=format&fit=crop",
             36, 3, 14, 16, "Muscle Gain, Diabetes-Friendly"),
            
            # 15. Sweet and Sour Chicken
            ("Sweet and Sour Chicken (Baked)", "Non-Veg", "Chinese", 380, "Sweet",
             "Chicken Breast, Pineapple Chunks, Bell Peppers, Vinegar, Ketchup (No Added Sugar), Honey",
             "Bake chicken breast cubes. Make sauce with honey, vinegar, and sugar-free ketchup. Toss chicken, pineapples, and peppers in sauce.",
             "Bromelain in fresh pineapples assists in protein digestion. Baking instead of deep-frying reduces fat intake by 60%.",
             "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format&fit=crop",
             32, 2, 25, 10, "Muscle Gain"),

            # 16. Lentil Spinach Soup (Veg, Italian, Spicy)
            ("Lentil Spinach Soup", "Veg", "Italian", 190, "Spicy",
             "Brown Lentils, Fresh Spinach, Celery, Carrot, Garlic, Black Pepper, Olive Oil",
             "Sauté garlic, carrots, and celery. Add washed lentils and water. Simmer until soft. Stir in fresh spinach and black pepper.",
             "High in non-heme iron and folate. High fiber content slows down digestion, stabilizing glycemic index and helping cardiac health.",
             "https://images.unsplash.com/photo-1547592165-e1d17fed6005?w=500&auto=format&fit=crop",
             12, 9, 25, 3, "Weight Loss, Diabetes-Friendly, Heart-Healthy"),

            # 17. Tofu Broccoli Stir Fry (Veg, Chinese, Spicy)
            ("Tofu Broccoli Stir Fry", "Veg", "Chinese", 240, "Spicy",
             "Firm Tofu, Broccoli, Bell Peppers, Ginger, Chili Flakes, Soy Sauce, Sesame Oil",
             "Press and cube tofu. Stir-fry in sesame oil. Add chopped vegetables, ginger, soy sauce, and chili flakes. Toss together.",
             "Soy isoflavones improve cardiovascular markers. Cruciferous broccoli is rich in sulforaphane, helping liver detoxification and cellular repair.",
             "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&auto=format&fit=crop",
             15, 4, 12, 14, "Weight Loss, Diabetes-Friendly, Heart-Healthy, Muscle Gain"),

            # 18. Millet Veggie Khichdi (Veg, Indian, Spicy)
            ("Millet Veggie Khichdi", "Veg", "Indian", 270, "Spicy",
             "Foxtail Millet, Moong Dal, Turmeric, Ginger, Green Chilies, Cumin Seeds, Ghee",
             "Pressure cook millet and dal with turmeric, ginger, and green chilies. Temper with cumin seeds in minimal ghee.",
             "Millets are high-fiber, low-GI grains that prevent postprandial glucose spikes. Cumin aids digestive tract enzymes.",
             "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500&auto=format&fit=crop",
             8, 6, 48, 5, "Weight Loss, Diabetes-Friendly, Heart-Healthy"),

            # 19. Baked Salmon with Herbs (Non-Veg, Italian, Spicy)
            ("Baked Salmon with Herbs", "Non-Veg", "Italian", 350, "Spicy",
             "Salmon Fillet, Lemon Juice, Garlic, Black Pepper, Rosemary, Dill Leaves, Olive Oil",
             "Rub salmon with lemon juice, minced garlic, herbs, and olive oil. Bake at 400°F (200°C) for 12-15 minutes.",
             "High levels of Omega-3 fatty acids (EPA/DHA) reduce arterial inflammation and protect cardiac tissues while offering pure protein.",
             "https://images.unsplash.com/photo-1485962398705-ef6a13c41e8f?w=500&auto=format&fit=crop",
             34, 0, 2, 22, "Muscle Gain, Diabetes-Friendly, Heart-Healthy"),

            # 20. Steamed Fish in Ginger-Soy (Non-Veg, Chinese, Spicy)
            ("Steamed Fish in Ginger-Soy", "Non-Veg", "Chinese", 260, "Spicy",
             "White Fish Fillets (Cod/Tilapia), Ginger Juliennes, Scallions, Light Soy Sauce, Rice Wine, Cilantro",
             "Place fish on steam plate, cover with ginger and white wine. Steam for 8 minutes. Drizzle hot soy sauce and scallions on top.",
             "Lean source of highly bioavailable protein. Ginger contains gingerol which alleviates digestive tract inflammation.",
             "https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=500&auto=format&fit=crop",
             28, 1, 6, 12, "Muscle Gain, Weight Loss, Diabetes-Friendly, Heart-Healthy"),

            # 21. High-Protein Chicken Salad (Non-Veg, Italian, Spicy)
            ("High-Protein Chicken Salad", "Non-Veg", "Italian", 310, "Spicy",
             "Grilled Chicken Breast, Romaine Lettuce, Cherry Tomatoes, Cucumber, Olive Oil, Lemon-Oregano Vinaigrette",
             "Toss grilled chicken strips with chopped romaine, tomatoes, and cucumbers. Drizzle olive oil and lemon juice dressing.",
             "Lean protein supports lean mass preservation during weight loss. Tomatoes add beta-carotene and cardiovascular antioxidants.",
             "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop",
             36, 4, 8, 14, "Muscle Gain, Weight Loss, Diabetes-Friendly"),

            # 22. Sweet Mango Yogurt Bowl (Veg, Indian, Sweet)
            ("Sweet Mango Yogurt Bowl", "Veg", "Indian", 210, "Sweet",
             "Low-Fat Greek Yogurt, Fresh Mango Puree, Chia Seeds, Mint Leaves, Honey",
             "Whisk yogurt. Layer mango puree and yogurt in a bowl. Top with chia seeds, mint, and a drop of honey.",
             "Greek yogurt offers slow-digesting casein protein. Mangoes provide vitamin C and soluble dietary fibers.",
             "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=500&auto=format&fit=crop",
             14, 3, 28, 4, "Weight Loss, Muscle Gain"),

            # 23. Steamed Chicken Dumplings (Non-Veg, Chinese, Sweet)
            ("Steamed Chicken Dumplings", "Non-Veg", "Chinese", 290, "Sweet",
             "Ground Chicken Breast, Wonton Wrappers, Cabbage, Ginger, Honey-Soy Dipping Sauce",
             "Mix chicken, cabbage, and ginger. Fill wrappers, fold and steam for 10 minutes. Serve with a touch of honey-soy dip.",
             "Steaming preserves nutrients without introducing extra lipids. High protein content aids cellular repair.",
             "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=500&auto=format&fit=crop",
             22, 2, 32, 6, "Muscle Gain, Weight Loss"),

            # 24. Apple Cinnamon Oats Payasam (Veg, Indian, Sweet)
            ("Apple Cinnamon Oats Payasam", "Veg", "Indian", 220, "Sweet",
             "Rolled Oats, Apple Grates, Skimmed Milk, Cinnamon Powder, Stevia",
             "Boil oats in skimmed milk. Stir in grated apples, cinnamon powder, and stevia. Simmer until thick.",
             "Oats are rich in beta-glucan fiber, which binds bile acids to lower serum cholesterol levels. Cinnamon improves insulin sensitivity.",
             "https://images.unsplash.com/photo-1517881917431-13488d5371a7?w=500&auto=format&fit=crop",
             6, 5, 38, 4, "Weight Loss, Heart-Healthy, Diabetes-Friendly")
        ]
        cursor.executemany('''
            INSERT INTO recipes (
                name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url,
                protein, fiber, carbs, fat, health_goals
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_recipes)
        conn.commit()
    conn.close()

# Run DB migration on startup
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
        'image_url': row['image_url'],
        'protein': row['protein'],
        'fiber': row['fiber'],
        'carbs': row['carbs'],
        'fat': row['fat'],
        'health_goals': row['health_goals']
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
    max_calories = int(data.get('calories', 400))
    taste = data.get('taste')
    goal = data.get('goal', 'General Wellness')
    
    logs = []
    recommendations = []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Helper to check if a goal filter is active
    has_goal = goal and goal != 'General Wellness'
    goal_query_param = f"%{goal}%"
    
    # RULE 1: Exact Match (with Goal if active)
    if has_goal:
        logs.append(f"Evaluating Rule 1 (Exact Match): IF diet = '{diet}' AND cuisine = '{cuisine}' AND taste = '{taste}' AND calories <= {max_calories} AND health_goals contains '{goal}'")
        cursor.execute('''
            SELECT * FROM recipes 
            WHERE diet = ? AND cuisine = ? AND taste = ? AND calories <= ? AND health_goals LIKE ?
        ''', (diet, cuisine, taste, max_calories, goal_query_param))
    else:
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
        if has_goal:
            logs.append(f"Evaluating Rule 2 (Calorie Relaxation): IF no exact match THEN relax calorie limit by 25% (up to {relaxed_calories} kcal) keeping goal = '{goal}' for diet = '{diet}', cuisine = '{cuisine}', taste = '{taste}'")
            cursor.execute('''
                SELECT * FROM recipes 
                WHERE diet = ? AND cuisine = ? AND taste = ? AND calories <= ? AND health_goals LIKE ?
            ''', (diet, cuisine, taste, relaxed_calories, goal_query_param))
        else:
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
            
            # RULE 3: Taste Shifting (Alternative Taste, keeping goal)
            if has_goal:
                logs.append(f"Evaluating Rule 3 (Taste Broadening): IF no match with relaxed calories THEN broaden taste profile to match ANY taste for cuisine = '{cuisine}', diet = '{diet}', goal = '{goal}' under {max_calories} kcal")
                cursor.execute('''
                    SELECT * FROM recipes 
                    WHERE diet = ? AND cuisine = ? AND calories <= ? AND health_goals LIKE ?
                ''', (diet, cuisine, max_calories, goal_query_param))
            else:
                logs.append(f"Evaluating Rule 3 (Taste Broadening): IF no match with relaxed calories THEN broaden taste profile to match ANY taste for cuisine = '{cuisine}' and diet = '{diet}' under {max_calories} kcal")
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
                
                # RULE 4: Cuisine Generalization (keeping goal)
                if has_goal:
                    logs.append(f"Evaluating Rule 4 (Cuisine Generalization): IF no match in '{cuisine}' cuisine THEN generalize search across all cuisines for diet = '{diet}', taste = '{taste}', goal = '{goal}' under {max_calories} kcal")
                    cursor.execute('''
                        SELECT * FROM recipes 
                        WHERE diet = ? AND taste = ? AND calories <= ? AND health_goals LIKE ?
                    ''', (diet, taste, max_calories, goal_query_param))
                else:
                    logs.append(f"Evaluating Rule 4 (Cuisine Generalization): IF no match in '{cuisine}' cuisine THEN generalize search across all cuisines for diet = '{diet}', taste = '{taste}' under {max_calories} kcal")
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
                    
                    # RULE 5: Goal-based Generalization (Ignore cuisine and taste, filter only diet and goal)
                    if has_goal:
                        logs.append(f"Evaluating Rule 5 (Goal-based Broadening): IF no specific match THEN search for any '{diet}' recipe matching goal = '{goal}' under calorie limit <= {max_calories}")
                        cursor.execute('''
                            SELECT * FROM recipes 
                            WHERE diet = ? AND calories <= ? AND health_goals LIKE ?
                        ''', (diet, max_calories, goal_query_param))
                        rows = cursor.fetchall()
                        
                        if rows:
                            logs.append(f"-> [SUCCESS] Rule 5 triggered. Found {len(rows)} recipe(s) matching health goal.")
                            recommendations = [serialize_recipe(r) for r in rows]
                        else:
                            logs.append(f"-> [FAILED] No recipes found matching goal '{goal}' under {max_calories} kcal.")
                    else:
                        logs.append("Evaluating Rule 5: Skipping goal-based broadening (no health goal selected).")
                        rows = None
                    
                    if not recommendations:
                        # RULE 6: Global Fallback (Drop Goal entirely, look for any recipe with diet under calorie limit)
                        if has_goal:
                            logs.append(f"Evaluating Rule 6 (Global Fallback - Drop Goal): IF no goal-matching recipe found THEN drop goal filter and search for any '{diet}' recipe under calorie limit <= {max_calories}")
                        else:
                            logs.append(f"Evaluating Rule 6 (Global Fallback): IF no specific match found THEN fallback to any '{diet}' recipe under calorie limit <= {max_calories}")
                        
                        cursor.execute('''
                            SELECT * FROM recipes 
                            WHERE diet = ? AND calories <= ?
                        ''', (diet, max_calories))
                        rows = cursor.fetchall()
                        
                        if rows:
                            logs.append(f"-> [SUCCESS] Rule 6 triggered. Found {len(rows)} fallback recipe(s).")
                            recommendations = [serialize_recipe(r) for r in rows]
                        else:
                            logs.append(f"-> [FAILED] No recipes found under {max_calories} kcal for '{diet}' diet.")
                            
                            # RULE 7: Absolute Lowest Calorie Recipe (Emergency Match)
                            logs.append(f"Evaluating Rule 7 (Lowest Calorie Fallback): Find the absolute lowest calorie recipe for '{diet}' diet.")
                            cursor.execute('''
                                SELECT * FROM recipes 
                                WHERE diet = ? 
                                ORDER BY calories ASC LIMIT 1
                            ''', (diet,))
                            row = cursor.fetchone()
                            if row:
                                logs.append(f"-> [SUCCESS] Rule 7 triggered. Recommending lowest calorie recipe: '{row['name']}' ({row['calories']} kcal).")
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
    protein = data.get('protein')
    fiber = data.get('fiber')
    carbs = data.get('carbs')
    fat = data.get('fat')
    health_goals = data.get('health_goals')
    
    if not all([name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url, health_goals]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        calories = int(calories)
        protein = int(protein or 10)
        fiber = int(fiber or 2)
        carbs = int(carbs or 30)
        fat = int(fat or 10)
    except ValueError:
        return jsonify({'error': 'Numeric fields must be integers'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recipes (name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url,
                             protein, fiber, carbs, fat, health_goals)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url,
          protein, fiber, carbs, fat, health_goals))
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
    protein = data.get('protein')
    fiber = data.get('fiber')
    carbs = data.get('carbs')
    fat = data.get('fat')
    health_goals = data.get('health_goals')
    
    if not all([recipe_id, name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url, health_goals]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        calories = int(calories)
        protein = int(protein or 10)
        fiber = int(fiber or 2)
        carbs = int(carbs or 30)
        fat = int(fat or 10)
    except ValueError:
        return jsonify({'error': 'Numeric fields must be integers'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE recipes 
        SET name = ?, diet = ?, cuisine = ?, calories = ?, taste = ?, ingredients = ?, instructions = ?, scientific_backing = ?, image_url = ?,
            protein = ?, fiber = ?, carbs = ?, fat = ?, health_goals = ?
        WHERE id = ?
    ''', (name, diet, cuisine, calories, taste, ingredients, instructions, scientific_backing, image_url,
          protein, fiber, carbs, fat, health_goals, recipe_id))
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
