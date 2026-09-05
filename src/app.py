import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Cricket Analytics Dashboard",
    page_icon="🏏",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🏏 Cricket Analytics Dashboard")

st.markdown(
    "### Interactive Cricket Performance Analysis"
)

st.divider()


# =========================================================
# SNOWFLAKE CONNECTION
# =========================================================

@st.cache_resource
def create_connection():

    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database="CRICKET_ANALYTICS",
        schema="GOLD"
    )


conn = create_connection()


# =========================================================
# LOAD MATCH DATA
# =========================================================

@st.cache_data
def load_matches(_conn):

    query = """
        SELECT
            MATCH_ID,
            COMPETITION,
            FORMAT,
            MATCH_DATE,
            TEAM_A_ID,
            TEAM_B_ID,
            WINNER_TEAM_ID,
            RESULT_TYPE,
            MATCH_STATUS
        FROM CRICKET_ANALYTICS.GOLD.MATCH_SUMMARY
        ORDER BY MATCH_DATE
    """

    return pd.read_sql(query, _conn)


matches = load_matches(conn)


# =========================================================
# LOAD TEAM ANALYTICS
# =========================================================

@st.cache_data
def load_team_analytics(_conn):

    query = """
        SELECT
            TEAM_ID,
            TEAM_NAME,
            TEAM_CODE,
            COUNTRY,
            COMPETITION,
            REGION,
            MATCHES_PLAYED,
            WINS,
            LOSSES,
            TOSS_WINS,
            NO_RESULTS,
            WIN_PERCENTAGE
        FROM CRICKET_ANALYTICS.GOLD.TEAM_ANALYTICS
        ORDER BY WINS DESC
    """

    return pd.read_sql(query, _conn)


teams = load_team_analytics(conn)


# =========================================================
# LOAD PLAYER ANALYTICS
# =========================================================

@st.cache_data
def load_player_analytics(_conn):

    query = """
        SELECT
            PLAYER_ID,
            FIRST_NAME,
            LAST_NAME,
            NATIONALITY,
            ROLE,
            TOTAL_RUNS,
            FOURS,
            SIXES,
            WICKETS,
            BALLS_FACED,
            BALLS_BOWLED,
            RUNS_CONCEDED,
            BATTING_MATCHES,
            BOWLING_MATCHES
        FROM CRICKET_ANALYTICS.GOLD.PLAYER_ANALYTICS
    """

    return pd.read_sql(query, _conn)


players = load_player_analytics(conn)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")


competitions = ["All"]

