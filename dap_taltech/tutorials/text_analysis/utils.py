import pandas as pd
import altair as alt
from toolz import pipe
import numpy as np
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import torch
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
from transformers import AutoTokenizer, AutoModel

def hist_plot(pubdataframe: pd.DataFrame, citdataframe:pd.DataFrame, bins: int = 30) -> alt.Chart:
    """Plot the distribution of publications over time and the distribution of citations.

    Args:
        pubdataframe (pd.DataFrame): Dataframe containing the publication data.
        citdataframe (pd.DataFrame): Dataframe containing the citation data.
        bins (int, optional): Number of bins for the histograms. Defaults to 30.
    
    Returns:
        alt.Chart: Altair chart object.
    """

    # Create the first plot (distribution of publications over time)
    publications_plot = alt.Chart(pubdataframe).mark_bar().encode(
        alt.X('Year:O', title='Year'),
        alt.Y('Number of Publications:Q', title='Number of Publications')
    ).properties(
        title='Distribution of Publications Over Time',
        width=800,
        height=400
    )

    # Create the second plot (distribution of citations)
    citations_plot = alt.Chart(citdataframe).mark_bar().encode(
        alt.X('Number of Citations (Log Scale):Q', bin=alt.Bin(maxbins=bins), title='Number of Citations (Log Scale)'),
        alt.Y('count()', title='Number of Papers')
    ).properties(
        title='Distribution of Citations',
        width=800,
        height=400
    )

    # Display the plots side by side
    chart = alt.hconcat(publications_plot, citations_plot)

    return chart

def ts_citation_plot(dataframe: pd.DataFrame) -> alt.Chart:
    """Plot the time series of the number of citations and cumulative citations for each paper in the dataframe.

    Args:
        dataframe (pd.DataFrame): Dataframe containing the data to be plotted.

    Returns:
        alt.Chart: Altair chart object.
    """    
    # Create a selection that chooses papers based on a lower-bound threshold for the total number of citations
    lower_bound_selection = alt.selection_single(
        name='Select_total_citation_lower_bound',
        fields=['lower_bound'],
        init={'lower_bound': 0},
        bind=alt.binding_range(min=0, max=dataframe['cited_by_count_total'].max(), step=0.1)
    )

    # Create a selection that chooses papers based on an upper-bound threshold for the total number of citations
    upper_bound_selection = alt.selection_single(
        name='Select_total_citation_upper_bound',
        fields=['upper_bound'],
        init={'upper_bound': dataframe['cited_by_count_total'].max()},
        bind=alt.binding_range(min=0, max=dataframe['cited_by_count_total'].max(), step=0.1)
    )

    # Create the first line chart with scatter points (cited_by_count)
    chart1 = alt.Chart(dataframe).mark_line(point=True, opacity=0.3).encode(
        alt.X('year:O', title='Year', scale=alt.Scale(zero=False)),
        alt.Y('cited_by_count:Q', title='Number of citations (Log Scale)', scale=alt.Scale(zero=False)),
        color=alt.Color('id:N', legend=None),
        tooltip=['display_name']
    ).add_selection(
        lower_bound_selection,
        upper_bound_selection
    ).transform_filter(
        (alt.datum.cited_by_count_total >= lower_bound_selection.lower_bound) &
        (alt.datum.cited_by_count_total <= upper_bound_selection.upper_bound)
    ).properties(
        width=800,
        height=400
    )

    # Create the second line chart with scatter points (cumulative_citations)
    chart2 = alt.Chart(dataframe).mark_line(point=True, opacity=0.5).encode(
        alt.X('year:O', title='Year', scale=alt.Scale(zero=False)),
        alt.Y('cumulative_citations:Q', title='Cumulative number of citations', scale=alt.Scale(zero=False)),
        color=alt.Color('id:N', legend=None),
        tooltip=['display_name']
    ).add_selection(
        lower_bound_selection,
        upper_bound_selection
    ).transform_filter(
        (alt.datum.cited_by_count_total >= lower_bound_selection.lower_bound) &
        (alt.datum.cited_by_count_total <= upper_bound_selection.upper_bound)
    ).properties(
        width=800,
        height=400
    )

    # Horizontally concatenate the two charts
    chart = alt.hconcat(chart1, chart2)

    return chart

