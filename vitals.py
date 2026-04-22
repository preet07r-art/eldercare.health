import streamlit as st
import database, numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
import time, subprocess, sys
from datetime import datetime, timedelta

def safe_float(val, default=0.0):
    if val is None or str(val).lower() == 'none' or str(val).strip() == "":
        return float(default)
    try: return float(val)
    except: return float(default)

def trigger_auto_alert(reason):
    user = database.get_user()
    name = user.get('caretaker_name', 'Caretaker')
    subprocess.Popen([sys.executable, "warning_popup.py", reason])
    with st.status(f"AUTOMATIC RISK ALERT: {reason}", expanded=True) as status:
        st.write("Dangerous Levels Detected! Initializing Emergency Protocol...")
        time.sleep(1.5)
        st.write(f"Connecting to Caretaker Gateway for {name}...")
        time.sleep(1.5)
        st.write("Sending SMS & Email Notification...")
        time.sleep(2)
        status.update(label="✅ Caretaker Notified of Health Risk!", state="complete", expanded=False)
    st.toast(f"Risk Alert Sent: {reason}", icon="⚠️")

def show_vitals():
    st.title("Vital Signs Logger")
    user = database.get_user()
    
    h, w = safe_float(user.get('height')), safe_float(user.get('weight'))
    if h > 0 and w > 0:
        bmi = round(w / np.square(h / 100), 2)
        st.info(f"Your calculated BMI is {bmi}. Keep it up!")
    else:
        st.info("Update height & weight in User Profile to see BMI.")

    st.write("---")

    goals = database.get_vitals_goals()
    with st.expander("Set My Vitals Goals"):
        c1, c2, c3, c4 = st.columns(4)
        s_min = c1.number_input("Min Systolic", value=int(safe_float(goals.get('sys_min'), 90)))
        s_max = c2.number_input("Max Systolic", value=int(safe_float(goals.get('sys_max'), 120)))
        d_min = c3.number_input("Min Diastolic", value=int(safe_float(goals.get('dia_min'), 60)))
        d_max = c4.number_input("Max Diastolic", value=int(safe_float(goals.get('dia_max'), 80)))
        
        c1b, c2b, c3b, c4b = st.columns(4)
        su_min = c1b.number_input("Min Sugar", value=int(safe_float(goals.get('sug_min'), 70)))
        su_max = c2b.number_input("Max Sugar", value=int(safe_float(goals.get('sug_max'), 140)))
        hr_min = c3b.number_input("Min HR", value=int(safe_float(goals.get('hr_min'), 60)))
        hr_max = c4b.number_input("Max HR", value=int(safe_float(goals.get('hr_max'), 100)))
        
        c1c, c2c = st.columns(2)
        w_min = c1c.number_input("Min Weight", value=safe_float(goals.get('w_min'), 50.0))
        w_max = c2c.number_input("Max Weight", value=safe_float(goals.get('w_max', 90.0)))
        
        if st.button("Save Goals"):
            database.update_vitals_goals(sys_min=s_min, sys_max=s_max, dia_min=d_min, dia_max=d_max, 
                                        sug_min=su_min, sug_max=su_max, hr_min=hr_min, hr_max=hr_max,
                                        w_min=w_min, w_max=w_max)
            st.success("Goals updated!")

    with st.expander("Log New Reading"):
        cl1, cl2 = st.columns(2)
        sys_val = cl1.number_input("Systolic BP", 0, 300, 120)
        dia_val = cl2.number_input("Diastolic BP", 0, 200, 80)
        hr_val = cl1.number_input("Heart Rate", 0, 250, 72)
        weight_val = cl2.number_input("Weight (kg)", 0.0, 500.0, float(w))
        sugar_b = cl1.number_input("Blood Sugar Before Meal", 0.0, 500.0, 0.0)
        sugar_a = cl2.number_input("Blood Sugar After Meal", 0.0, 500.0, 0.0)
        
        if st.button("Save Entry"):
            database.add_vitals(sys_val, dia_val, hr_val, weight_val, sugar_b, sugar_a)
            st.success("Reading logged!")
            if sys_val > 160 or sys_val < 85: trigger_auto_alert(f"Critical BP: {sys_val}/{dia_val}")
            elif hr_val > 120 or hr_val < 50: trigger_auto_alert(f"Critical Heart Rate: {hr_val} bpm")
            elif sugar_b > 250 or sugar_b < 60: trigger_auto_alert(f"Critical Blood Sugar: {sugar_b} mg/dL")
            st.rerun()

    v_data = database.get_vitals()
    if v_data:
        st.write("---")
        latest = v_data[0]
        st.write("### Latest Readings vs Goal Ranges")
        
        fig, ax = plt.subplots(figsize=(10, 4))
        metrics = ["Systolic", "Diastolic", "Heart Rate"]
        vals = [latest.get('bp_systolic'), latest.get('bp_diastolic'), latest.get('heart_rate')]
        
        # Safe math for goals
        mins = [safe_float(goals.get('sys_min'), 90), safe_float(goals.get('dia_min'), 60), safe_float(goals.get('hr_min'), 60)]
        maxs = [safe_float(goals.get('sys_max'), 120), safe_float(goals.get('dia_max'), 80), safe_float(goals.get('hr_max'), 100)]
        colors = ["#3498db", "#2ecc71", "#e67e22"]
        
        for i, (m, v, mi, ma, c) in enumerate(zip(metrics, vals, mins, maxs, colors)):
            ax.barh(m, ma-mi, left=mi, color=c, alpha=0.2)
            ax.barh(m, 1, left=safe_float(v)-0.5, color=c, height=0.6)
            ax.text(safe_float(v) + 0.5, i, str(v), color=c, fontweight='bold', va='center')
        st.pyplot(fig)

        st.write("### Heart Rate Trend")
        df = pd.DataFrame(v_data)
        df['dt'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df_top = df.head(15)
        
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=df_top, x='dt', y='heart_rate', marker='o', color='orange')
        ax2.axhline(safe_float(goals.get('hr_min'), 60), color='green', linestyle='--', alpha=0.5, label="Min Goal")
        ax2.axhline(safe_float(goals.get('hr_max'), 100), color='red', linestyle='--', alpha=0.5, label="Max Goal")
        plt.xticks(rotation=45); plt.legend(); st.pyplot(fig2)

        st.write("### Blood Sugar Trend")
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=df_top, x='dt', y='blood_sugar_before_meal', marker='o', label="Before Meal", color='blue')
        sns.lineplot(data=df_top, x='dt', y='blood_sugar_after_meal', marker='o', label="After Meal", color='purple')
        ax3.axhline(safe_float(goals.get('sug_min'), 70), color='green', linestyle='--', alpha=0.5, label="Min Goal")
        ax3.axhline(safe_float(goals.get('sug_max'), 140), color='red', linestyle='--', alpha=0.5, label="Max Goal")
        plt.xticks(rotation=45); plt.legend(); st.pyplot(fig3)

        st.write("### Monthly Statistics (NumPy)")
        df['date_only'] = pd.to_datetime(df['date'])
        df_month = df[df['date_only'] > (datetime.now() - timedelta(days=30))]
        if not df_month.empty:
            cols = st.columns(3)
            stat_map = [
                ("Systolic", "bp_systolic"), ("Diastolic", "bp_diastolic"), 
                ("Heart Rate", "heart_rate"), ("Weight", "weight"),
                ("Sugar (Before)", "blood_sugar_before_meal"), ("Sugar (After)", "blood_sugar_after_meal")
            ]
            for i, (label, col_name) in enumerate(stat_map):
                arr = pd.to_numeric(df_month[col_name], errors='coerce').values
                c_idx = i % 3
                with cols[c_idx]:
                    st.write(f"**{label} Avg**")
                    avg_val = np.nanmean(arr) if not np.all(np.isnan(arr)) else 0.0
                    st.write(f"{avg_val:.1f}")
                    min_val = np.nanmin(arr) if not np.all(np.isnan(arr)) else 0.0
                    max_val = np.nanmax(arr) if not np.all(np.isnan(arr)) else 0.0
                    st.caption(f"Min: {min_val} | Max: {max_val}")

        st.write("### Full History")
        st.dataframe(df.drop(columns=['dt', 'date_only']), use_container_width=True)
