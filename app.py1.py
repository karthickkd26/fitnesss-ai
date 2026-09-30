import streamlit as st
import time

# Page Configuration
st.set_page_config(
    page_title="FitBuddy- AI Fitness & Diet Generator",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Fitness Theme)
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FF4757;
        text-align: center;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 1.15rem;
        text-align: center;
        color: #666;
        margin-bottom: 1.8rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF4757, #ff6b81);
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0.6rem 1.5rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.4);
        width: 100%;
        height: 3.2em;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-title'>🏋️‍♂️ FitBuddy: AI Fitness & Meal Planner</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Instant personalized workout routines, macronutrient breakdown, and diet schedules</div>", unsafe_allow_html=True)

# Sidebar (Cleaned up)
with st.sidebar:
    st.header("⚡ FitBuddy System")
    st.success("🟢 System Active & Ready")
    st.markdown("### 🏆 How It Works")
    st.markdown("""
    1. **Enter Your Stats**: Fill in your age, height, weight, and fitness targets.
    2. **Customize Diet & Gear**: Pick your preferred meal type and workout setting.
    """)

# Main Form
st.subheader("📋 Step 1: Your Biometrics & Goals")
col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age (Years)", min_value=12, max_value=100, value=12)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=175.0, step=0.5)

with col2:
    current_weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=250.0, value=70.0, step=0.5)
    target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=250.0, value=65.0, step=0.5)
    activity_level = st.selectbox(
        "Activity Level",
        [
            "Sedentary (Little/No exercise, desk job)",
            "Lightly Active (1-3 workout days/week)",
            "Moderately Active (3-5 workout days/week)",
            "Very Active (6-7 workout days/week)"
        ],
        index=1
    )

with col3:
    goal = st.selectbox(
        "Fitness Goal",
        [
            "Weight Loss & Fat Burn",
            "Muscle Building & Bulking",
            "Lean Body Recomposition",
            "Strength & Stamina",
            "General Health & Fitness"
        ]
    )
    experience = st.selectbox(
        "Experience Level",
        ["Beginner (0-6 months)", "Intermediate (6 months - 2 years)", "Advanced (2+ years)"]
    )
    workout_location = st.selectbox(
        "Workout Location & Gear",
        [
            "Commercial Gym (Full Equipment)",
            "Home Workout (Dumbbells Only)",
            "Home Workout (Bodyweight Only / Calisthenics)"
        ]
    )

st.subheader("🥗 Step 2: Diet & Lifestyle")
d_col1, d_col2 = st.columns(2)

with d_col1:
    diet_type = st.selectbox(
        "Dietary Lifestyle",
        ["Non-Vegetarian", "Vegetarian", "Vegan", "Eggetarian", "Keto / Low-Carb", "Mediterranean"]
    )
    meals_per_day = st.slider("Meals per Day", min_value=2, max_value=6, value=3)

with d_col2:
    allergies = st.text_input("Food Allergies / Dislikes (Optional)", placeholder="e.g., Peanuts, Dairy, Gluten, None")
    medical_notes = st.text_input("Injuries or Medical Notes (Optional)", placeholder="e.g., Lower back pain, None")

# Action Button
st.markdown("---")
generate_btn = st.button("🚀 Generate My Personalized FitBuddy Plan Now")

# Scientific Calculations Engine
height_m = height_cm / 100.0
bmi = current_weight / (height_m ** 2)

if bmi < 18.5:
    bmi_cat = "Underweight"
elif bmi < 24.9:
    bmi_cat = "Healthy / Normal Weight"
elif bmi < 29.9:
    bmi_cat = "Overweight"
else:
    bmi_cat = "Obese"

# BMR (Mifflin-St Jeor) & TDEE calculation
if gender == "Male":
    bmr = 10 * current_weight + 6.25 * height_cm - 5 * age + 5
else:
    bmr = 10 * current_weight + 6.25 * height_cm - 5 * age - 161

activity_multipliers = {
    "Sedentary (Little/No exercise, desk job)": 1.2,
    "Lightly Active (1-3 workout days/week)": 1.375,
    "Moderately Active (3-5 workout days/week)": 1.55,
    "Very Active (6-7 workout days/week)": 1.725
}
tdee = bmr * activity_multipliers.get(activity_level, 1.375)

# Target calories according to goal
if "Loss" in goal:
    target_calories = int(tdee - 500)
    protein_grams = int(current_weight * 2.0)
    fat_grams = int((target_calories * 0.25) / 9)
    carb_grams = int((target_calories - (protein_grams * 4) - (fat_grams * 9)) / 4)
