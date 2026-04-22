"""OST tree component — Week 2 implementation"""
import streamlit as st

def render_ost_tree(ost: dict):
    st.info("OST tree — Week 2")
    st.json(ost)
