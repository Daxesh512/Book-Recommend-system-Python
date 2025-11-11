import streamlit as st
import pickle
import pandas as pd
import gdown
import os

# Set output filenames
similarity_file = 'similarity.pkl'
books_file = 'books.pkl'

# Get file IDs from Streamlit secrets
try:
    similarity_id = st.secrets['similarity']
    books_id = st.secrets['books']
except Exception as e:
    st.error("Missing Google Drive file IDs in `.streamlit/secrets.toml`.")
    st.stop()

# Download similarity.pkl if not exists
if not os.path.exists(similarity_file):
    st.info("Downloading similarity.pkl from Google Drive...")
    gdown.download(id=similarity_id, output=similarity_file, quiet=False)

# Load similarity
with open(similarity_file, 'rb') as f:
    similarity = pickle.load(f)

# Download books.pkl if not exists
if not os.path.exists(books_file):
    st.info("Downloading books.pkl from Google Drive...")
    gdown.download(id=books_id, output=books_file, quiet=False)

# Load books
with open(books_file, 'rb') as f:
    books = pd.DataFrame(pickle.load(f))

# Recommendation function
def recommend(book):
    try:
        book_index = books[books['title'] == book].index[0]
        distances = similarity[book_index]
        books_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:21]

        recommended_books = []
        recommended_books_posters = []
        for i in books_list:
            recommended_books.append(books.loc[i[0]].title)
            recommended_books_posters.append(books.loc[i[0]].thumbnail)
        return recommended_books, recommended_books_posters
    except IndexError:
        return [], []

# Streamlit UI
st.title('📚 Book Recommendation System')

option = st.selectbox(
    "🔍 Search Similar Books",
    books['title'].values,
    index=None,
    placeholder="Select a book...",
)

if st.button("Recommend") and option:
    names, posters = recommend(option)

    if not names:
        st.warning("No recommendations found. Try another book.")
    else:
        num_books = len(names)
        num_cols = 4
        rows = (num_books + num_cols - 1) // num_cols

        for row in range(rows):
            cols = st.columns(num_cols)
            for col_idx in range(num_cols):
                idx = row * num_cols + col_idx
                if idx < num_books:
                    with cols[col_idx]:
                        st.markdown(
                            f"""
                            <div style="height: 250px; text-align: center;">
                                <img src="{posters[idx]}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;" />
                                <p style="margin-top: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;" title="{names[idx]}">
                                    {names[idx]}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
