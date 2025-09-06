"""Streamlit frontend for Phase Analyzer SaaS.

This app demonstrates how users might upload files and trigger
processing jobs. For now it only shows plan limits and accepts
uploads without further processing."""

import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Phase Analyzer")
st.title("Phase Analyzer SaaS")

plan = st.selectbox("Select plan", ["free", "pro", "team"], index=0)

if st.button("Show plan limits"):
    resp = requests.get(f"{API_URL}/entitlements/{plan}")
    if resp.ok:
        st.json(resp.json())
    else:
        st.error("Failed to fetch entitlements")

uploaded_files = st.file_uploader("Upload XML files", accept_multiple_files=True)
if uploaded_files:
    st.write(f"{len(uploaded_files)} file(s) queued for processing")
    # Real implementation would send files to object storage and enqueue a job
