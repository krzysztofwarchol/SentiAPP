import praw
import streamlit as st
import plotly.express as px
import pandas as pd
from transformers import pipeline
import altair as alt
import os
import time

# from dotenv import load_dotenv
# load_dotenv()

client_id = os.environ.get('REDDIT_ID')
client_secret = os.environ.get('REDDIT_SECRET')
password = os.environ.get('REDDIT_PASSWORD')
username = os.environ.get('REDDIT_USERNAME')

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret, 
                     password=password,
                     user_agent='bot_data',
                     username=username)

classifier = pipeline("text-classification",model='bhadresh-savani/albert-base-v2-emotion', top_k=None)
st.set_page_config(page_title="SentiAPP")

@st.cache_data
def get_subreddit(input_val):
        headlines = []
        for submission in reddit.subreddit(input_val).hot(limit=None):

            element= {'title': submission.title, 'date': submission.created_utc, 
                            'url': submission.url, 'score': submission.score, 
                            'upvote_ration': submission.upvote_ratio
                            }
            headlines.append(element)
        df = pd.DataFrame(headlines)
        df['date'] = pd.to_datetime(df['date'], unit='s')
        return df
     

st.title("Sentiment analysis - SentiAPP")
input = st.text_input("Enter the name of the subreddit:", value='nba')


def get_main_emotion(text):
    result = classifier(text)
    sorted_result = sorted(result[0], key=lambda x: x['score'], reverse=True)
    emotion = sorted_result[0]['label']
    return emotion

def handle_subreddit():
    if input:
        with st.spinner('Sentiment analysis...'):
            progress_bar = st.progress(0)
            for row_num, row in df.iterrows():
                df.at[row_num, 'emotion'] = get_main_emotion(row['title'])
                progress_percent = int((row_num + 1) / len(df) * 100)
                progress_bar.progress(progress_percent) 

def get_emotions_new_post():
            text = df['title'][0]
            result = classifier(text)
            sorted_result = sorted(result[0], key=lambda x: x['score'], reverse=False)
            df_res = pd.DataFrame.from_dict(sorted_result)
            st.write("**Emotional sentiment of the latest post**")
            st.write(f"Text: {text}")
            chart_emotion_one = alt.Chart(df_res).mark_bar().encode(
            x='score',
            y='label',)
            st.altair_chart(chart_emotion_one, use_container_width=True)


clicked_btn = st.button("Analyze")

if clicked_btn:
    try:
        df = get_subreddit(input)
        
        handle_subreddit()
            
        st.write(f"**Subreddit**: {input},  **Posts**: {len(df)}")
        st.dataframe(df)
        fig = px.histogram(df['date'], x="date", title='Number of posts over time')
        st.plotly_chart(fig, theme="streamlit", use_container_width=True, color="continent")

        get_emotions_new_post()


        chart_emotion_total = alt.Chart(df).mark_bar().encode(
                x='count()',
                y='emotion',)

        st.write("**Overall emotional sentiment of posts**")
        st.altair_chart(chart_emotion_total, use_container_width=True)

        fig2 = fig = px.histogram(df, x="date", color='emotion', title='Emotional sentiment of posts over time')
        st.plotly_chart(fig2, theme="streamlit", use_container_width=True, color="continent")

        percent_emotions = df['emotion'].value_counts(normalize=True) * 100

        emotion_dict = df['emotion'].value_counts().to_dict()
        sum_all = sum(emotion_dict.values())
        formated_dict = {"emotion": [el for el in emotion_dict], "value": [val/sum_all for key, val in emotion_dict.items()]}
        emotion_df = pd.DataFrame.from_dict(formated_dict)

        st.write("**Percentage of emotions in posts [%]**")
        pie = alt.Chart(emotion_df).mark_arc().encode(
                theta="value",
                color="emotion"
            )
        
        st.altair_chart(pie, use_container_width=True)

    except:
        st.warning('Subbreddit provided does not exist!')