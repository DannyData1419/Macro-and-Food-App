
import streamlit as st

# v2 inc. Cals/Macro ratios
# v1 inc. TDEE calc
# v0 BMR calc

# set title
st.set_page_config(
    page_title='BMR & TDEE Calculator',
    layout="centered" )

# activity factors dictionary
ACTIVITY_FACTORS = {
    "Sedentary (little or no exercise)": 1.2,
    "Lightly Active (light exercise/sports 1-3 days/week)": 1.375,
    "Moderately Active (moderate exercise/sports 3-5 days/week)": 1.55,
    "Very Active (hard exercise/sports 6-7 days a week)": 1.725,
    "Extremely Active (very hard exercise/physical job)": 1.9 }

# goal factors calorie/macro dictioary
GOAL_FACTORS = {
    "Cutting (keep muscle and lose fat)": {
        "calorie_goal": 0.85,  # 1 - 0.15
        "macro_goal": (0.4, 0.3, 0.3) }, # protein, carbs, fat

    "Maintenance": {
        "calorie_goal": 1.0,
        "macro_goal": (0.25, 0.45, 0.3)},

    "Increase size (muscle gain)": {
        "calorie_goal": 1.15,  # 1 + 0.15
        "macro_goal": (0.3, 0.5, 0.2)} }


# BMR function
def calculate_bmr(age, gender, height, weight):
    """
    Calculates the Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation
    """
    if gender == "Female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:  # Male
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    return bmr

# TDEE function
def calculate_tdee(bmr, activity_level_str):
    """
    Calculates the Total Daily Energy Expenditure (TDEE) based on BMR and activity level
    """
    # get activity factor from dictionary
    activity_factor = ACTIVITY_FACTORS.get(activity_level_str)
    if activity_factor:
        tdee = bmr * activity_factor
        return tdee
    else:
        st.error("Invalid activity level selected.")
        return 0

# Goals function
def determine_goals(tdee, goals_key):
    """
    Determines user's daily calorie intake and macro ratio based on their fitness goal
    """
    # get goals from dictionary
    cals_and_macro_goals = GOAL_FACTORS.get(goals_key)
    if cals_and_macro_goals:
        calorie_intake = tdee * cals_and_macro_goals["calorie_goal"]
        macro_ratio = cals_and_macro_goals["macro_goal"]
        return calorie_intake, macro_ratio
    else:
        st.error("Invalid goals selected.")
        return None, None

def calculate_macro_grams(calorie_intake, macro_ratio):
    """Converts each macro's calorie allocation into grams."""
    protein_ratio, carbohydrate_ratio, fat_ratio = macro_ratio
    return (
        calorie_intake * protein_ratio / 4,
        calorie_intake * carbohydrate_ratio / 4,
        calorie_intake * fat_ratio / 9,
    )

# Session state initialization
if 'bmr' not in st.session_state:
    st.session_state.bmr = 0
if 'tdee' not in st.session_state:
    st.session_state.tdee = 0
if 'goals' not in st.session_state:
    st.session_state.goals = (None, None)

# Input controls and calculation buttons
with st.sidebar:
    st.header('Your Inputs')
    st.subheader('Personal Details')
    age = st.number_input('Age (years)', min_value=1, max_value=120, value=30)
    gender = st.radio('Gender', ['Male', 'Female'])
    height = st.number_input('Height (cm)', min_value=100, max_value=250, value=170)
    weight = st.number_input('Weight (kg)', min_value=30.0, max_value=250.0, value=70.0)

    if st.button('Calculate BMR', use_container_width=True):
        st.session_state.bmr = calculate_bmr(age, gender, height, weight)
        st.session_state.tdee = 0
        st.session_state.goals = (None, None)

    st.subheader('Activity')
    activity_level = st.selectbox('Activity Level', list(ACTIVITY_FACTORS.keys()))
    if st.button('Calculate TDEE', disabled=st.session_state.bmr <= 0, use_container_width=True):
        st.session_state.tdee = calculate_tdee(st.session_state.bmr, activity_level)
        st.session_state.goals = (None, None)

    st.subheader('Fitness Goal')
    goals_key = st.selectbox('Goal', list(GOAL_FACTORS.keys()))
    if st.button('Calculate Goals', disabled=st.session_state.tdee <= 0, use_container_width=True):
        st.session_state.goals = determine_goals(st.session_state.tdee, goals_key)

# Results remain on the main page across Streamlit reruns.
st.title('BMR & TDEE Calculator')
st.markdown('Calculate your daily energy needs and macro targets.')

if st.session_state.bmr > 0:
    st.subheader('Basal Metabolic Rate (BMR)')
    st.metric('BMR', f"{st.session_state.bmr:,.0f} kcal")

if st.session_state.tdee > 0:
    st.subheader('Total Daily Energy Expenditure (TDEE)')
    st.metric('TDEE', f"{st.session_state.tdee:,.0f} kcal")

if st.session_state.goals[0] is not None:
    calorie_goal, macro_ratio = st.session_state.goals
    st.subheader('Daily Calorie and Macro Goals')
    st.metric('Daily Calorie Intake', f'{calorie_goal:,.0f} kcal')
    st.metric(
        'Daily Macro Ratio (P:C:F)',
        f'{int(macro_ratio[0] * 100)}% Protein, {int(macro_ratio[1] * 100)}% Carbohydrates, {int(macro_ratio[2] * 100)}% Fat',
    )

    protein_grams, carbohydrate_grams, fat_grams = calculate_macro_grams(calorie_goal, macro_ratio)
    st.subheader('Daily Macronutrients')
    macro_col1, macro_col2, macro_col3 = st.columns(3)
    macro_col1.metric('Protein', f'{protein_grams:,.0f} g')
    macro_col2.metric('Carbohydrates', f'{carbohydrate_grams:,.0f} g')
    macro_col3.metric('Fat', f'{fat_grams:,.0f} g')