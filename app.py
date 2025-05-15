import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import json
import os

# ======= HISTORIE FUNKCE =======

HISTORY_FILE = "history.json"

def save_to_history(entry):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []

    entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

# ====== TRÉNINK A JÍDELNÍČEK FUNKCE ======

def generate_training_details(goal, level, day_index):
    details = {
        "Z2 běh / jízda": ("Z2 (70–80 % TFmax)", "Trénink aerobní vytrvalosti", "45–60 min"),
        "intervaly": ("Z4 (90 % TFmax)", "Rozvoj VO2max", "6× 4 min s pauzou"),
        "tempový trénink": ("Z3 (85 % TFmax)", "Zvýšení laktátového prahu", "30 min v tempu"),
        "dlouhý běh/jízda": ("Z2", "Rozvoj základní vytrvalosti", "1,5–2 h"),
        "kombinovaný trénink": ("Z3 + Z4", "Rozvoj tempové i anaerobní zdatnosti", "60–90 min"),
        "Z4": ("Z4", "Maximální aerobní výkon", "8× 3 min"),
        "Z2 / regenerační trénink": ("Z1–Z2", "Regenerace, podpora krevního oběhu", "30–45 min"),
        "Lehký běh nebo cyklo (Z1-Z2)": ("Z1", "Nízká zátěž pro spalování tuků", "30 min"),
        "krátký trénink": ("Z2", "Základní vytrvalostní trénink", "30 min"),
        "volno": ("-", "Odpočinek", "-")
    }
    keys = list(details.keys())
    return details.get(keys[day_index % len(keys)], ("Z2", "Vytrvalostní trénink", "45 min"))

def generate_training_plan(goal, level, training_days):
    plan = []
    base_days = ['Pondělí', 'Úterý', 'Středa', 'Čtvrtek', 'Pátek', 'Sobota', 'Neděle']
    workouts = {
        "začátečník": ["Z2 běh / jízda", "volno", "krátký trénink"],
        "pokročilý": ["intervaly", "Z2", "tempový trénink", "dlouhý běh/jízda"],
        "elite": ["intervaly", "Z4", "tempový trénink", "dlouhý běh/jízda", "kombinovaný trénink"]
    }
    used_days = 0
    for i, day in enumerate(base_days):
        if used_days < training_days:
            workout = workouts[level][used_days % len(workouts[level])] if goal != "Redukce hmotnosti" else "Lehký běh nebo cyklo (Z1-Z2)"
            plan.append((day, workout))
            used_days += 1
        else:
            plan.append((day, "Volno / Mobilita"))
    return plan

def generate_meal_plan(goal):
    if goal == "Zlepšit výkonnost":
        return {
            "Snídaně": "Ovesná kaše s ovocem a ořechy",
            "Oběd": "Kuřecí maso, rýže, zelenina",
            "Večeře": "Losos s bramborem a špenátem",
            "Svačina": "Banán + hrst mandlí"
        }, {"Bílkoviny": 120, "Sacharidy": 280, "Tuky": 60}
    elif goal == "Zlepšit kondici":
        return {
            "Snídaně": "Jogurt s granolou a ovocem",
            "Oběd": "Těstoviny se zeleninou a sýrem",
            "Večeře": "Vejce, chléb, zelenina",
            "Svačina": "Jablko + ořechy"
        }, {"Bílkoviny": 90, "Sacharidy": 220, "Tuky": 55}
    else:
        return {
            "Snídaně": "Smoothie s proteinem a ovocem",
            "Oběd": "Grilované kuře se zeleninovým salátem",
            "Večeře": "Zeleninová polévka s vejcem",
            "Svačina": "Tvaroh s lněným semínkem"
        }, {"Bílkoviny": 100, "Sacharidy": 150, "Tuky": 40}

def draw_nutrient_pie(nutrients):
    fig, ax = plt.subplots()
    ax.pie(nutrients.values(), labels=nutrients.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

# ====== UI STREAMLIT ======

st.title("AI Trenér pro Vytrvalostní Sportovce 🏃‍♂️🚴‍♀️")

with st.form("vstup"):
    goal = st.selectbox("Cíl tréninku", ["Zlepšit výkonnost", "Zlepšit kondici", "Redukce hmotnosti"])
    level = st.selectbox("Výkonnostní úroveň", ["začátečník", "pokročilý", "elite"])
    training_days = st.slider("Počet tréninkových dní v týdnu", 3, 7, 5)
    gender = st.selectbox("Pohlaví", ["Muž", "Žena"])
    age = st.number_input("Věk", 12, 90, 25)
    submit = st.form_submit_button("Vygeneruj plán")

if submit:
    training_plan = generate_training_plan(goal, level, training_days)
    meal_plan, nutrients = generate_meal_plan(goal)

    st.success("Plán byl úspěšně vygenerován!")
    save_to_history({
        "goal": goal,
        "level": level,
        "training_days": training_days,
        "gender": gender,
        "age": age,
        "training_plan": training_plan,
        "meal_plan": meal_plan,
        "nutrients": nutrients
    })

    st.header("🗓️ Týdenní plán (rozklikni den)")
    for i, (day, workout) in enumerate(training_plan):
        with st.expander(f"📅 {day}"):
            st.subheader("🏃‍♂️ Trénink")
            zone, purpose, duration = generate_training_details(goal, level, i)
            st.markdown(f"- **Typ tréninku:** {workout}")
            st.markdown(f"- **Intenzita:** {zone}")
            st.markdown(f"- **Účel:** {purpose}")
            st.markdown(f"- **Odhad trvání:** {duration}")

            st.subheader("🍽️ Jídelníček")
            for meal, food in meal_plan.items():
                st.markdown(f"**{meal}**: {food}")

    st.subheader("Graf rozložení živin (na den)")
    draw_nutrient_pie(nutrients)

# ====== HISTORIE ZOBRAZENÍ ======
st.markdown("---")
if st.checkbox("📚 Zobrazit historii plánů"):
    history = load_history()
    if not history:
        st.info("Historie je zatím prázdná.")
    else:
        for item in reversed(history[-5:]):
            with st.expander(f"{item['timestamp']} – {item['goal']} – {item['level']}"):
                st.markdown(f"**Pohlaví:** {item['gender']}, **Věk:** {item['age']}")
                for i, (day, workout) in enumerate(item["training_plan"]):
                    st.markdown(f"**{day}**: {workout}")
