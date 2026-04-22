import streamlit as st
import database, numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
from datetime import datetime, timedelta
from medications import get_slots

def show_reports():
    st.title("Health Analytics Dashboard")
    today = datetime.now().date()
    
    # 1. Compliance Logic
    meds = database.get_medications()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
    taken, expected = 0, 0
    for m in meds:
        if m['frequency'] == "As Needed": continue
        slots = get_slots(m['frequency'])
        for d in dates:
            if m['start_date'] <= d <= m['end_date']:
                expected += len(slots)
                logs = database.get_logs(d)
                for s in slots:
                    if logs.get((m['id'], s)) == "Taken": taken += 1
    
    score = round((taken/expected)*100, 1) if expected else 0
    st.metric("30-Day Compliance Score", f"{score}%")
    
    # 2. Vitals Charts
    v_data = database.get_vitals()
    if v_data:
        # v_data is already a list of dicts
        df = pd.DataFrame(v_data)
        df['date_dt'] = pd.to_datetime(df['date'])
        
        st.write("### Blood Pressure Trends")
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=df, x='date_dt', y='bp_systolic', label='Systolic', marker='o')
        sns.lineplot(data=df, x='date_dt', y='bp_diastolic', label='Diastolic', marker='o')
        plt.xticks(rotation=45); plt.legend(); st.pyplot(fig)
        
        st.write("### Blood Sugar Comparison (Before vs After Meal)")
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=df, x='date_dt', y='blood_sugar_before_meal', label='Before Meal', color='blue', marker='o')
        sns.lineplot(data=df, x='date_dt', y='blood_sugar_after_meal', label='After Meal', color='purple', marker='o')
        plt.xticks(rotation=45); plt.legend(); st.pyplot(fig3)

    st.write("---")
    st.write("### Weekly Water Consistency")
    # Simple list for beginners: 8 is the goal!
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    glasses = [6, 8, 5, 8, 7, 8, 8] 
    
    fig4, ax4 = plt.subplots(figsize=(10, 4))
    colors = ['#2ecc71' if g >= 8 else '#e74c3c' for g in glasses]
    plt.bar(days, glasses, color=colors)
    plt.axhline(8, color='blue', linestyle='--', label="Goal (8 Glasses)")
    plt.ylabel("Glasses of Water")
    plt.legend(); st.pyplot(fig4)
    
    # 3. Export
    if v_data:
        if st.button("Export Data to CSV"):
            df.to_csv("health_data_export.csv", index=False)
            st.success("Exported to health_data_export.csv")