elif "Building" in goal:
    target_calories = int(tdee + 350)
    protein_grams = int(current_weight * 2.2)
    fat_grams = int((target_calories * 0.25) / 9)
    carb_grams = int((target_calories - (protein_grams * 4) - (fat_grams * 9)) / 4)
else:
    target_calories = int(tdee)
    protein_grams = int(current_weight * 1.8)
    fat_grams = int((target_calories * 0.25) / 9)
    carb_grams = int((target_calories - (protein_grams * 4) - (fat_grams * 9)) / 4)

water_target = round(current_weight * 0.04, 1)

# Plan Generator Function
def generate_automated_fitness_plan():
    if "Gym" in workout_location:
        d1 = "**Day 1: Chest & Triceps (Push Day)**\n- Barbell Bench Press: 4 sets x 8-10 reps (Rest: 90s)\n- Incline Dumbbell Press: 3 sets x 10-12 reps\n- Cable Chest Flyes: 3 sets x 15 reps\n- Tricep Rope Pushdowns: 4 sets x 12 reps\n- Overhead Tricep Extension: 3 sets x 12 reps"
        d2 = "**Day 2: Back & Biceps (Pull Day)**\n- Lat Pulldowns / Pull-ups: 4 sets x 8-10 reps (Rest: 90s)\n- Seated Cable Rows: 4 sets x 10-12 reps\n- Dumbbell Single-Arm Rows: 3 sets x 10 reps\n- Barbell Bicep Curls: 4 sets x 10-12 reps\n- Hammer Curls: 3 sets x 12 reps"
        d3 = "**Day 3: Legs & Core Power**\n- Barbell Squats / Leg Press: 4 sets x 8-10 reps (Rest: 120s)\n- Romanian Deadlifts: 3 sets x 10-12 reps\n- Walking Lunges: 3 sets x 12 reps/leg\n- Standing Calf Raises: 4 sets x 15 reps\n- Hanging Leg Raises & Planks: 3 sets x 15 reps"
        d4 = "**Day 4: Active Recovery / Light Cardio**\n- 30 mins brisk walking or cycling + 15 mins mobility stretching"
        d5 = "**Day 5: Shoulders & Upper Sculpt**\n- Overhead Dumbbell Shoulder Press: 4 sets x 8-10 reps\n- Lateral Dumbbell Raises: 4 sets x 15 reps\n- Face Pulls: 3 sets x 15 reps\n- Dips: 3 sets to failure"
        d6 = "**Day 6: Lower Body Power & Core**\n- Bulgarian Split Squats: 3 sets x 10 reps/leg\n- Leg Curls & Extensions: 3 sets x 12 reps\n- Russian Twists: 3 sets x 25 reps"
        d7 = "**Day 7: Complete Rest & Muscle Recovery**\n- Light walking, foam rolling, and hydration focus"
    elif "Dumbbells" in workout_location:
        d1 = "**Day 1: Upper Body Push (Chest/Shoulders/Triceps)**\n- Dumbbell Floor Press: 4 sets x 10-12 reps\n- Incline Dumbbell Press: 3 sets x 12 reps\n- Dumbbell Lateral Raises: 4 sets x 15 reps\n- Overhead Dumbbell Tricep Extension: 3 sets x 12 reps"
        d2 = "**Day 2: Upper Body Pull (Back/Biceps)**\n- Dumbbell Bent-Over Rows: 4 sets x 10-12 reps\n- Single-Arm Dumbbell Rows: 3 sets x 12 reps\n- Dumbbell Bicep Curls: 4 sets x 12 reps\n- Hammer Curls: 3 sets x 12 reps"
        d3 = "**Day 3: Lower Body & Core**\n- Goblet Squats with Dumbbell: 4 sets x 12-15 reps\n- Dumbbell Romanian Deadlifts: 4 sets x 12 reps\n- Dumbbell Walking Lunges: 3 sets x 10 reps/leg\n- Dumbbell Calf Raises: 4 sets x 20 reps"
        d4 = "**Day 4: Active Recovery & Mobility**\n- 20 mins light mobility stretches + brisk walking"
        d5 = "**Day 5: Full Body Dumbbell Circuit**\n- Dumbbell Thrusters (Squat to Press): 3 sets x 10 reps\n- Renegade Rows: 3 sets x 10 reps\n- Dumbbell Romanian Deadlift to Shrug: 3 sets x 12 reps\n- Plank Hold: 3 sets x 60 seconds"
        d6 = "**Day 6: HIIT & Core Ignition**\n- Mountain Climbers: 4 sets x 30s\n- Dumbbell Shadow Boxing: 3 sets x 40s\n- Bicycle Crunches: 4 sets x 20 reps"
        d7 = "**Day 7: Full Rest & Recovery**"
    else:
        d1 = "**Day 1: Bodyweight Upper Body Push**\n- Push-ups (Standard / Incline): 4 sets x 12-15 reps\n- Diamond Push-ups: 3 sets x 10-12 reps\n- Pike Push-ups: 3 sets x 10 reps\n- Chair Dips: 3 sets x 15 reps"
        d2 = "**Day 2: Bodyweight Lower Body Power**\n- Bodyweight Squats: 4 sets x 20 reps\n- Reverse Lunges: 3 sets x 12 reps/leg\n- Glute Bridges: 4 sets x 20 reps\n- Single-leg Calf Raises: 4 sets x 15 reps/leg"
        d3 = "**Day 3: Core & Cardio Conditioning**\n- High Knees: 4 sets x 30s\n- Plank to Downward Dog: 3 sets x 12 reps\n- Russian Twists: 4 sets x 25 reps"
        d4 = "**Day 4: Active Recovery & Flexibility**\n- Full body mobility & yoga flow (25 mins)"
        d5 = "**Day 5: Full Body Calisthenics Circuit**\n- Burpees: 3 sets x 10 reps\n- Jump Squats: 3 sets x 15 reps\n- Decline Push-ups: 3 sets x 12 reps\n- Plank: 3 sets x 60s"
        d6 = "**Day 6: Lower Body Endurance & Core**\n- Wall Sit: 3 sets x 45s\n- Step-ups: 3 sets x 12 reps/leg\n- Leg Raises: 4 sets x 15 reps"
        d7 = "**Day 7: Rest & Relaxation**"

    if diet_type == "Vegetarian":
        m_breakfast = "🥣 **Breakfast:** Rolled oats with almond milk, chia seeds, almonds & sliced banana (approx. 450 kcal | 22g protein)"
        m_lunch = "🍛 **Lunch:** Brown Rice / Whole-wheat rotis with 150g Paneer curry, 1 bowl Spinach Dal & cucumber salad (approx. 650 kcal | 35g protein)"
        m_snack = "🥜 **Evening Snack:** Roasted chickpeas (Chana) with green tea & pumpkin seeds (approx. 200 kcal | 15g protein)"
        m_dinner = "🥗 **Dinner:** Grilled Paneer or Soya chunks with sautéed broccoli, bell peppers & quinoa (approx. 500 kcal | 35g protein)"
    elif diet_type == "Vegan":
        m_breakfast = "🥣 **Breakfast:** Tofu Scramble with whole-wheat toast, spinach & avocado (approx. 420 kcal | 24g protein)"
        m_lunch = "🍛 **Lunch:** Quinoa bowl with spiced chickpeas, edamame & tahini dressing (approx. 600 kcal | 28g protein)"
        m_snack = "🥜 **Evening Snack:** Mixed nuts (walnuts, almonds) & chia seed pudding (approx. 220 kcal | 12g protein)"
        m_dinner = "🥗 **Dinner:** Red Lentil (Masoor) curry with steamed vegetables and brown rice (approx. 480 kcal | 26g protein)"
    elif diet_type == "Keto / Low-Carb":
        m_breakfast = "🍳 **Breakfast:** 3 Whole eggs scrambled with spinach, butter & avocado (approx. 480 kcal | 22g protein | 4g carbs)"
        m_lunch = "🥗 **Lunch:** Grilled Chicken Breast / Paneer with caesar salad, olive oil & cheese (approx. 620 kcal | 45g protein | 5g carbs)"
        m_snack = "🥜 **Evening Snack:** Handful of almonds & string cheese (approx. 210 kcal | 10g protein | 3g carbs)"
        m_dinner = "🍲 **Dinner:** Baked salmon / Grilled Paneer with asparagus and cauliflower mash (approx. 550 kcal | 38g protein | 5g carbs)"
    else:
        m_breakfast = "🍳 **Breakfast:** 3 Scrambled Eggs with whole-grain toast & 1 apple (approx. 450 kcal | 28g protein)"
        m_lunch = "🍗 **Lunch:** 150g Grilled Chicken Breast with Brown Rice, Green Beans & Olive Oil (approx. 600 kcal | 45g protein)"
        m_snack = "🥤 **Evening Snack:** Protein shake or boiled eggs with almonds (approx. 220 kcal | 25g protein)"
        m_dinner = "🐟 **Dinner:** Grilled Fish / Chicken with roasted sweet potatoes & leafy salad (approx. 500 kcal | 40g protein)"

    plan_md = f"""
## 📊 1. Personal Assessment & Calorie Breakdown

| Metric | Scientific Value | Notes |
| :--- | :--- | :--- |
| **Current BMI** | **{bmi:.1f} kg/m²** | {bmi_cat} |
| **Basal Metabolic Rate (BMR)** | **{int(bmr)} kcal/day** | Calories burned at rest |
| **Maintenance TDEE** | **{int(tdee)} kcal/day** | Daily energy expenditure |
| **🎯 Daily Target Intake** | **{target_calories} kcal/day** | Goal: *{goal}* |
| **🥩 Daily Protein Goal** | **{protein_grams} grams** | Muscle recovery |
| **🥑 Daily Healthy Fats** | **{fat_grams} grams** | Hormone balance |
| **🍚 Daily Carbohydrates** | **{carb_grams} grams** | Workout energy |

---

## 🏋️‍♂️ 2. Your 7-Day Workout Routine ({workout_location})

{d1}

{d2}

{d3}

{d4}

{d5}

{d6}

{d7}

---

## 🥗 3. Customized Daily Meal Plan ({diet_type})

{m_breakfast}

{m_lunch}

{m_snack}

{m_dinner}

---

## 💧 4. Recovery, Sleep & Lifestyle Rules
1. **Hydration Target:** Drink at least **{water_target} Liters of water** daily.
2. **Sleep:** Aim for **7.5 to 8.5 hours of quality sleep** every night.
3. **Warm-up:** Spend 5 mins doing arm circles and light stretches before each session.
4. **Injuries / Medical:** *{f"Modify exercises to avoid pain: {medical_notes}" if medical_notes else "Maintain strict form over heavy weight."}*
"""
    return plan_md

