from psrqpy import QueryATNF
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.express as px
import io
import base64
import math

st.set_page_config(layout="wide", page_title="ATNFPulsarDB", page_icon=":telescope:")


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


def sidebar_style():
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


sidebar_style()


@st.cache_resource(experimental_allow_widgets=True)
def filter_data(df):
    p0_min, p0_max = st.sidebar.slider(
        "Filter by P0 (s)",
        math.floor(df["P0"].min()),
        math.ceil(df["P0"].max()),
        (math.floor(df["P0"].min()), math.ceil(df["P0"].max())),
    )
    df = df[(df["P0"] >= p0_min) & (df["P0"] <= p0_max)]

    return df


@st.cache_resource(experimental_allow_widgets=True)
def gofetch():
    options = st.sidebar.multiselect(
        "Choose your parameter(s)",
        ["PSRJ", "F0", "P0", "P1", "RaJ", "DecJ"],
        default=["PSRJ", "P0"],
    )
    col1, col2 = st.sidebar.columns(2)
    with col1:
        nan_replacer = st.button("replace nan values to 0")
    with col2:
        nan_remover = st.button("remove rows with nan values")
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
    df = filter_data(df)
    styles = [
        dict(selector="td", props=[("font-size", "32pt"), ("width", "300px")]),
        dict(
            selector=".col_heading", props=[("font-size", "16pt"), ("width", "8000px")]
        ),
    ]
    styles.append(dict(selector="table", props=[("margin", "auto")]))
    st.dataframe(df.style.set_table_styles(styles), height=500)
    csv = convert_df(df)
    st.download_button(
        label="Download Data",
        data=csv,
        file_name="atnf_data.csv",
        mime="text/csv",
        key="download-csv",
    )

    return df


df = gofetch()


@st.cache_resource(experimental_allow_widgets=True)
def plot_query():
    query = QueryATNF(params=["P0", "P1", "ASSOC", "BINARY", "TYPE", "P1_I"])
    types = {
        "Binary": "BINARY",
        "High-energy": "HE",
        "Non-recycled": "NRAD",
        "Rotating radio": "RRAT",
        "X-ray emitting": "XINS",
        "Anomalous X-ray": "AXP",
        "Associated with supernova remnants": "SNRs",
        "All": "ALL",
    }
    ppdot_options = types.keys()
    ppdot_vars = st.sidebar.multiselect(
        "Choose the pulsar types to be plotted",
        list(ppdot_options),
        default=list(ppdot_options)[-2],
    )
    chosen_plot_types = [types[option] for option in ppdot_vars]
    showSNRs = True if "SNRs" in chosen_plot_types else False
    if "SNRs" in chosen_plot_types:
        chosen_plot_types.remove("SNRs")
    else:
        pass
    ppdot = query.ppdot(showSNRs=showSNRs, showtypes=chosen_plot_types)
    st.write(ppdot)
    img = io.BytesIO()
    plt.savefig(img, format="png")
    btn = st.download_button(
        label="Download plot", data=img, file_name="ppdot.png", mime="image/png"
    )


@st.cache_resource(experimental_allow_widgets=True)
def front_style():
    st.markdown(
        """
    <style>
    .big-font {
        font-size:25px !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "This is a test app for pulsar data query and plotting. It is based on the [ATNF pulsar catalog](https://www.atnf.csiro.au/research/pulsar/psrcat/) and [psrqpy](https://psrqpy.readthedocs.io/en/latest/)."
    )

    st.title("The $P$ - $\dot{P}$ diagram")
    title_alignment = """
    <style>
    #the-title {
    text-align: center
    }
    </style>
    """
    st.markdown(title_alignment, unsafe_allow_html=True)
    st.write(
        """The $P$ - $\dot{P}$ diagram  helps us track pulsars' evolution, identify different pulsar populations, study emission mechanisms, and probe the properties of their interiors. By analyzing the relationship between the pulsar's period ($P$) and its derivative ($\dot{P}$), valuable insights are gained into these rapidly rotating neutron stars and their behavior. The diagram plays a crucial role in advancing our understanding of pulsars and the extreme conditions in the universe."""
    )
    st.write(
        "You can use the option on the left to plot a $P$ - $\dot{P}$ diagram for different pulsar types."
    )

    return


ppdot_button = st.sidebar.checkbox(r"plot a $P$ - $\dot{P}$ diagram.")

if __name__ == "__main__":
    front_style()
    if ppdot_button:
        plot_query()
