import streamlit as st
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import pandas as pd
import requests
from config import API_KEY


# DB management
conn = sqlite3.connect('./database/data.db')
c = conn.cursor()

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')

def add_userdata(username, password):
    hashed_password = generate_password_hash(password, method='sha256')
    
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()


def check_authenticated():
    menu = ["Login", "Sign Up"]
    
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Login":
        st.subheader("Login Section")

        username = st.text_input("User Name")
        password = st.text_input("Password", type='password', key="login_pass")
        
        if st.button("Login"):
            if len(username) == 0 and len(password) == 0:
                    st.error("You haven't typed anything to log in!", icon="🚨")
            elif len(username) < 3:
                st.error('Your username has to be more than or equal 3 characters', icon="🚨")
            elif len(password) < 6:
                st.error('Your password has to be more then or equal 6 characters', icon="🚨")
            else:   
                create_usertable()
                c.execute('SELECT * FROM userstable WHERE username=?', (username,))
                data = c.fetchone()
                if data:
                    if check_password_hash(data[1], password):
                        st.success("Logged In as {}".format(username))
                        st.session_state["page"] = "main"
                        st.balloons()
                        st.experimental_rerun()
                else:
                    st.error('Account does not exist!', icon="🚨")
    
    elif choice == "Sign Up":
        st.subheader("Create New Account")

        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password', key="signup_pass")
        
        if st.button("Sign Up"):
            create_usertable()
            c.execute('SELECT * FROM userstable WHERE username=?', (new_user,))
            data = c.fetchone()
            
            if data:
                st.error('Username already exist!', icon="🚨")
            else:
                if len(new_user) == 0 and len(new_password) == 0:
                    st.error("You haven't typed anything to sign up!", icon="🚨")
                elif len(new_user) < 3:
                    st.error('Your username has to be more than or equal 3 characters', icon="🚨")
                elif len(new_password) < 6:
                    st.error('Your password has to be more then or equal 6 characters', icon="🚨")
                
                else:
                    add_userdata(new_user, new_password)
                    st.success("You have successfully created an account!")
                    st.info("Go to Login Menu to login")
    return False


# create poster function
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(movie_id, API_KEY)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    
    return full_path

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
        
        recommended_movies = []
        recommended_movies_posters = []
        for i in movies_list:
            # fetch the movie poster
            movie_id = movies.iloc[i[0]].id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))
        return recommended_movies, recommended_movies_posters
    except:
        return None


def main_screen():

    selected_movie_name = st.selectbox(
        "Type or select a movie from the dropdown",
        movies['title'].values
    )

    if st.button('Show Recommendation'):
        names, posters = recommend(selected_movie_name)

        #display with the columns
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)
        col7, col8, col9 = st.columns(3)
        
        with col1:
            st.text(names[0])
            st.image(posters[0])
        with col2:
            st.text(names[1])
            st.image(posters[1])
        with col3:
            st.text(names[2])
            st.image(posters[2])
        with col4:
            st.text(names[3])
            st.image(posters[3])
        with col5:
            st.text(names[4])
            st.image(posters[4])
        with col6:
            st.text(names[5])
            st.image(posters[5])
        with col7:
            st.text(names[6])
            st.image(posters[6])
        with col8:
            st.text(names[7])
            st.image(posters[7])
        with col9:
            st.text(names[8])
            st.image(posters[8])
    
    if st.button("Log out"):
        st.session_state["page"] = "login"
        st.experimental_rerun()


def main():
    st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🕸",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "## A content based movie recommendation system build using cosine similarity"
    }
    )

    st.title('Movie Recommender System')
    
    if "page" not in st.session_state:
        st.session_state["page"] = "login"
    
    if st.session_state["page"] == "login":
        check_authenticated()
    elif st.session_state["page"] == "main":
        main_screen()



if __name__ == '__main__':
    movies_dict = pickle.load(open('./Dataset/movies.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('./Dataset/similarity.pkl', 'rb'))
    main()

