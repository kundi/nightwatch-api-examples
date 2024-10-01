
import streamlit as st
import requests
import time
import pandas as pd

def fetch_all_keywords(url_id, access_token, limit=100):
    """Fetch all keywords for a given URL ID."""
    all_keywords = []
    page = 1
    while True:
        response = requests.get(
            f"https://api.nightwatch.io/api/v1/urls/{url_id}/keywords",
            params={"access_token": access_token, "page": page, "limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        
        # Check if data is a list of keywords
        if not isinstance(data, list):
            st.error(f"Unexpected API response structure on page {page}. Expected a list of keywords.")
            # st.write("API response:", data)
            break
        
        all_keywords.extend(data)
        if len(data) < limit:
            break
        page += 1
        time.sleep(1)  # Avoid rate limiting
    return all_keywords

def tag_keyword(url_id, keyword_id, access_token, tags_to_add, tags_to_remove):
    """Tag or untag a keyword."""
    response = requests.get(
        f"https://api.nightwatch.io/api/v1/urls/{url_id}/keywords/{keyword_id}",
        params={"access_token": access_token}
    )
    response.raise_for_status()
    keyword_data = response.json()
    
    current_tags = set(tag["name"] for tag in keyword_data.get("tags", []))
    new_tags = (current_tags | set(tags_to_add)) - set(tags_to_remove)
    
    response = requests.put(
        f"https://api.nightwatch.io/api/v1/urls/{url_id}/keywords/{keyword_id}",
        params={"access_token": access_token},
        json={"keyword": {"tags": list(new_tags)}}
    )
    response.raise_for_status()
    return response.json()

def main():
    st.title("Keyword Tagging Tool")
    st.write("This script will tag the list of provided keywords (query, engine, googleHL, googleGL, if any are omitted it will not search by them) for a specified URL with the corresponding tags.")

    # Input fields
    access_token = st.text_input("Nightwatch API Token", type="password")
    url_id = st.text_input("URL ID")

    # Option to choose manual input or file import
    input_mode = st.radio("Choose input mode:", ("Manual Input", "Import from File (CSV/XLSX)"))

    keyword_list = []
    tags_to_add = []
    tags_to_remove = []

    if input_mode == "Manual Input":
        keywords = st.text_area("Keyword List (one per line, only required field)")
        engine = st.text_area("Engine List (one per line, if omitted will not search by engine)")
        googleHL = st.text_area("Google HL List (one per line, if omitted will not search by googleHL)")
        googleGL = st.text_area("Google GL List (one per line, if omitted will not search by googleGL)")
        tags_to_add = st.text_input("Tags to Apply (comma-separated)")
        tags_to_remove = st.text_input("Tags to Remove (comma-separated)")

        # Ensure no failure if inputs are not provided
        keywords = keywords.split("\n") if keywords else []
        engine = engine.split("\n") if engine else []
        googleHL = googleHL.split("\n") if googleHL else []
        googleGL = googleGL.split("\n") if googleGL else []

        # Strip and filter out empty values
        keywords = [k.strip() for k in keywords if k.strip()]
        engine = [e.strip() for e in engine if e.strip()]
        googleHL = [hl.strip() for hl in googleHL if hl.strip()]
        googleGL = [gl.strip() for gl in googleGL if gl.strip()]

        # Find the longest list length and pad other lists with empty strings
        max_length = max(len(keywords), len(engine), len(googleHL), len(googleGL))

        # Pad each list to make them the same length
        keywords += [""] * (max_length - len(keywords))
        engine += [""] * (max_length - len(engine))
        googleHL += [""] * (max_length - len(googleHL))
        googleGL += [""] * (max_length - len(googleGL))

        # Now zip the lists safely
        keyword_data = zip(keywords, engine, googleHL, googleGL)

        tags_to_add_list = [t.strip() for t in tags_to_add.split(",") if t.strip()]
        tags_to_remove_list = [t.strip() for t in tags_to_remove.split(",") if t.strip()]

        for query, eng, hl, gl in keyword_data:
            keyword_list.append({
                "query": query,
                "engine": eng,
                "google_hl": hl,
                "google_gl": gl,
                "tags_to_add": tags_to_add_list,
                "tags_to_remove": tags_to_remove_list
            })
    else:
        uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"])
        if uploaded_file:
            df = None
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file, header=None)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file, header=None)


            for idx, row in df.iterrows():
                try:
                    query = str(row.iloc[0]) if pd.notna(row.iloc[0]) else None
                    engine = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
                    googleHL = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ""
                    googleGL = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
                    tag_add = row.iloc[4] if len(row) > 4 else None
                    tag_remove = row.iloc[5] if len(row) > 5 else None
                    if pd.notna(query):
                        keyword_list.append({
                            "query": query,
                            "engine": engine,
                            "google_hl": googleHL,
                            "google_gl": googleGL,
                            "tags_to_add": tag_add if pd.notna(tag_add) else "",
                            "tags_to_remove": tag_remove if pd.notna(tag_remove) else ""
                        })
                    else:
                        # Handle cases where the row is too short
                        st.warning(f"Row {idx+1} does not contain query column. Skipping this row.")

                except IndexError:
                    # Handle cases where the row is too short
                    st.warning(f"Row {idx+1} does not contain enough columns. Skipping this row.")

    if st.button("Execute"):
        if not all([access_token, url_id]):
            st.error("Please fill in all required fields.")
            return
        if not keyword_list:
            st.error("No keywords to process.")
            return

        with st.spinner("Fetching keywords..."):
            all_keywords = fetch_all_keywords(url_id, access_token)
            st.success(f"Fetched {len(all_keywords)} keywords.")
        # TESTING
        # all_keywords = [
        #     {"id": 1, "query": "apple", "engine": "google", "google_hl": "en", "google_gl": "US"},
        #     {"id": 2, "query": "banana", "engine": "bing", "google_hl": "fr", "google_gl": "FR"},
        #     {"id": 3, "query": "orange", "engine": "google", "google_hl": "es", "google_gl": "ES"},
        #     {"id": 4, "query": "apple", "engine": "google", "google_hl": "en", "google_gl": "CA"},

        progress_bar = st.progress(0)
        for i, keyword_data in enumerate(keyword_list):

            matching_keywords = [
                k for k in all_keywords 
                if (not keyword_data["query"] or k["query"].lower() == keyword_data["query"].lower())
                and (not keyword_data["engine"] or k["engine"].lower() == keyword_data["engine"].lower())
                and (not keyword_data["google_hl"] or k["google_hl"].lower() == keyword_data["google_hl"].lower())
                and (not keyword_data["google_gl"] or k["google_gl"].lower() == keyword_data["google_gl"].lower())
]
            if matching_keywords:
                for match in matching_keywords:
                    try:
                        tag_keyword(url_id, match["id"], access_token, keyword_data["tags_to_add"], keyword_data["tags_to_remove"])
                        st.write(f"Tagged keyword: {keyword_data['query']}")
                    except requests.RequestException as e:
                        st.error(f"Error tagging keyword {keyword_data['query']}: {str(e)}")
            else:
                st.warning(f"Keyword not found: {keyword_data['query']}, {keyword_data['engine']}, {keyword_data['google_hl']}, {keyword_data['google_gl']}")
            progress_bar.progress((i + 1) / len(keyword_list))

        st.success("Tagging process completed!")

if __name__ == "__main__":
    main()
