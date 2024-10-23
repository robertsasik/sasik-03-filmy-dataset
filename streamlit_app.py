# 🎬 Filmy dataset

import altair as alt
import pandas as pd
import streamlit as st

# Zobraziť názov stránky a popis.
st.set_page_config(page_title="Filmy dataset", page_icon="🎬")
st.title("🎬 Filmy dataset")
st.write(
    """
    Táto aplikácia vizualizuje údaje z [The Movie Database (TMDB)](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata).
    Ukazuje, ktorý filmový žáner mal v kinách za posledné roky najlepší výkon. 
    Stačí kliknúť na miniaplikácie nižšie a preskúmať ich!
    """
)

# Načítajte údaje z CSV. Ukladáme to do vyrovnávacej pamäte, aby sa nenačítalo znova pri každom spustení aplikácie (napr. ak používateľ interaguje s miniaplikáciami).
@st.cache_data
def load_data():
    df = pd.read_csv("data/movies_genres_summary.csv")
    return df

df = load_data()

# Zobrazte miniaplikáciu s viacerými výbermi so žánrami pomocou `st.multiselect`.
genres = st.multiselect(
    "Žánre",
    df.genre.unique(),
    ["Action", "Adventure", "Biography", "Comedy", "Drama", "Horror"],
)

# Zobrazte miniaplikáciu jazdca s rokmi pomocou `st.slider`.
years = st.slider("Roky", 1986, 2006, (2000, 2016))

# Filtrujte dátový rámec na základe vstupu widgetu a pretvorte ho.
df_filtered = df[(df["genre"].isin(genres)) & (df["year"].between(years[0], years[1]))]
df_reshaped = df_filtered.pivot_table(
    index="year", columns="genre", values="gross", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="year", ascending=False)

# Zobrazte údaje ako tabuľku pomocou `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"year": st.column_config.TextColumn("Rok")},
)

# Zobrazte údaje ako Altairovu tabuľku pomocou `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="year", var_name="genre", value_name="gross"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("year:N", title="Rok"),
        y=alt.Y("gross:Q", title="Zisk ($)"),
        color="genre:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)

# Pridajte stĺpcový graf s celkovými zárobkami podľa žánru.
st.write("### Celkové zárobky podľa žánru")
genre_totals = df_filtered.groupby("genre")["gross"].sum().reset_index()

bar_chart = (
    alt.Chart(genre_totals)
    .mark_bar()
    .encode(
        x=alt.X("genre:N", title="Žáner"),
        y=alt.Y("gross:Q", title="Celkové zárobky ($)", scale=alt.Scale(domain=[0, 2500000000])),
        color="genre:N",
    )
    .properties(height=320)
)

# Pridanie textových popisov do stĺpcového grafu
bar_chart_text = bar_chart.mark_text(
    align='center',
    baseline='middle',
    dy=-10  # Posúva text nad stĺpce
).encode(
    text=alt.Text('gross:Q', format='$,.0f')  # Formátovanie hodnôt ako dolárov
)

st.altair_chart(bar_chart + bar_chart_text, use_container_width=True)

# Pridajte koláčový graf pre rozdelenie zárobkov podľa žánru s percentami.
st.write("### Rozdelenie celkových zárobkov podľa žánru")
total_gross = genre_totals["gross"].sum()
genre_totals["percentage"] = genre_totals["gross"] / total_gross * 100  # Výpočet percent

pie_chart = (
    alt.Chart(genre_totals)
    .mark_arc(innerRadius=50)  # Pridanie vnútorného polomeru pre koláčový graf
    .encode(
        theta=alt.Theta("gross:Q", title="Zárobky ($)", stack=True),
        color=alt.Color("genre:N", legend=None),
        tooltip=["genre:N", "gross:Q", alt.Tooltip("percentage:Q", format=".2f", title="Percentá (%)")]
    )
    .properties(height=320)
)

# Pridanie textových popisov do koláčového grafu s percentami vo vnútri
pie_chart_text = pie_chart.mark_text(radius=30, size=12).encode(
    text=alt.Text("percentage:Q", format=".1f")  # Zobrazenie percent s jedným desatinným miestom
)

st.altair_chart(pie_chart + pie_chart_text, use_container_width=True)
