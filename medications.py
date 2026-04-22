import streamlit as st
import database, pandas as pd, matplotlib.pyplot as plt, numpy as np
from datetime import datetime, timedelta

FREQUENCY_SLOTS = {
    "Once Daily - Morning": ["Morning"],
    "Once Daily - Afternoon": ["Afternoon"],
    "Once Daily - Night": ["Night"],
    "Twice Daily - Morning + Afternoon": ["Morning", "Afternoon"],
    "Twice Daily - Morning + Night": ["Morning", "Night"],
    "Twice Daily - Afternoon + Night": ["Afternoon", "Night"],
    "Thrice Daily - Morning + Afternoon + Night": ["Morning", "Afternoon", "Night"],
    "As Needed": []
}

def get_slots(freq_str):
    if not freq_str: return []
    # Dynamic detection based on keywords
    slots = []
    if "Morning" in freq_str: slots.append("Morning")
    if "Afternoon" in freq_str: slots.append("Afternoon")
    if "Night" in freq_str: slots.append("Night")
    
    # Fallback for simple names (compatibility)
    if not slots:
        if "Thrice" in freq_str or "3 Times" in freq_str: return ["Morning", "Afternoon", "Night"]
        if "Twice" in freq_str or "2 Times" in freq_str: return ["Morning", "Night"]
        if "Once" in freq_str or "1 Time" in freq_str: return ["Morning"]
    return slots

def show_medications():
    st.title("Medication Manager")
    
    today = datetime.now().strftime("%Y-%m-%d")
    meds = database.get_medications()
    logs = database.get_logs(today)
    
    st.write("### Today's Medication Checklist")
    for m in meds:
        # m is now a dict
        if m['start_date'] <= today <= m['end_date']:
            slots = get_slots(m['frequency'])
            with st.container():
                st.markdown(f"""
                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 10px;'>
                    <span style='font-size: 1.2rem;'>💊 <b>{m['name']}</b> — {m['dosage']}</span><br>
                    <span style='color: #6c757d; font-size: 0.9rem;'>Schedule: {m['frequency']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if slots:
                    cols = st.columns(len(slots))
                    for i, slot in enumerate(slots):
                        status = logs.get((m['id'], slot), "Pending")
                        checked = (status == "Taken")
                        if cols[i].checkbox(f"{slot}", value=checked, key=f"chk_{m['id']}_{slot}"):
                            if not checked:
                                database.log_medication(m['id'], today, "Taken", slot)
                                st.rerun()
                        else:
                            if checked:
                                database.log_medication(m['id'], today, "Pending", slot)
                                st.rerun()
                else:
                    st.write("*Taken as needed (SOS)*")
    
    st.divider()

    if meds:
        st.write("### Weekly Progress Chart")
        dates = [(datetime.now() - timedelta(days=i)).strftime("%m/%d") for i in range(6, -1, -1)]
        full_dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        taken_counts, missed_counts = [], []
        
        for d in full_dates:
            d_logs = database.get_logs(d)
            t, m = 0, 0
            for med in meds:
                if med['start_date'] <= d <= med['end_date']:
                    for s in get_slots(med['frequency']):
                        if d_logs.get((med['id'], s)) == "Taken": t += 1
                        else: m += 1
            taken_counts.append(t); missed_counts.append(m)
            
        fig, ax = plt.subplots(figsize=(10, 4))
        x = np.arange(len(dates))
        width = 0.35
        ax.bar(x - width/2, taken_counts, width, label='Taken', color='#2ecc71')
        ax.bar(x + width/2, missed_counts, width, label='Missed', color='#e74c3c')
        ax.set_xticks(x); ax.set_xticklabels(dates)
        plt.title("Dose Compliance — Last 7 Days"); plt.legend(); st.pyplot(fig)

        st.write("### Monthly Compliance Report")
        report_data = []
        month_dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
        for med in meds:
            for s in get_slots(med['frequency']):
                t, m = 0, 0
                for d in month_dates:
                    if med['start_date'] <= d <= med['end_date']:
                        d_logs = database.get_logs(d)
                        if d_logs.get((med['id'], s)) == "Taken": t += 1
                        else: m += 1
                total = t + m
                if total > 0:
                    perc = round((t/total)*100)
                    report_data.append({"Medicine": f"{med['name']} ({s})", "Taken": t, "Missed": m, "Total": total, "Compliance %": perc})
        
        if report_data:
            st.table(pd.DataFrame(report_data))

    st.divider()
    with st.expander("➕ Add New Medication"):
        n = st.text_input("Medicine Name")
        d = st.text_input("Dosage (e.g. 500mg, 1 tablet)")
        f = st.selectbox("Frequency & Timing", list(FREQUENCY_SLOTS.keys()))
        col1, col2 = st.columns(2)
        s_date = col1.date_input("Start Date", value=datetime.now())
        e_date = col2.date_input("End Date", value=datetime.now() + timedelta(days=30))
        if st.button("Save Medication"):
            database.add_medication(n, d, f, s_date.strftime("%Y-%m-%d"), e_date.strftime("%Y-%m-%d"))
            st.success("Saved!"); st.rerun()

    with st.expander("🗑️ Delete Medication"):
        if meds:
            m_to_del = st.selectbox("Select medication to delete", [f"{m['name']} ({m['dosage']})" for m in meds])
            if st.button("Delete", type="primary"):
                idx = [f"{m['name']} ({m['dosage']})" for m in meds].index(m_to_del)
                database.delete_medication(meds[idx]['id'])
                st.success("Deleted!"); st.rerun()
