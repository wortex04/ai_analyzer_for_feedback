import streamlit as st
import requests
import io

import pandas as pd
import altair as alt
import datetime

import plotly.express as px
from pydantic import BaseModel
import json

today = datetime.datetime.now()
prev_year = today.year - 1
jan_1 = datetime.date(today.year, 1, 1)
dec_31 = datetime.date(today.year + 1, 12, 31)


class Review(BaseModel):
    like: str = ""
    difficult: str = ""
    improve: str = ""
    new_knowledge: str = ""
    positive: bool = True
    informative: bool = True
    object: int = 0


# Функция для отображения списка кастомных объектов
def display_custom_item(custom_item: Review):
    st.write(f"**Понравилось:**"
             f"<br>"
             f"{custom_item.like}", unsafe_allow_html=True)
    st.write(f"**Сложные моменты:**"
             f"<br>"
             f"{custom_item.difficult}", unsafe_allow_html=True)
    st.write(f"**Что можно улучшить:**"
             f"<br>"
             f"{custom_item.improve}", unsafe_allow_html=True)
    st.write(f"**Чтобы хотелось узнать:**"
             f"<br>"
             f"{custom_item.new_knowledge}", unsafe_allow_html=True)
    st.divider()


st.set_page_config(
    page_title="Анализатор обратной связи",
    page_icon="🐼",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']

    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100 - input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })

    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            # domain=['A', 'B'],
                            domain=[input_text, ''],
                            # range=['#29b5e8', '#155F7A']),  # 31333F
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)

    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700).encode(
        text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            # domain=['A', 'B'],
                            domain=[input_text, ''],
                            range=chart_color),  # 31333F
                        legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text


# load data
response = requests.get("http://127.0.0.1:8000/api/v2/streamlit/get_csv_from_s3")

# Check if the request was successful (status code 200)
data = pd.read_csv("train_data.csv")
if response.status_code == 200:
    # Read the CSV data into a pandas dataframe
    data = pd.read_csv(io.StringIO(response.text))


with st.sidebar:
    st.title('🐼 Анализатор обратной связи')

    selected_webinar = st.selectbox("Select webinar", data['question_1'].unique())

    d = st.date_input(
        "Select your vacation for next year",
        (jan_1, datetime.date(today.year, 10, 7)),
        jan_1,
        dec_31,
        format="DD.MM.YYYY",
    )

    with open("sum_data.json", "r", encoding="UTF-8") as f:
        json_sum_data = json.load(f)
    sum_text = json_sum_data[selected_webinar]

try:
    data_1 = data[(data['question_1'] == selected_webinar) & data['timestamp'].apply(
        lambda x: pd.Timestamp(x).date()).between(pd.Timestamp(d[0]).date(), pd.Timestamp(d[1]).date())]
except Exception:
    data_1 = data[(data['question_1'] == selected_webinar) & data['timestamp'].apply(
        lambda x: pd.Timestamp(x).date()).between(pd.Timestamp(datetime.date(today.year, 1, 1)).date(),
                                                  pd.Timestamp(datetime.date(today.year, 12, 31)).date())]

col = st.columns((3, 5, 3))

df = data_1[['is_relevant', 'object', 'is_positive']]

with col[1]:
    st.markdown("#### Общий анализ комментариев")

    show_full_text = st.button("Показать полностью")

    # Отображение текста в зависимости от статуса кнопки
    if show_full_text:
        # Показать полный текст
        st.markdown(f"<div style='word-wrap: break-word;'>{sum_text}</div>", unsafe_allow_html=True)
        # Кнопка "Скрыть"
        if st.button("Скрыть"):
            show_full_text = False
    else:
        # Первая часть текста
        l = min(200, len(sum_text)-1)
        teaser_text = f'{sum_text[:l]}...'
        # Отображение первой части текста
        st.markdown(f"<div style='word-wrap: break-word;'>{teaser_text}</div>", unsafe_allow_html=True)



with col[2]:
    st.markdown("#### Диаграммы")

    grouped_data = df.groupby('object').mean().reset_index()

    # Создание столбчатой диаграммы с Plotly Express
    fig = px.bar(grouped_data, x='object', y=['is_relevant', 'is_positive'],
                 barmode='stack', title='Столбчатая диаграмма: Релевантность и Тональность по классу отзыва',
                 labels={'object': 'Класс отзыва', 'value': 'Среднее значение', 'variable': 'Характеристика'})

    # Отображение диаграммы в Streamlit
    st.plotly_chart(fig, use_container_width=True)

    try:
        res1 = int((data_1.is_positive == 1).sum() * 100 / data_1.shape[0])
        res2 = int((data_1.is_relevant == 1).sum() * 100 / data_1.shape[0])
    except:
        res1 = 0
        res2 = 0

    donut_chart_greater1 = make_donut(res1, 'positive', 'green')
    # st.altair_chart(donut_chart_greater1)

    donut_chart_greater2 = make_donut(res2, 'relevant', 'blue')
    # st.altair_chart(donut_chart_greater2

    donut_col = st.columns(2)
    with donut_col[0]:
        st.write('Положительные')
        st.altair_chart(donut_chart_greater1, use_container_width=True)
    with donut_col[1]:
        st.write('Информативные')
        st.altair_chart(donut_chart_greater2, use_container_width=True)

    objects = ["Вебинар", "Программа", "Преподаватель"]

    names = [objects[i] for i in df['object'].value_counts().index]
    fig_pie = px.pie(df['object'].value_counts(), labels=df['object'].value_counts().index,
                     values=df['object'].value_counts().values,
                     title='Круговая диаграмма: Распределение классов отзывов', hole=0.3,
                     names=names)
    st.plotly_chart(fig_pie, use_container_width=True)

with col[0]:
    st.markdown('#### Комментарии')

    options = st.multiselect(
        "Выберите какие вы хотите увидеть комментарии:",
        ["Положительные", "Отрицательные", "Информативные", "Не информативные", "Вебинар", "Программа", "Преподаватель"]
    )


    def review_matches_options(review, options):
        if "Положительные" in options and not review.positive:
            return False
        if "Отрицательные" in options and review.positive:
            return False
        if "Информативные" in options and not review.informative:
            return False
        if "Не информативные" in options and review.informative:
            return False
        if "Вебинар" in options and review.object != 0:
            return False
        if "Программа" in options and review.object != 1:
            return False
        if "Преподаватель" in options and review.object != 2:
            return False
        return True


    reviews = []
    for index, row in data_1.iterrows():
        review = Review(
            like=row['question_2'],
            difficult=row['question_3'],
            improve=row['question_4'],
            new_knowledge=row['question_5'],
            positive=bool(row['is_positive']),
            informative=bool(row['is_relevant']),
            object=int(row['object'])
        )
        if review_matches_options(review, options):
            reviews.append(review)

    try:
        with st.container(height=646):

            for item in reviews:
                display_custom_item(item)

    except Exception as e:
        print(e)