if "COMPETITION" in matches.columns:

    competitions += sorted(
        matches["COMPETITION"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


formats = ["All"]

if "FORMAT" in matches.columns:

    formats += sorted(
        matches["FORMAT"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


selected_competition = st.sidebar.selectbox(
    "🏆 Competition",
    competitions
)


selected_format = st.sidebar.selectbox(
    "🏏 Format",
    formats
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_matches = matches.copy()


if selected_competition != "All":

    filtered_matches = filtered_matches[
        filtered_matches["COMPETITION"]
        == selected_competition
    ]


if selected_format != "All":

    filtered_matches = filtered_matches[
        filtered_matches["FORMAT"]
        == selected_format
    ]


# =========================================================
# KPI SECTION
# =========================================================

st.subheader("📊 Overview")


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "🏏 Total Matches",
    len(filtered_matches)
)


col2.metric(
    "✅ Completed Matches",
    len(
        filtered_matches[
            filtered_matches["MATCH_STATUS"]
            == "COMPLETED"
        ]
    )
)


col3.metric(
    "🏆 Matches With Winner",
    filtered_matches[
        "WINNER_TEAM_ID"
    ].notna().sum()
)


col4.metric(
    "📅 Competitions",
    filtered_matches[
        "COMPETITION"
    ].nunique()
)


st.divider()


# =========================================================
# MATCH DETAILS
# =========================================================

st.subheader("🏏 Match Details")


if not filtered_matches.empty:

    st.dataframe(
        filtered_matches,
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning("No matches found for the selected filters.")


st.divider()


# =========================================================
# CHART ROW 1
# =========================================================

st.subheader("📊 Match Distribution")


chart_col1, chart_col2 = st.columns(2)


# ---------------------------------------------------------
# MATCHES BY COMPETITION
# ---------------------------------------------------------

with chart_col1:

    competition_counts = (
        filtered_matches
        .groupby("COMPETITION")
        .size()
        .reset_index(name="MATCHES")
    )


    if not competition_counts.empty:

        fig = px.bar(
            competition_counts,
            x="COMPETITION",
            y="MATCHES",
            text="MATCHES",
            title="Matches by Competition"
        )

        fig.update_layout(
            xaxis_title="Competition",
            yaxis_title="Number of Matches"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ---------------------------------------------------------
# MATCHES BY FORMAT
# ---------------------------------------------------------

with chart_col2:

    format_counts = (
        filtered_matches
        .groupby("FORMAT")
        .size()
        .reset_index(name="MATCHES")
    )


    if not format_counts.empty:

        fig = px.bar(
            format_counts,
            x="FORMAT",
            y="MATCHES",
            text="MATCHES",
            title="Matches by Format"
        )

        fig.update_layout(
            xaxis_title="Format",
            yaxis_title="Number of Matches"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# PIE CHARTS
# =========================================================

st.subheader("🥧 Match Distribution – Pie Charts")


pie_col1, pie_col2 = st.columns(2)


# ---------------------------------------------------------
# COMPETITION PIE CHART
# ---------------------------------------------------------

with pie_col1:

    competition_pie = (
        filtered_matches
        .groupby("COMPETITION")
        .size()
        .reset_index(name="MATCHES")
    )


    if not competition_pie.empty:

        fig = px.pie(
            competition_pie,
            names="COMPETITION",
            values="MATCHES",
            hole=0.35,
            title="Matches by Competition"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ---------------------------------------------------------
# FORMAT PIE CHART
# ---------------------------------------------------------

with pie_col2:

    format_pie = (
        filtered_matches
        .groupby("FORMAT")
        .size()
        .reset_index(name="MATCHES")
    )


    if not format_pie.empty:

        fig = px.pie(
            format_pie,
            names="FORMAT",
            values="MATCHES",
            hole=0.35,
            title="Matches by Format"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


st.divider()


# =========================================================
# MATCH TREND
# =========================================================

st.subheader("📈 Match Trend Analysis")


if not filtered_matches.empty:

    trend_data = (
        filtered_matches
        .copy()
    )


    trend_data["MATCH_DATE"] = pd.to_datetime(
        trend_data["MATCH_DATE"]
    )


    trend_data = (
        trend_data
        .groupby("MATCH_DATE")
        .size()
        .reset_index(name="MATCHES")
    )


    fig = px.line(
        trend_data,
        x="MATCH_DATE",
        y="MATCHES",
        markers=True,
        title="Matches Played Over Time"
    )


    fig.update_layout(
        xaxis_title="Match Date",
        yaxis_title="Number of Matches"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.divider()


# =========================================================
# TEAM PERFORMANCE
# =========================================================

st.subheader("🏆 Team Performance")


if not teams.empty:

    team_display = teams[
        [
            "TEAM_NAME",
            "TEAM_CODE",
            "COUNTRY",
            "MATCHES_PLAYED",
            "WINS",
            "LOSSES",
            "TOSS_WINS",
            "NO_RESULTS",
            "WIN_PERCENTAGE"
        ]
    ].copy()


    team_display = team_display.sort_values(
        "WINS",
        ascending=False
    )


    st.dataframe(
        team_display,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# =========================================================
# TEAM WIN/LOSS PIE CHART
# =========================================================

st.subheader("🥧 Overall Team Results")


if not teams.empty:

    total_wins = teams["WINS"].sum()

    total_losses = teams["LOSSES"].sum()

    total_no_results = teams["NO_RESULTS"].sum()


    result_data = pd.DataFrame(
        {
            "RESULT": [
                "Wins",
                "Losses",
                "No Results"
            ],
            "COUNT": [
                total_wins,
                total_losses,
                total_no_results
            ]
        }
    )


    result_data = result_data[
        result_data["COUNT"] > 0
    ]


    if not result_data.empty:

        fig = px.pie(
            result_data,
            names="RESULT",
            values="COUNT",
            hole=0.4,
            title="Wins vs Losses vs No Results"
        )


        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


st.divider()


# =========================================================
# TOP RUN SCORERS
# =========================================================

st.subheader("🏏 Top Run Scorers")


if not players.empty:

    top_runs = (
        players[
            [
                "PLAYER_ID",
                "FIRST_NAME",
                "LAST_NAME",
                "NATIONALITY",
                "ROLE",
                "TOTAL_RUNS",
                "FOURS",
                "SIXES"
            ]
        ]
        .sort_values(
            "TOTAL_RUNS",
            ascending=False
        )
        .head(10)
    )


    st.dataframe(
        top_runs,
        use_container_width=True,
        hide_index=True
    )


    fig = px.bar(
        top_runs.sort_values("TOTAL_RUNS"),
        x="TOTAL_RUNS",
        y="LAST_NAME",
        orientation="h",
        text="TOTAL_RUNS",
        title="Top 10 Run Scorers"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.divider()


# =========================================================
# TOP WICKET TAKERS
# =========================================================

st.subheader("🎯 Top Wicket Takers")


if not players.empty:

    top_wickets = (
        players[
            [
                "PLAYER_ID",
                "FIRST_NAME",
                "LAST_NAME",
                "NATIONALITY",
                "ROLE",
                "WICKETS",
                "BALLS_BOWLED",
                "RUNS_CONCEDED"
            ]
        ]
        .sort_values(
            "WICKETS",
            ascending=False
        )
        .head(10)
    )


    st.dataframe(
        top_wickets,
        use_container_width=True,
        hide_index=True
    )


    fig = px.bar(
        top_wickets.sort_values("WICKETS"),
        x="WICKETS",
        y="LAST_NAME",
        orientation="h",
        text="WICKETS",
        title="Top 10 Wicket Takers"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.divider()


# =========================================================
# PLAYER RUNS VS WICKETS
# =========================================================

st.subheader("📊 Player Performance Comparison")


if not players.empty:

    comparison = players[
        [
            "FIRST_NAME",
            "LAST_NAME",
            "TOTAL_RUNS",
            "WICKETS"
        ]
    ].copy()


    comparison["PLAYER"] = (
        comparison["FIRST_NAME"]
        + " "
        + comparison["LAST_NAME"]
    )


    fig = px.scatter(
        comparison,
        x="TOTAL_RUNS",
        y="WICKETS",
        hover_name="PLAYER",
        size="TOTAL_RUNS",
        title="Runs vs Wickets"
    )


    fig.update_layout(
        xaxis_title="Total Runs",
        yaxis_title="Total Wickets"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.divider()


# =========================================================
# BATTING INTENSITY HEATMAP
# =========================================================

st.subheader("🔥 Batting Intensity Heatmap")


@st.cache_data
def load_deliveries(_conn):

    query = """
        SELECT
            MATCH_ID,
            INNINGS_NO,
            OVER_NO,
            BATSMAN_RUNS,
            TOTAL_RUNS,
            IS_FOUR,
            IS_SIX
        FROM CRICKET_ANALYTICS.SILVER.STG_CRICKET_DELIVERIES
    """

    return pd.read_sql(query, _conn)


deliveries = load_deliveries(conn)


if not deliveries.empty:

    heatmap_data = (
        deliveries
        .groupby(
            ["INNINGS_NO", "OVER_NO"]
        )["TOTAL_RUNS"]
        .sum()
        .reset_index()
    )


    fig = px.density_heatmap(
        heatmap_data,
        x="OVER_NO",
        y="INNINGS_NO",
        z="TOTAL_RUNS",
        text_auto=True,
        title="Runs Scored by Over and Innings",
        labels={
            "OVER_NO": "Over",
            "INNINGS_NO": "Innings",
            "TOTAL_RUNS": "Runs"
        }
    )


    fig.update_layout(
        height=550
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.caption(
        "Higher values indicate greater scoring intensity."
    )


st.divider()


# =========================================================
# RECENT MATCHES
# =========================================================

st.subheader("🕐 Recent Matches")


if not filtered_matches.empty:

    recent_matches = (
        filtered_matches
        .sort_values(
            "MATCH_DATE",
            ascending=False
        )
        .head(10)
    )


    st.dataframe(
        recent_matches,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# =========================================================
# FOOTER
# =========================================================

st.success(
    "✅ Cricket Analytics Dashboard loaded successfully! 🏏"
)

st.caption(
    "Built using Snowflake + dbt + Streamlit + Python + Plotly"
)