# Button Click Event
if generate_btn:
    with st.spinner("🤖 FitBuddy AI is analyzing your metrics and designing your custom routine..."):
        time.sleep(0.8)
        plan_content = generate_automated_fitness_plan()
        
        st.success("🎉 Your personalized FitBuddy Plan is ready!")
        
        # Metric Highlight Cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current BMI", f"{bmi:.1f}", bmi_cat)
        m2.metric("Daily Calorie Target", f"{target_calories} kcal", f"{'+' if 'Building' in goal else '-' if 'Loss' in goal else ''}{abs(target_calories - int(tdee))} kcal")
        m3.metric("Protein Target", f"{protein_grams}g / day", "Muscle Support")
        m4.metric("Water Target", f"{water_target} L / day", "Hydration")
        
        st.markdown("---")
        
        # Interactive Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🏋️ 7-Day Workout", "🥗 Custom Meal Plan", "📊 Macro & Calorie Targets", "💡 Recovery & Tips"])
        
        with tab1:
            st.markdown(f"### 🏋️ 7-Day Routine — {workout_location}")
            st.markdown(plan_content.split("## 🏋️‍♂️ 2. Your 7-Day Workout Routine")[1].split("## 🥗 3. Customized Daily Meal Plan")[0])
            
        with tab2:
            st.markdown(f"### 🥗 Day-by-Day Nutrition Guide ({diet_type})")
            st.markdown(plan_content.split("## 🥗 3. Customized Daily Meal Plan")[1].split("## 💧 4. Recovery, Sleep & Lifestyle Rules")[0])
            
        with tab3:
            st.markdown("### 📊 Scientific Health & Caloric Profile")
            st.markdown(plan_content.split("## 📊 1. Personal Assessment & Calorie Breakdown")[1].split("## 🏋️‍♂️ 2. Your 7-Day Workout Routine")[0])
            
        with tab4:
            st.markdown("### 💧 Recovery, Hydration & Wellness Protocol")
            st.markdown(plan_content.split("## 💧 4. Recovery, Sleep & Lifestyle Rules")[1])
            
        # Download Button
        st.markdown("---")
        st.download_button(
            label="📥 Download Full FitBuddy Plan (.md file)",
            data=plan_content,
            file_name=f"FitBuddy_{goal.replace(' ', '_')}_Plan.md",
            mime="text/markdown"
        )
