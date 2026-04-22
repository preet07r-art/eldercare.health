import streamlit as st
import database, subprocess, sys

def show_visuals():
    st.title("Visual Progress & Reminders")
    st.write("---")
    
    # Quick Stats using Pandas
    v_df = database.get_vitals()
    st.write("### Health Data Overview")
    c1, c2 = st.columns(2)
    c1.metric("Total Vitals Logs", len(v_df))
    if v_df:
        c2.metric("Latest Weight", f"{v_df[0].get('weight', '—')} kg")

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Launch Turtle Chart", use_container_width=True):
            subprocess.Popen([sys.executable, "progress_visual.py", "weekly", "1"])
        st.caption("Visualizes weekly medication compliance in a circular chart. See your consistency at a glance.")
    with col2:
        if st.button("Launch Turtle Grid", use_container_width=True):
            subprocess.Popen([sys.executable, "progress_visual.py", "monthly", "1"])
        st.caption("Displays a monthly calendar grid colored by daily adherence. Track long-term health habits easily.")
    with col3:
        if st.button("Launch Tkinter Popup", use_container_width=True):
            subprocess.Popen([sys.executable, "reminder.py", "1"])
        st.caption("Opens a dedicated desktop popup listing today's medications. Never miss a dose.")
    
    st.divider()
    st.subheader("Importance of Vital Progress")
    st.write("Consistent tracking of vitals allows for early detection of health trends and risks. It ensures your treatment plan is working and provides critical data for your healthcare providers.")
