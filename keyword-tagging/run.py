
import streamlit as st
import requests
import time

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
    st.write("This script will tag the list of provided keywords for a specified URL with the corresponding tags.")

    # Input fields
    access_token = st.text_input("Nightwatch API Token", type="password")
    url_id = st.text_input("URL ID")
    keywords = st.text_area("Keyword List (one per line)")
    tags_to_add = st.text_input("Tags to Apply (comma-separated)")
    tags_to_remove = st.text_input("Tags to Remove (comma-separated)")

    if st.button("Execute"):
        if not all([access_token, url_id, keywords]):
            st.error("Please fill in all required fields.")
            return

        with st.spinner("Fetching keywords..."):
            all_keywords = fetch_all_keywords(url_id, access_token)
            st.success(f"Fetched {len(all_keywords)} keywords.")

        keyword_list = [k.strip() for k in keywords.split("\n") if k.strip()]
        tags_to_add = [t.strip() for t in tags_to_add.split(",") if t.strip()]
        tags_to_remove = [t.strip() for t in tags_to_remove.split(",") if t.strip()]

        progress_bar = st.progress(0)
        for i, keyword in enumerate(keyword_list):
            matching_keywords = [k for k in all_keywords if k["query"].lower() == keyword.lower()]
            if matching_keywords:
                for match in matching_keywords:
                    try:
                        tag_keyword(url_id, match["id"], access_token, tags_to_add, tags_to_remove)
                        st.write(f"Tagged keyword: {keyword}")
                    except requests.RequestException as e:
                        st.error(f"Error tagging keyword {keyword}: {str(e)}")
            else:
                st.warning(f"Keyword not found: {keyword}")
            progress_bar.progress((i + 1) / len(keyword_list))

        st.success("Tagging process completed!")

if __name__ == "__main__":
    main()