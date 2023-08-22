# Fetch data about radio pulsars using streamlit
This app can be used as a teaching tool for those who are interested in learning about pulsars and their properties. It fetches data, derived from observations, that is particularly useful for studying the evolution and behavior of pulsars as it can provide insights into their magnetic field strengths, ages, and possible evolutionary paths. The $P$ - $\dot{P}$ diagram helps astronomers categorize pulsars into different stages of their lifecycle, understand their energy loss mechanisms

# Some theory first
Pulsars are highly-magnetized, rotating neutron stars that emit beams of electromagnetic radiation out into space. They were first discovered in 1967 by astronomers Jocelyn Bell Burnell and Antony Hewish. Pulsars are incredibly dense objects, composed mostly of neutrons, and they are, mainly, the left overs of supernova explosions. Although they were firt discovered almost 60 years ago, they still remain mysterious, because scientists haven't found out, yet, how they work!


# the goal of this app
This app provides an easy-to-use interface for fetching data, such as the period ($P$) and period derivative ($\dot{P}$) among other parameters.
This is done by using [psrqpy](https://psrqpy.readthedocs.io/en/latest/) to query the [ATNF](https://www.atnf.csiro.au/) pulsar catalog and retrieve the data needed to generate $P$ - $\dot{P}$ diagrams.

<!-- Furthermore, the app can generate $P$ - $\dot{P}$ diagrams, which can be used to gain insights into the behavior of pulsars and the extreme conditions of theenvironments close to their vicinities. -->

# The $P$ - $\dot{P}$ diagram

The $P$ - $\dot{P}$ diagram, also known as the Pulsar Spin-Down Diagram, is a graphical representation that helps astronomers study the evolution and properties of pulsars. It plots two key parameters of pulsars: the pulsar's rotation period ($P$) and its rate of change of rotation period ($\dot{P}$). ($P$) is the time it takes for the pulsar to complete one full rotation on its axis and $\dot{P}$ represents the rate at which the pulsar's rotation period is changing over time. Pulsars gradually slow down due to the loss of rotational energy and $\dot{P}$ gives insight into the pulsar's age, magnetic field strength, and the nature of its emission mechanisms. That's why it's an imporant observable and together with $P$,
we can study study pulsars using such diagrams.

Here's an example of a $P$ - $\dot{P}$ diagram

![ppdot](https://raw.githubusercontent.com/alexfilothodoros/streamlit_atnf_requests/main/ppdot.png)


# Now let's check the code

This code defines a function called gofetch() that fetches data from the ATNF Pulsar Catalogue using the QueryATNF function from the psrqpy package. The function allows the user to choose which parameters to fetch and provides options to replace or remove rows with NaN values. The fetched data can be filtered using the filter_data() function and displayed in a table using the dataframe() function. The table is styled using CSS and a download button is provided to download the data as a CSV file.

```python
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
```


## Creating the $P$ - $\dot{P}$ diagram
This code defines a function plot_query() that generates a scatter plot of  $P$ versus $\dot{P}$. The user can define the pulsar types whose parameters will be plotted. This is useful for, quickly, comparing the different properties of each pulsar type. The function uses the QueryATNF class to query the ATNF pulsar catalog and retrieve the relevant data. The types of pulsars to be plotted are selected by the user through a multiselect widget in the sidebar. The function then generates the scatter plot using matplotlib and displays it using streamlit. Finally, the function provides a download button for the plot image.

```
# @st.cache_resource(experimental_allow_widgets=True)
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
```
# Styling
This code defines a function called front_style() that sets the front-end style of the app. 

The function sets the font size of the app to 25px and adds a markdown description of the app. It also sets the title of the app to "The $P$ - $\dot{P}$ diagram" and adds a markdown description of what the diagram is used for. Finally, it adds a message to the user to use the option on the left to plot a $P$ - $\dot{P}$ diagram for different pulsar types.

This function is called in the main block of the code when the user selects the ppdot_button checkbox.


```
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
```
# Wrapping up

This app is providing an friendlier experience in getting data about radio pulsars.
It offers some basic filtering on the two most important characteristics of these stars (the period and its derivative). This information can be plotted and the properties of different pulsar groups can be compared on a $P$ - $\dot{P}$ diagram.

Enjoy!
