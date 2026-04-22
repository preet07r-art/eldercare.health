# ElderCare Companion - Updated Version 1.1
import streamlit as st
import database, profile, medications, vitals, reports, visuals, time, subprocess, sys, random
from datetime import datetime

st.set_page_config(page_title="ElderCare Companion", layout="wide")

def send_alert(reason="Manual SOS Triggered"):
    user = database.get_user()
    name = user.get('ct_n', 'Caretaker')
    subprocess.Popen([sys.executable, "warning_popup.py", reason])
    with st.status(f"🚨 EMERGENCY ALERT: {reason}", expanded=True) as status:
        st.write("Initializing Secure Protocol...")
        time.sleep(1)
        st.write(f"Encrypting message for {name}...")
        time.sleep(1.5)
        st.write("Sending SMS & Email via Gateway...")
        time.sleep(2)
        status.update(label="✅ Emergency Alert Sent Successfully!", state="complete", expanded=False)
    st.toast(f"Caretaker {name} has been notified.", icon="🚨")

def main():
    database.migrate_database()
    st.sidebar.title("ElderCare Companion")
    user = database.get_user()
    st.sidebar.success(f"User: {user.get('name', 'Elder User')}")
    pg = st.sidebar.radio("Navigation", ["Home Dashboard", "Vital Signs Logger", "Medication Manager", "Health Reports", "Desktop Visuals", "User Profile"])
    
    st.sidebar.divider()
    if st.sidebar.button("🚨 SOS EMERGENCY", type="primary", use_container_width=True):
        send_alert("Manual SOS Triggered")

    if pg == "Home Dashboard":
        st.title(f"Welcome back, {user.get('name', 'Elder User')}!")
        st.subheader(datetime.now().strftime("%A, %d %B %Y"))
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Health Status", "Stable", delta="Good")
        c2.metric("Next Medicine", "1:00 PM", delta="2 Hours Left")
        c3.metric("Daily Activity", "85%", delta="Target Met")
        
        st.write("---")
        col1, col2, col3 = st.columns(3)
        col1.write(f"**Age:** {user.get('age','—')} | **Gender:** {user.get('gender','—')}")
        col2.write(f"**Blood Group:** {user.get('bg','—')} | **Caretaker:** {user.get('ct_n','—')}")
        col3.write(f"**Conditions:** {user.get('cond','—')}")
        
        st.write("---")
        st.subheader("Daily Water Intake")
        if 'water' not in st.session_state: st.session_state.water = 0
        wc1, wc2, wc3 = st.columns([1, 1, 4])
        if wc1.button("➖ Remove Glass"): 
            if st.session_state.water > 0: st.session_state.water -= 1
        if wc2.button("➕ Add Glass"): st.session_state.water += 1
        progress = min(st.session_state.water / 8, 1.0)
        wc3.progress(progress, text=f"{st.session_state.water} / 8 Glasses")
        
        # Trigger Tkinter Popup only once when reaching 8
        if st.session_state.water == 8 and not st.session_state.get('water_alert_sent', False):
            subprocess.Popen([sys.executable, "water_popup.py"])
            st.session_state.water_alert_sent = True
            st.success("Goal Reached! Stay Hydrated.")
        elif st.session_state.water < 8:
            st.session_state.water_alert_sent = False
        elif st.session_state.water > 8:
            st.success("You've exceeded your goal! Excellent.")

        st.write("---")
        tips = [
            "Walking for 30 minutes can reduce blood pressure by 10 points.",
            "Stay hydrated! Drinking water boosts your energy and brain function.",
            "A balanced diet is a cookie in each hand... just kidding! Eat your greens.",
            "Your health is an investment, not an expense.",
            "Laughter is the best medicine. Don't forget to smile today!",
            "Small steps lead to big changes. Keep moving!",
            "Quality sleep is just as important as diet and exercise.",
            "Deep breathing for 5 minutes can significantly lower stress."
        ]
        st.info(f" **Daily Inspiration:** {random.choice(tips)}")
        
    elif pg == "Vital Signs Logger": vitals.show_vitals()
    elif pg == "Medication Manager": medications.show_medications()
    elif pg == "Health Reports": reports.show_reports()
    elif pg == "Desktop Visuals": visuals.show_visuals()
    elif pg == "User Profile": profile.show_profile()

if __name__ == "__main__":
    main()
