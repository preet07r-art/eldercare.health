import streamlit as st
import database
from datetime import datetime

def safe_float(val, default=0.0):
    if val is None or str(val).lower() == 'none' or str(val).strip() == "":
        return float(default)
    try: return float(val)
    except: return float(default)

def show_profile():
    st.title("User Profile")
    user = database.get_user()
    
    with st.expander("Personal Information", expanded=True):
        n = st.text_input("Name", value=user.get('name',''))
        
        # Super-Flexible Birthdate logic
        dob_raw = user.get('date_of_birth')
        default_dob = datetime(1960, 1, 1)
        if dob_raw:
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    default_dob = datetime.strptime(dob_raw, fmt)
                    break
                except: continue
            
        dob = st.date_input("Birthdate", value=default_dob, min_value=datetime(1900, 1, 1), max_value=datetime.now())
        
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        st.info(f"Calculated Age: {age} years")
        
        gender_opts = ["Male","Female","Other"]
        curr_g = user.get('gender')
        g_idx = gender_opts.index(curr_g) if curr_g in gender_opts else 0
        g = st.selectbox("Gender", gender_opts, index=g_idx)
        
        h = st.number_input("Height (cm)", 0.0, 300.0, safe_float(user.get('height'), 170))
        w = st.number_input("Weight (kg)", 0.0, 500.0, safe_float(user.get('weight'), 70))
    
    with st.expander("Medical Information"):
        bg_opts = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
        curr_bg = user.get('blood_group','A+')
        bg_idx = bg_opts.index(curr_bg) if curr_bg in bg_opts else 0
        bg = st.selectbox("Blood Group", bg_opts, index=bg_idx)
        cond = st.text_area("Conditions", value=user.get('known_conditions',''))
        allg = st.text_area("Allergies", value=user.get('allergies',''))

    with st.expander("Caretaker Information"):
        ct_n = st.text_input("Caretaker Name", value=user.get('caretaker_name',''))
        ct_p = st.text_input("Phone Number", value=user.get('caretaker_phone',''))

    if st.button("Save All Changes", type="primary"):
        success = database.update_user_profile(
            name=n, gender=g, height=h, weight=w, blood_group=bg, 
            known_conditions=cond, allergies=allg, caretaker_name=ct_n, 
            caretaker_phone=ct_p, dob=dob.strftime("%Y-%m-%d"), age=age
        )
        if success:
            st.success(f"Profile Saved Successfully! Age: {age}")
            st.rerun()
        else:
            st.error("Error saving profile. Please check your database connection.")
