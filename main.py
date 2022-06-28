import pandas as pd
import streamlit as st
import altair as alt


def clean_dataset(df: pd.DataFrame):
    df = df.replace([".", "..", "..."], "0").replace(",", "", regex=True)

    return df


def get_dataset_without_totals(df: pd.DataFrame):
    return df.drop(df.columns[1], axis=1)


def build_st_query_for_line_charts(df: pd.DataFrame, header_title: str):
    name_list = df[df.columns[0]].unique().tolist()
    names = st.multiselect(f"Select {header_title}", name_list)

    return (name_list, names)


def build_st_query_for_bar_charts(df: pd.DataFrame, header_title: str, fake_value: str):
    st.subheader('Compare most popular names by year')
    years_list = df.columns.unique().tolist()[1:]
    selected_years = st.selectbox(f"Select {header_title}", [fake_value] + years_list)

    return (years_list, selected_years)


def filter_df_by_selected_values(
    df: pd.DataFrame, header_title: str, all_names: list[str], selected_names: list[str]
):
    df_by_selected_names = df[df[df.columns[0]].isin(list(selected_names))]

    df_to_show = df_by_selected_names.drop(df_by_selected_names.columns[0], axis=1)
    df_to_show = df_to_show.T

    df_to_show.index = pd.DatetimeIndex(df_to_show.index).year
    df_to_show = df_to_show.astype("int32")

    selected_names_as_set = set(selected_names)

    df_to_show.columns = [
        f"{x} ({header_title})" for x in all_names if x in selected_names_as_set
    ]

    return df_to_show


jewish_boys_header = "בן יהודי"
jewish_girls_header = "בת יהודיה"
muslim_boys_header = "בן מוסלמי"
muslim_girls_header = "בת מוסלמית"

original_jewish_boys = clean_dataset(pd.read_csv("boys.csv"))
original_jewish_girls = clean_dataset(pd.read_csv("girls.csv"))
original_muslim_boys = clean_dataset(pd.read_csv("muslim_boys.csv"))
original_muslim_girls = clean_dataset(pd.read_csv("muslim_girls.csv"))

jewish_boys = get_dataset_without_totals(original_jewish_boys)
jewish_girls = get_dataset_without_totals(original_jewish_girls)
muslim_boys = get_dataset_without_totals(original_muslim_boys)
muslim_girls = get_dataset_without_totals(original_muslim_girls)


def build_line_charts_for_datasets():
    st.subheader('Comparison of Jewish & Muslim (boys and girls) names over the years')

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        all_jewish_boys, selected_jewish_boys = build_st_query_for_line_charts(
            jewish_boys, jewish_boys_header
        )

    with col2:
        all_jewish_girls, selected_jewish_girls = build_st_query_for_line_charts(
            jewish_girls, jewish_girls_header
        )

    with col3:
        all_muslim_boys, selected_muslim_boys = build_st_query_for_line_charts(
            muslim_boys, muslim_boys_header
        )

    with col4:
        all_muslim_girls, selected_muslim_girls = build_st_query_for_line_charts(
            muslim_girls, muslim_girls_header
        )

    all_selected_names = (
        selected_jewish_boys
        + selected_jewish_girls
        + selected_muslim_boys
        + selected_muslim_girls
    )

    if all_selected_names:

        jewish_boys_filtered_df = filter_df_by_selected_values(
            jewish_boys, jewish_boys_header, all_jewish_boys, selected_jewish_boys
        )
        jewish_girls_filtered_df = filter_df_by_selected_values(
            jewish_girls, jewish_girls_header, all_jewish_girls, selected_jewish_girls
        )
        muslim_boys_filtered_df = filter_df_by_selected_values(
            muslim_boys, muslim_boys_header, all_muslim_boys, selected_muslim_boys
        )
        muslim_girls_filtered_df = filter_df_by_selected_values(
            muslim_girls, muslim_girls_header, all_muslim_girls, selected_muslim_girls
        )

        dfs_to_merge = [
            jewish_boys_filtered_df,
            jewish_girls_filtered_df,
            muslim_boys_filtered_df,
            muslim_girls_filtered_df,
        ]

        combined_df = pd.concat(df.T for df in dfs_to_merge).T

        st.line_chart(combined_df, use_container_width=True)


