"""
dashboard.py
Streamlit dashboard for displaying and interacting with Freelancer.com job listings.
"""

import streamlit as st
import pandas as pd
import time
from database import JobDatabase
from datetime import datetime, date

def load_jobs(db: JobDatabase, filters: dict) -> pd.DataFrame:
    jobs = db.get_jobs(filters)
    if not jobs:
        return pd.DataFrame()
    df = pd.DataFrame(jobs)
    if 'skills' in df.columns:
        df['skills'] = df['skills'].apply(lambda x: ', '.join(x.split(',')) if isinstance(x, str) else '')
    return df

def main():
    st.set_page_config(page_title="GigPilot - Freelancer.com Job Dashboard", layout="wide")
    st.title("GigPilot: Freelancer.com Job Dashboard")
    db = JobDatabase("jobs.db")

    # Sidebar filters
    st.sidebar.header("Filters")
    keyword = st.sidebar.text_input("Keyword")
    country = st.sidebar.text_input("Client Country")
    budget = st.sidebar.text_input("Budget (exact or partial)")
    skill = st.sidebar.text_input("Skill")
    refresh_interval = st.sidebar.slider("Auto-refresh interval (seconds)", 10, 300, 30)
    filters = {}
    if keyword:
        filters['keyword'] = keyword
    if country:
        filters['country'] = country
    if skill:
        filters['skill'] = skill
    if budget:
        filters['budget'] = budget

    # Remove while True loop and st_autorefresh
    jobs_df = load_jobs(db, filters)
    st.subheader("Job Listings")
    st.write(jobs_df.columns)  # Debug: show available columns
    st.write(f"Total jobs loaded: {len(jobs_df)}")  # Debug: show total jobs loaded
    if jobs_df.empty:
        st.info("No jobs found. Try adjusting your filters or run the scraper.")
    else:
        # Only show columns that exist in the DataFrame
        preferred_cols = ['id', 'title', 'country', 'budget', 'skills', 'snippet', 'link', 'keyword']
        display_cols = [col for col in preferred_cols if col in jobs_df.columns]
        st.dataframe(jobs_df[display_cols])

    # Count of new jobs scraped today
    today = date.today().isoformat()
    jobs_today = jobs_df[jobs_df['date_posted'].str.startswith(today)] if 'date_posted' in jobs_df.columns else pd.DataFrame()
    st.metric("New Jobs Scraped Today", len(jobs_today))

    # Bar chart: job count by keyword or skill
    st.subheader("Job Count by Keyword or Skill")
    chart_option = st.selectbox("Group by", ["keyword", "skills"], key="group_by_chart")
    if not jobs_df.empty:
        if chart_option == "keyword":
            chart_data = jobs_df['keyword'].value_counts().reset_index()
            chart_data.columns = ["Keyword", "Count"]
            st.bar_chart(chart_data.set_index("Keyword"))
        else:
            # Flatten skills for bar chart
            skill_counts = {}
            for skills in jobs_df['skills']:
                for skill in str(skills).split(','):
                    skill = skill.strip()
                    if skill:
                        skill_counts[skill] = skill_counts.get(skill, 0) + 1
            skill_df = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Count"])
            skill_df = skill_df.sort_values("Count", ascending=False)
            st.bar_chart(skill_df.set_index("Skill"))
    else:
        st.info("No data for chart.")

    # Favorites section
    st.subheader("Favorite Jobs")
    favs = db.get_favorites()
    if favs:
        favs_df = pd.DataFrame(favs)
        fav_display_cols = [col for col in preferred_cols if col in favs_df.columns]
        st.dataframe(favs_df[fav_display_cols])
    else:
        st.info("No favorite jobs yet.")

    # Mark/save favorite jobs
    st.markdown("**Favorite a job:**")
    favorite_id = st.number_input("Enter Job ID to favorite/unfavorite", min_value=1, step=1)
    if st.button("Add to Favorites"):
        try:
            db.add_favorite(int(favorite_id))
            st.success(f"Job {favorite_id} added to favorites.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error adding favorite: {e}")
    if st.button("Remove from Favorites"):
        try:
            db.remove_favorite(int(favorite_id))
            st.success(f"Job {favorite_id} removed from favorites.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error removing favorite: {e}")

    # Optionally, show refresh info
    st.info(f"Set auto-refresh interval in the sidebar. Last refresh: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
