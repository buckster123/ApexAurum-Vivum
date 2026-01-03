"""
Quick Reference Module

Provides a quick reference guide for ApexAurum UI features.
Simple, reliable - just shows where things are in the UI.
"""

import streamlit as st
from typing import Dict, List


# Quick reference - maps features to their UI locations
QUICK_REFERENCE: Dict[str, List[Dict]] = {
    "Conversation": [
        {"icon": "💾", "label": "Save", "location": "Sidebar top"},
        {"icon": "🆕", "label": "New", "location": "Sidebar top"},
        {"icon": "🔍", "label": "Search", "location": "Conversation History"},
    ],
    "Agents": [
        {"icon": "➕", "label": "Spawn Agent", "location": "Agent Quick Actions"},
        {"icon": "🗳️", "label": "Socratic Council", "location": "Agent Quick Actions"},
        {"icon": "📊", "label": "Agent Status", "location": "Agent Monitoring"},
    ],
    "Settings": [
        {"icon": "⚙️", "label": "Presets", "location": "Sidebar middle"},
        {"icon": "🎛️", "label": "Model Selection", "location": "Below presets"},
        {"icon": "📝", "label": "System Prompt", "location": "Advanced Settings"},
    ],
    "Data": [
        {"icon": "📤", "label": "Export", "location": "Data Management"},
        {"icon": "📥", "label": "Import", "location": "Data Management"},
        {"icon": "📚", "label": "Knowledge", "location": "Data Management"},
    ],
    "Navigation": [
        {"icon": "🏘️", "label": "Village Square", "location": "Pages menu (top-left)"},
        {"icon": "📊", "label": "Thread Graph", "location": "Thread Browser"},
        {"icon": "🔮", "label": "Convergence", "location": "Thread Browser"},
    ],
}


def render_cheat_sheet():
    """Render the quick reference guide showing where UI features are located."""
    for category, items in QUICK_REFERENCE.items():
        st.caption(f"**{category}**")
        for item in items:
            col1, col2 = st.columns([2, 2])
            with col1:
                st.write(f"{item['icon']} {item['label']}")
            with col2:
                st.caption(item['location'])


__all__ = [
    "QUICK_REFERENCE",
    "render_cheat_sheet",
]
