import streamlit as st

home_page = st.Page("Home.py", title="Home", icon="🏠")
connectivity_page = st.Page("pages/1_connectivity.py", title="Connectivity", icon="🔌")
document_processing_page = st.Page("pages/2_document_processing.py", title="Document Processing", icon="📄")
interactive_assistant_page = st.Page("pages/3_interactive_assistant.py", title="Interactive Assistant", icon="💬")
monitor_page = st.Page("pages/4_monitor.py", title="Operations Monitor", icon="📊")

# Pass them to navigation
pg = st.navigation([home_page, connectivity_page, document_processing_page, interactive_assistant_page, monitor_page])
pg.run()