def ts_proportion_plot(dataframe: pd.DataFrame) -> alt.Chart:
    """Plot the time series of the proportion of citations and weighted proportion of citations for each paper in the dataframe.

    Args:
        dataframe (pd.DataFrame): Dataframe containing the data to be plotted.

    Returns:
        alt.Chart: Altair chart object.
    """

    lower_bound_selection = alt.selection_single(
        name='Select_proportion_lower_bound',
        fields=['lower_bound'],
        init={'lower_bound': 0},
        bind=alt.binding_range(name='Lower Bound', min=0, max=dataframe['proportion'].max(), step=0.005)
    )

    # Create a stacked bar chart
    chart1 = alt.Chart(dataframe).mark_bar().encode(
        alt.X('year:O', title='Year'),
        alt.Y('proportion:Q', title='Proportion', stack='normalize'),
        alt.Color('display_name:N', title='Display Name', legend=None),
        tooltip=['display_name', 'proportion']
    ).add_selection(
        lower_bound_selection
    ).transform_filter(
        alt.datum.proportion >= lower_bound_selection.lower_bound
    ).properties(
        width=800,
        height=400
    )

    # Create a stacked bar chart
    chart2 = alt.Chart(dataframe).mark_bar().encode(
        alt.X('year:O', title='Year'),
        alt.Y('weighted_proportion:Q', title='Citation Weighted Proportion', stack='normalize'),
        alt.Color('display_name:N', title='Display Name', legend=None),
        tooltip=['display_name', 'weighted_proportion']
    ).add_selection(
        lower_bound_selection
    ).transform_filter(
        alt.datum.weighted_proportion >= lower_bound_selection.lower_bound
    ).properties(
        width=800,
        height=400
    )

    # Display the chart
    chart = alt.hconcat(chart1, chart2)

    return chart

def clusters_keywords_plot(dataframe: pd.DataFrame) -> alt.Chart:
    """Plot the time series of the proportion of citations and weighted proportion of citations for each paper in the dataframe.

    Args:
        dataframe (pd.DataFrame): Dataframe containing the data to be plotted.

    Returns:
        alt.Chart: Altair chart object.
    """
    
    # Load a pre-trained transformer model
    model_name = 'distilbert-base-uncased'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Get the embedding representation of each concept entity
    concepts = dataframe.display_name.to_list()

    input_ids = tokenizer(concepts, return_tensors='pt', padding=True)['input_ids']

    with torch.no_grad():
        outputs = model(input_ids)
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()

    # Perform k-means clustering on the PCA-reduced vectors
    kmeans = KMeans(n_clusters=10, n_init='auto')
    kmeans.fit(embeddings)

    # Add the cluster labels to the data
    dataframe['cluster'] = kmeans.labels_

    # Use t-SNE to map the clusters to 2 dimensions for visualization
    tsne = TSNE(n_components=2)
    tsne_matrix = tsne.fit_transform(embeddings)

    tsne_df = pd.DataFrame(tsne_matrix, columns=['x', 'y'])
    tsne_df['cluster'] = dataframe['cluster']

    # add counts and log them
    tsne_df = pd.concat([tsne_df, dataframe[['display_name', 'count']]], axis=1)

    tsne_df['sqrt_count'] = np.sqrt(tsne_df['count'])

    # Create a scatter plot using Altair
    chart = alt.Chart(tsne_df).mark_circle().encode(
        alt.X('x', title=''),
        alt.Y('y', title=''),
        alt.Size('sqrt_count:Q', title='Count', legend=None),
        color=alt.Color('cluster:N', title='Cluster', legend=None),
        tooltip=['display_name']
    ).properties(
        title='Clusters of Concepts',
        width=1200,
        height=400
    )

    # Display the chart
    return chart

def ts_authors_plot(dataframe: pd.DataFrame, dataframe_year: pd.DataFrame) -> alt.Chart:

    # create a selection object for the author
    author_selection = alt.selection_single(
        fields=['author_name'],
        bind=alt.binding_select(options=["All"] + list(dataframe.sort_values(by="author_name")['author_name'].unique()), name="Select Author (RHS plot): "),
        init={'author_name': 'All'}
    )

    # left hand side chart
    chart1 = alt.Chart(dataframe_year).mark_bar().encode(
        alt.X('year:O', title='Year'),
        alt.Y('weighted_proportion:Q', title='weighted_proportion', stack='normalize'),
        alt.Color('author_name:N', title='Author Name', legend=None),
        tooltip=['author_name', 'weighted_proportion']
    ).properties(
        width=800,
        height=400
    )

    # create a new dataframe that aggregates the data by author
    aggdataframe = dataframe.groupby('author_name').agg(
        publications=('display_article_name', 'count'),
        total_citations=('cited_by_count', 'sum')
    ).reset_index()

    # right hand side chart
    chart2 = alt.Chart(aggdataframe).mark_point().encode(
        x=alt.X('log_publications:Q', title='Log Count of Publications'),
        y=alt.Y('log_citations:Q', title='Log Sum of Citations'),
        color=alt.Color('author_name:N', title='Author Name', legend=None),
        tooltip=['author_name'],
        size=alt.condition(author_selection, alt.value(100), alt.value(12))
    ).transform_calculate(
        log_citations='log(datum.total_citations)',
        log_publications='log(datum.publications)'
    ).add_selection(
        author_selection
    ).properties(
        width=800,
        height=400
    )

    # concatenate the two charts
    chart = alt.hconcat(chart1, chart2)

    return chart
