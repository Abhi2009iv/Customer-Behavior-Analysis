import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Customer Behavior — Demo Dashboard")

@st.cache_data
def load_data():
    users = pd.read_csv("data/users.csv", parse_dates=["signup_date"])
    events = pd.read_csv("data/events.csv", parse_dates=["event_time"])
    return users, events

users, events = load_data()

st.header("Overview")
col1, col2 = st.columns(2)
with col1:
    mau = events.set_index("event_time").resample("M")["user_id"].nunique()
    st.line_chart(mau.rename("MAU"))
with col2:
    dau = events.set_index("event_time").resample("D")["user_id"].nunique()
    st.line_chart(dau.rename("DAU"))

st.header("Retention (week cohorts)")
# compute rough retention heatmap
events["week"] = events["event_time"].dt.to_period("W").apply(lambda r: r.start_time.date())
users["cohort_week"] = users["signup_date"].dt.to_period("W").apply(lambda r: r.start_time.date())
merged = events.merge(users[["user_id","cohort_week"]], on="user_id", how="left")
cohort = merged.groupby(["cohort_week","week"])["user_id"].nunique().reset_index()
pivot = cohort.pivot(index="cohort_week", columns="week", values="user_id").fillna(0)
fig, ax = plt.subplots(figsize=(10,6))
sns.heatmap(pivot, cmap="YlGnBu", ax=ax)
st.pyplot(fig)

st.header("Top events")
evs = events["event_name"].value_counts().reset_index()
evs.columns = ["event","count"]
st.table(evs.head(10))
