import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import streamlit_wordcloud as st_wordcloud
import nltk
import pycountry
import geopandas as gpd
import altair as alt
nltk.download('punkt')
nltk.download('stopwords')


header_container = st.container()
wordcloud_container = st.container()
map_container = st.container()
dataset_container =  st.container()

df = pd.read_excel("HRI 2022 LBR Sessions_010322.xlsx", sheet_name="All_LBRs")

def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="light",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection

def get_rows_contains_word(df,colname, word):
    contain_values = df[df[colname].str.lower().str.strip().str.contains(word)]
    return contain_values


with header_container:
    st.title("HRI 2022 LBR Accepted Papers")
    st.text("""This webpage just gives an overview of the paper submitted at HRI as LBRs
    """)

with wordcloud_container:
    st.header("Wordcloud of keywords used in the dataset")
    text = " ".join(name for name in df.Title)
    # stop words list
    
    stop = nltk.corpus.stopwords.words('english')
    list_of_stop_words = ["paper","robot","robots","study","social","human","interaction",
    "results","participants","people","using","human-robot","robots.","used","data","present","approach","could","based","two","one"]

    list_of_stop_words = st.multiselect("List of words not included in the wordcloud", list_of_stop_words, list_of_stop_words)

    stop.extend(list_of_stop_words)
   

    # Create and generate a word cloud imagestr.lower().str.strip():
    df.cleanAbs = df.Title.str.lower().str.strip().str.split()
    df['Clean'] = df.cleanAbs.apply(lambda x: [w.strip() for w in x if w.strip() not in stop])
    df['Clean'] = pd.DataFrame( df['Clean'])

    words = df.Clean.tolist()
    flat_list = [item for sublist in words for item in sublist]
    wdic = [dict(text = i, value = flat_list.count(i), title = list(get_rows_contains_word(df,'Title',i)['Title'].values)) for i in set(flat_list)]
    #st.text(wdic)

    wc = st_wordcloud.visualize(words=wdic,tooltip_data_fields={'text': 'text','value': 'value','title':'title'} , max_words=100)
    
    #st.write(wc)
    #st.write(wc["clicked"])
   
    


with map_container:

    st.header("Per country distribution of papers")
    df_country_count = df.groupby(['Affiliation Country']).count()['Paper No']
    
    #df_country_count['Affiliation Country'] = df_country_count.index
    df_country_count = pd.DataFrame(df_country_count,columns=["Paper No"])
    df_country_count.reset_index(inplace=True)

    countries = {}
    for country in pycountry.countries:
        countries[country.name] = country.alpha_3

    df_country_count['iso_a3'] = [countries.get(country, 'Unknown code') for country in df_country_count['Affiliation Country']]

    #st.write(df_country_count)
    df_country_count.loc[df_country_count['Affiliation Country']== 'Republic of Korea','iso_a3'] = 'KOR'
    df_country_count.loc[df_country_count['Affiliation Country']== 'USA','iso_a3'] = 'USA'
    df_country_count.loc[df_country_count['Affiliation Country']== 'Taiwan Roc','iso_a3'] = 'TWN'
    df_country_count.loc[df_country_count['Affiliation Country']== 'Czech Rep','iso_a3'] = 'CZE'

    #st.write(df_country_count)

    bars = alt.Chart(df_country_count).mark_bar().encode(
            x='Affiliation Country:O',
            y="Paper No:Q"
            )

    text = bars.mark_text(
        align='center',
        baseline='middle',
        dy=-5  # Nudges text to right so it doesn't appear on top of the bar
        ).encode(
        text='Paper No:Q'
    )

    c = (bars + text)
    
    #world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    #world  = world[world.continent!='Antarctica']
    #world_join = pd.merge(world,df_country_count,on="iso_a3",how='left')
    #world_join[''] = world_join['Paper No'].fillna(0)
    #st.write(world_join)

    #c = alt.Chart(world_join).mark_geoshape().encode(color = alt.Color(field = "Paper No",type = "quantitative"))
    st.altair_chart(c, use_container_width=True)


with dataset_container:
    st.header('List of all the LBR papers presented at HRI2022')
  
    selection = aggrid_interactive_table(df=df)

    if selection:
        st.write("You selected:")
        st.json(selection["selected_rows"])
    



st.write()