# https://psrqpy.readthedocs.io/en/latest/index.html
from psrqpy import QueryATNF
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.express as px
import io
import base64

# https://docs.streamlit.io/knowledge-base/using-streamlit/how-download-pandas-dataframe-csv


@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


@st.cache_resource(experimental_allow_widgets=True)
def gofetch():
    options = st.sidebar.multiselect(
        "Choose your parameter(s)",
        ["PSRJ", "F0", "P0", "P1", "RaJ", "DecJ"],
        default="PSRJ")
    # Use beta_columns to place buttons next to each other
    col1, col2 = st.sidebar.columns(2)
    with col1:
        nan_replacer = st.button("replace nan with 0")
    with col2:
        nan_remover = st.button("remove rows with nan")

    # nan_replacer = st.sidebar.button("replace nan with 0")
    # nan_remover = st.sidebar.button("remove rows with nan")
    query = QueryATNF(options)
    df = query.pandas
    cols = list(df.columns)
    if "PSRJ" in cols:
        cols.insert(0, cols.pop(cols.index("PSRJ")))
        df = df.loc[:, cols]
    if nan_replacer:
        df = df.fillna(0)
    elif nan_remover:
        df.dropna(axis=0, how="any", inplace=True)
    st.dataframe(df, width=2000, height=500)
    # Set the width of the sidebar using CSS
    st.markdown(
        f"""
        <style>
        .sidebar .sidebar-content {{
            width: 300px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    csv = convert_df(df)

    st.download_button(label = "Download Data", data=csv, file_name = "atnf_data.csv", mime = "text/csv", key='download-csv')

    return df


df = gofetch()

def plot_sth():
    plot_button = st.sidebar.checkbox("plot something")

    if plot_button:
        plot_vars = st.sidebar.multiselect(
            "Choose your parameter(s)", ["PSRJ", "F0", "P0", "P1", "RAJ", "DECJ"]
        )
        try:
            fig = px.scatter(
                df, x=plot_vars[0], y=plot_vars[1]
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.error("Select sth from the chosen parameters")
    
    return

ppdot_button = st.sidebar.checkbox(r"plot a $P$ - $\dot{P}$ diagram.")


@st.cache_resource(experimental_allow_widgets=True)
def plot_query():
    query = QueryATNF(params=["P0", "P1", "ASSOC", "BINARY", "TYPE", "P1_I"])
    ppdot_vars = st.sidebar.multiselect(
        "Choose the pulsar types",
        ["BINARY", "HE", "NRAD", "RRAT", "XINS", "AXP", "SNRs", 'ALL'],
        default=['ALL'])
    showSNRs = True if "SNRs" in ppdot_vars else False
    ppdot = query.ppdot(showSNRs=showSNRs, showtypes=ppdot_vars)
    st.write(ppdot)
    img = io.BytesIO()
    plt.savefig(img, format="png")
    btn = st.download_button(
        label="Download plot", data=img, file_name="ppdot.png", mime="image/png"
    )

    return 


if ppdot_button:
    plot_query()
    # advanced_plot_options = st.sidebar.checkbox('Advanced plotting options')
    # if advanced_plot_options:
    #     st.sidebar.multiselect()
