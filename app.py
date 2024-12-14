import streamlit as st
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity

# Tambahkan background menggunakan CSS
def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://i.imgur.com/6XmZcp0.jpeg");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Panggil fungsi background
add_bg_from_url()

# Fungsi untuk mengambil poster film
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    if 'poster_path' in data and data['poster_path']:
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    return None

# Load data
movies = pickle.load(open('movie_list (3).pkl', 'rb'))
similarity = pickle.load(open('similarity (2).pkl', 'rb'))
cv = pickle.load(open('cv.pkl', 'rb'))  # Load CountVectorizer
vectors = pickle.load(open('vectors.pkl', 'rb'))

# Fungsi rekomendasi berdasarkan judul
def recommend_title(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    for i in distances[1:6]:
        recommended_movies.append(movies.iloc[i[0]].movie_id)
    return recommended_movies

# Rekomendasi input bebas
def recommend_free_input(text):
    input_vector = cv.transform([text]).toarray()
    input_similarity = cosine_similarity(input_vector, vectors)
    distances = sorted(list(enumerate(input_similarity[0])), reverse=True, key=lambda x: x[1])
    return [movies.iloc[i[0]].movie_id for i in distances[1:6]]

# Streamlit UI
st.header("📽 Sistem Rekomendasi Film")

option = st.radio("Choose input method:", ['judul', 'genre', 'input bebas'])

if option == 'judul':
    movie_list = movies['title'].values
    selected_movie = st.selectbox("pilih film:", movie_list)
    if st.button('cari rekomendasi'):
        movie_ids = recommend_title(selected_movie)
        for movie_id in movie_ids:
            st.image(fetch_poster(movie_id))

elif option == 'genre':
    genres = ['Action', 'Comedy', 'Drama', 'Fantasy', 'Horror']
    selected_genre = st.selectbox("pilih genre:", genres)
    if st.button('cari rekomendasi'):
        genre_movies = movies[movies['tags'].str.contains(selected_genre.lower())]
        for _, row in genre_movies.head(5).iterrows():
            st.image(fetch_poster(row['movie_id']))

elif option == 'input bebas':
    user_input = st.text_input("masukkan deskripsi atau kata kunci:")
    if st.button('cari rekomendasi'):
        movie_ids = recommend_free_input(user_input)
        for movie_id in movie_ids:
            st.image(fetch_poster(movie_id))