def build_bar_charts_for_datasets():
    fake_value = "choose a year..."

    # Arbitrarily choose one of the DFs to extract possible years.
    years_list, selected_year = build_st_query_for_bar_charts(
        jewish_boys, "year of birth", fake_value
    )

    def get_df_of_largest_values(df: pd.DataFrame, header: str, graph_number: int):
        df_by_selected_year = df[[df.columns[0], selected_year]]
        df_by_selected_year.columns = [df_by_selected_year.columns[0], "count"]
        df_by_selected_year = df_by_selected_year.set_index(
            df_by_selected_year.columns[0], drop=False
        )

        df_by_selected_year.index = df_by_selected_year.index.map(
            lambda idx: f"{idx} ({header})"
        )

        df_by_selected_year = df_by_selected_year.astype({"count": "int64"})
        df_by_selected_year = df_by_selected_year.nlargest(5, "count")

        if graph_number % 2 == 0:
            df_by_selected_year = df_by_selected_year.sort_values(
                by="count", ascending=True
            )
        else:
            df_by_selected_year = df_by_selected_year.sort_values(
                by="count", ascending=False
            )

        graph_number += 1


        return df_by_selected_year

    if selected_year != fake_value:
        graph_number = 0

        jewish_boys_most_popular = get_df_of_largest_values(
            jewish_boys, "בנים יהודים", graph_number
        )
        jewish_boys_most_popular["type"] = "בנים יהודים"
        graph_number += 1

        jewish_girls_most_popular = get_df_of_largest_values(
            jewish_girls, "בנות יהודים", graph_number
        )
        jewish_girls_most_popular["type"] = "בנות יהודיות"
        graph_number += 1

        chart1 = (
            alt.Chart(pd.concat([jewish_boys_most_popular, jewish_girls_most_popular]))
            .mark_bar()
            .encode(
                x=alt.X("שם פרטי", sort=None),
                y=alt.Y("count", sort=None),
                color="type",
                tooltip=["שם פרטי", "type", "count"],
            )
        )

        muslim_boys_most_popular = get_df_of_largest_values(
            muslim_boys, "בנים מוסלמים", graph_number
        )
        muslim_boys_most_popular["type"] = "בנים מוסלמים"
        graph_number += 1

        muslim_girls_most_popular = get_df_of_largest_values(
            muslim_girls, "בנות מוסלמיות", graph_number
        )
        muslim_girls_most_popular["type"] = "בנות מוסלמיות"
        graph_number += 1

        chart2 = (
            alt.Chart(pd.concat([muslim_boys_most_popular, muslim_girls_most_popular]))
            .mark_bar()
            .encode(
                x=alt.X("שם פרטי", sort=None),
                y=alt.Y("count", sort=None),
                color="type",
                tooltip=["שם פרטי", "type", "count"],
            )
        )

        st.altair_chart(chart1 | chart2)


def build_scatterplot_for_datasets():
    def build_common_df(df1: pd.DataFrame, df2: pd.DataFrame):
        df1_total = df1[[df1.columns[0], df1.columns[1]]]
        df1_total.columns = [df1_total.columns[0], "total"]
        df1_total = df1_total.astype({"total": "int64"})
        df1_total = df1_total.set_index(df1_total.columns[0])

        df2_total = df2[[df2.columns[0], df2.columns[1]]]
        df2_total.columns = [df2_total.columns[0], "total"]
        df2_total = df2_total.astype({"total": "int64"})
        df2_total = df2_total.set_index(df2_total.columns[0])

        combined_data = {}

        for index_item in df1_total.index:
            if index_item in df2_total.index:
                combined_data.update(
                    {
                        index_item: (
                            index_item,
                            df1_total.loc[index_item].values[0],
                            df2_total.loc[index_item].values[0],
                        )
                    }
                )

        final_df = pd.DataFrame(combined_data).T
        final_df.columns = ["name", "total boys", "total girls"]

        return final_df

    jewish_df = build_common_df(original_jewish_boys, original_jewish_girls)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Comparison of common names for jewish boys and girls")
        st.write(
            alt.Chart(jewish_df)
            .mark_point()
            .encode(
                x=jewish_df.columns[1],
                y=jewish_df.columns[2],
                tooltip=[
                    jewish_df.columns[0],
                    jewish_df.columns[1],
                    jewish_df.columns[2],
                ],
            )
            .interactive()
        )

        muslim_df = build_common_df(original_muslim_boys, original_muslim_girls)

    with col2:
        st.subheader("Comparison of common names for muslim boys and girls")
        st.write(
            alt.Chart(muslim_df)
            .mark_point()
            .encode(
                x=muslim_df.columns[1],
                y=muslim_df.columns[2],
                tooltip=[
                    muslim_df.columns[0],
                    muslim_df.columns[1],
                    muslim_df.columns[2],
                ],
            )
            .interactive()
        )

st.title('Visualization of information - Final Project')
build_line_charts_for_datasets()
build_bar_charts_for_datasets()
build_scatterplot_for_datasets()
