
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

# Session state initialization
if 'bmr' not in st.session_state:
    st.session_state.bmr = 0
if 'tdee' not in st.session_state:
    st.session_state.tdee = 0
if 'goals' not in st.session_state:
    st.session_state.goals = (None, None)

# Streamlit app Layout
# 1. BMR title and desc
st.title('Basal Metabolic Rate (BMR) Calculator')
st.markdown("Enter your details below to estimate the number of calories your body burns at rest.")

# 2. col layout for BMR user input
col1, col2 = st.columns(2)
with col1:
    age = st.number_input('Age (years)', min_value=1, max_value=120, value=30)
    height = st.number_input('Height (cm)', min_value=100, max_value=250, value=170)
with col2:
    gender = st.radio('Gender', ['Male', 'Female'])
    weight = st.number_input('Weight (kg)', min_value=30.0, max_value=250.0, value=70.0)

# 3. button to trigger BMR calc
if st.button('Calculate BMR'):
    st.session_state.bmr = calculate_bmr(age, gender, height, weight)
    st.success("BMR calculation complete!")

# 4. display BMR result
if st.session_state.bmr > 0:
    st.subheader('Your Calculated BMR')
    st.metric("Basal Metabolic Rate (BMR)", f"{st.session_state.bmr:,.0f} kcal")

    st.markdown("---") # separator ---------------------------------------------

    # 1. TDEE title and desc (visible after BMR is calculated)
    st.title('Total Daily Energy Expenditure (TDEE) Calculator')
    st.markdown("Select your activity level below to factor in total calories burned.")

    # 2. radio button layout for activity level user input
    activity_level = st.radio('Activity Level', list(ACTIVITY_FACTORS.keys()))

    # 3. button to trigger TDEE calc
    if st.button('Calculate TDEE'):
        st.session_state.tdee = calculate_tdee(st.session_state.bmr, activity_level)
        st.success("TDEE calculation complete!")

    # 4. display TDEE result
    if st.session_state.tdee > 0:
        st.subheader('Your Calculated TDEE')
        st.metric("Total Daily Energy Expenditure (TDEE)", f"{st.session_state.tdee:,.0f} kcal")

        st.markdown("---") # separator ---------------------------------------------

        # 1. Goals title and desc (visible after TDEE is calculated)
        st.title('Fitness Goals Calculator')
        st.markdown('Select your fitness goal below to determine your daily calorie intake and macro ratio.')

        # 2. radio button layout for fitness goal user input
        goals_key = st.radio('Fitness Goal', list(GOAL_FACTORS.keys()))

        # 3. button to trigger Goals calc
        if st.button('Calculate Goals'):
            st.session_state.goals = determine_goals(st.session_state.tdee, goals_key)
            st.success("Goals calculation complete!")

            # 4. display goals result
            if st.session_state.goals[0] is not None:
              st.subheader('Your Calculated Daily Calorie Intake and Macro Goals')

              calorie_goal, macro_ratio = st.session_state.goals
              st.metric("Daily Calorie Intake", f"{calorie_goal:,.0f} kcal")
              st.metric("Daily Macro Ratio (P:C:F)",
                        f"{int(macro_ratio[0]*100)}% Protein, {int(macro_ratio[1]*100)}% Carbohydrates, {int(macro_ratio[2]*100)}% Fat"
                        )