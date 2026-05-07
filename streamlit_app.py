import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import urllib.parse
import json

# Page Configuration
st.set_page_config(
    page_title="WordPress Tag Extractor",
    page_icon="🏷️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stTextArea textarea {
        font-family: monospace;
    }
    .stButton button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

def extract_wp_data(html_content):
    """Parses WordPress HTML and returns a list of dictionaries."""
    if not html_content.strip():
        return []

    # Ensure valid HTML structure for BeautifulSoup
    if ("<tr" in html_content or "<tbody" in html_content) and "<table" not in html_content:
        html_content = f"<table>{html_content}</table>"

    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr')
    
    extracted_data = []

    for row in rows:
        link = row.find('a', class_='row-title')
        if not link:
            continue

        name = link.get_text(strip=True).lstrip('—').strip()
        href = link.get('href', '')
        
        try:
            # Parse URL parameters
            parsed_url = urllib.parse.urlparse(href)
            params = urllib.parse.parse_qs(parsed_url.query)
            
            tag_id = params.get('tag_ID', [None])[0]
            taxonomy = params.get('taxonomy', [''])[0]

            if tag_id:
                # Extract Slug
                slug_cell = row.find(attrs={"data-colname": "Slug"}) or row.find('td', class_='column-slug') or row.find('td', class_='slug')
                slug_text = slug_cell.get_text(strip=True).replace('Slug', '').strip() if slug_cell else 'N/A'

                # Extract Count
                count_cell = row.find(attrs={"data-colname": "Count"}) or row.find('td', class_='column-posts') or row.find('td', class_='posts')
                count = '0'
                if count_cell:
                    count_link = count_cell.find('a')
                    count = (count_link.get_text(strip=True) if count_link else count_cell.get_text(strip=True)).replace('Count', '').strip()

                # Extract View URL
                view_link = row.select_one('.view a')
                view_url = view_link.get('href', '#') if view_link else '#'
                
                # Clean Type
                path_type = taxonomy.replace('resource-', '') if taxonomy else "unknown"

                extracted_data.append({
                    "ID": tag_id,
                    "Name": name,
                    "Slug": slug_text,
                    "Type": path_type,
                    "Count": count,
                    "URL": view_url
                })
        except Exception as e:
            continue

    return extracted_data

# Header
st.title("🏷️ WordPress Tag Extractor")
st.caption("Extract Tag IDs, Names, Slugs, Types, and Post Counts from WordPress HTML")

# Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("HTML Input")
    html_input = st.text_area(
        "Paste <table>, <tbody>, or <tr> blocks here...",
        height=450,
        placeholder="<tr id='tag-123'>..."
    )
    
    # Process Button
    process_btn = st.button("🚀 Process HTML Content", type="primary")

with col2:
    st.subheader("Extracted Data")
    
    # Only run logic if button is clicked
    if process_btn:
        if html_input:
            with st.spinner("Analyzing HTML..."):
                data = extract_wp_data(html_input)
            
            if data:
                df = pd.DataFrame(data)
                st.success(f"Successfully extracted {len(df)} items!")
                
                # Display table
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Action Buttons
                st.divider()
                
                # Download as TSV for Google Sheets
                tsv = df.to_csv(index=False, sep='\t')
                st.download_button(
                    label="📥 Download for Google Sheets (TSV)",
                    data=tsv,
                    file_name="wp_tags.tsv",
                    mime="text/tab-separated-values",
                    use_container_width=True
                )

                # Download as JSON
                json_data = json.dumps(data, indent=4)
                st.download_button(
                    label="📄 Download JSON List",
                    data=json_data,
                    file_name="wp_tags.json",
                    mime="application/json",
                    use_container_width=True
                )
                
                # Copy-friendly text area
                st.text_area("Copy-paste Rows (TSV format):", value=tsv, height=150)
            else:
                st.error("No valid WordPress rows found in the input. Please check your HTML.")
        else:
            st.warning("Please paste some HTML before clicking process.")
    else:
        st.info("Paste your HTML in the left column and click the button to begin.")

# Footer
st.markdown("---")
st.markdown("Created for WordPress taxonomy management.")
