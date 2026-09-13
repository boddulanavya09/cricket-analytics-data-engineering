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

st.title("🏏 Cricket Analytics Dashboard")
st.markdown("### Interactive Cricket Performance Analysis")

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
            VENUE_ID,
            TEAM_A_ID,
            TEAM_B_ID,
            WINNER_TEAM_ID,
            RESULT_TYPE,
            MATCH_STATUS
        FROM CRICKET_ANALYTICS.GOLD.MATCH_SUMMARY
        ORDER BY MATCH_DATE
    """

    return pd.read_sql(query, _conn)


# =========================================================
# LOAD PLAYER DATA
# =========================================================

@st.cache_data
def load_players(_conn):

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


# =========================================================
# LOAD TEAM DATA
# =========================================================

@st.cache_data
def load_teams(_conn):

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
    """

    return pd.read_sql(query, _conn)


# =========================================================
# LOAD DELIVERY DATA
# =========================================================

@st.cache_data
def load_deliveries(_conn):

    query = """
        SELECT
            DELIVERY_ID,
            MATCH_ID,
            INNINGS_NO,
            OVER_NO,
            BALL_NO,
            BATTING_TEAM_ID,
            BOWLING_TEAM_ID,
            STRIKER_PLAYER_ID,
            NON_STRIKER_PLAYER_ID,
            BOWLER_PLAYER_ID,
            BATSMAN_RUNS,
            WIDES,
            NO_BALLS,
            BYES,
            LEG_BYES,
            TOTAL_RUNS,
            IS_WICKET,
            DISMISSAL_TYPE,
            IS_FOUR,
            IS_SIX,
            IS_DOT_BALL
        FROM CRICKET_ANALYTICS.SILVER.STG_CRICKET_DELIVERIES
    """

    return pd.read_sql(query, _conn)


matches = load_matches(conn)
players = load_players(conn)
teams = load_teams(conn)
deliveries = load_deliveries(conn)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

competition_options = ["All"] + sorted(
    matches["COMPETITION"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

format_options = ["All"] + sorted(
    matches["FORMAT"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

match_options = ["All"] + sorted(
    matches["MATCH_ID"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_competition = st.sidebar.selectbox(
    "🏆 Competition",
    competition_options
)

selected_format = st.sidebar.selectbox(
    "🏏 Format",
    format_options
)

selected_match = st.sidebar.selectbox(
    "🏏 Match",
    match_options
)


# =========================================================
# APPLY GLOBAL FILTERS
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

if selected_match != "All":

    filtered_matches = filtered_matches[
        filtered_matches["MATCH_ID"].astype(str)
        == selected_match
    ]


# =========================================================
# FOUR MAIN SECTIONS
# =========================================================

section = st.sidebar.radio(
    "📂 Select Analysis",
    [
        "🏏 Match Overview",
        "👤 Player Insights",
        "🏆 Team / Venue Analysis",
        "🔍 Ball-by-Ball Explorer"
    ]
)


# =========================================================
# 1. MATCH OVERVIEW
# =========================================================

if section == "🏏 Match Overview":

    st.header("🏏 Match Overview")

    if filtered_matches.empty:

        st.warning(
            "No matches found for the selected filters."
        )

    else:

        match_ids = filtered_matches["MATCH_ID"].tolist()

        match_deliveries = deliveries[
            deliveries["MATCH_ID"].isin(match_ids)
        ].copy()

        # -------------------------------------------------
        # INNINGS FILTER
        # -------------------------------------------------

        innings_options = ["All"]

        if not match_deliveries.empty:

            innings_options += sorted(
                match_deliveries["INNINGS_NO"]
                .dropna()
                .unique()
                .tolist()
            )

        selected_innings = st.selectbox(
            "🏏 Select Innings",
            innings_options
        )

        if selected_innings != "All":

            match_deliveries = match_deliveries[
                match_deliveries["INNINGS_NO"]
                == selected_innings
            ]

        # -------------------------------------------------
        # KPI CALCULATIONS
        # -------------------------------------------------

        total_runs = int(
            match_deliveries["TOTAL_RUNS"].sum()
        )

        wickets = int(
            match_deliveries["IS_WICKET"].sum()
        )

        balls = len(match_deliveries)

        fours = int(
            match_deliveries["IS_FOUR"].sum()
        )

        sixes = int(
            match_deliveries["IS_SIX"].sum()
        )

        boundary_runs = (
            fours * 4
            +
            sixes * 6
        )

        boundary_percentage = (
            boundary_runs * 100 / total_runs
            if total_runs > 0
            else 0
        )

        run_rate = (
            total_runs / (balls / 6)
            if balls > 0
            else 0
        )

        # -------------------------------------------------
        # KPI CARDS
        # -------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "🏏 Total Runs",
            total_runs
        )

        col2.metric(
            "📈 Run Rate",
            round(run_rate, 2)
        )

        col3.metric(
            "🎯 Wickets",
            wickets
        )

        col4.metric(
            "🔥 Boundary %",
            f"{boundary_percentage:.2f}%"
        )

        st.divider()

        # -------------------------------------------------
        # SCORE PROGRESSION
        # -------------------------------------------------

        st.subheader("📈 Score Progression")

        if not match_deliveries.empty:

            score_progression = (
                match_deliveries
                .groupby(
                    ["INNINGS_NO", "OVER_NO"]
                )["TOTAL_RUNS"]
                .sum()
                .reset_index()
            )

            score_progression[
                "CUMULATIVE_RUNS"
            ] = (
                score_progression
                .groupby("INNINGS_NO")
                ["TOTAL_RUNS"]
                .cumsum()
            )

            score_progression["INNINGS"] = (
                "Innings "
                +
                score_progression[
                    "INNINGS_NO"
                ].astype(str)
            )

            fig = px.line(
                score_progression,
                x="OVER_NO",
                y="CUMULATIVE_RUNS",
                color="INNINGS",
                markers=True,
                title="Score Progression"
            )

            fig.update_layout(
                xaxis_title="Over",
                yaxis_title="Cumulative Runs"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -------------------------------------------------
        # RUNS BY OVER
        # -------------------------------------------------

        st.subheader("📊 Runs by Over")

        over_runs = (
            match_deliveries
            .groupby("OVER_NO")
            ["TOTAL_RUNS"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            over_runs,
            x="OVER_NO",
            y="TOTAL_RUNS",
            text="TOTAL_RUNS",
            title="Runs Scored by Over"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# 2. PLAYER INSIGHTS
# =========================================================

elif section == "👤 Player Insights":

    st.header("👤 Player Insights")

    # -----------------------------------------------------
    # TOP BATTERS
    # -----------------------------------------------------

    st.subheader("🏏 Top Batters")

    batter_data = players.copy()

    batter_data["PLAYER"] = (
        batter_data["FIRST_NAME"]
        + " "
        + batter_data["LAST_NAME"]
    )

    batter_data["STRIKE_RATE"] = (
        batter_data["TOTAL_RUNS"] * 100
        /
        batter_data["BALLS_FACED"].replace(
            0,
            pd.NA
        )
    )

    batter_data["STRIKE_RATE"] = (
        batter_data["STRIKE_RATE"]
        .fillna(0)
        .round(2)
    )

    top_batters = (
        batter_data
        .sort_values(
            "TOTAL_RUNS",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_batters[
            [
                "PLAYER",
                "TOTAL_RUNS",
                "STRIKE_RATE",
                "FOURS",
                "SIXES"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        top_batters.sort_values(
            "TOTAL_RUNS"
        ),
        x="TOTAL_RUNS",
        y="PLAYER",
        orientation="h",
        text="TOTAL_RUNS",
        title="Top 10 Run Scorers"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # -----------------------------------------------------
    # TOP BOWLERS
    # -----------------------------------------------------

    st.subheader("🎯 Top Bowlers")

    bowler_data = players.copy()

    bowler_data["PLAYER"] = (
        bowler_data["FIRST_NAME"]
        + " "
        + bowler_data["LAST_NAME"]
    )

    bowler_data["ECONOMY"] = (
        bowler_data["RUNS_CONCEDED"] * 6
        /
        bowler_data["BALLS_BOWLED"].replace(
            0,
            pd.NA
        )
    )

    bowler_data["ECONOMY"] = (
        bowler_data["ECONOMY"]
        .fillna(0)
        .round(2)
    )

    top_bowlers = (
        bowler_data
        .sort_values(
            "WICKETS",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_bowlers[
            [
                "PLAYER",
                "WICKETS",
                "ECONOMY",
                "BALLS_BOWLED",
                "RUNS_CONCEDED"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        top_bowlers.sort_values(
            "WICKETS"
        ),
        x="WICKETS",
        y="PLAYER",
        orientation="h",
        text="WICKETS",
        title="Top 10 Wicket Takers"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # -----------------------------------------------------
    # PHASE-WISE ANALYSIS
    # -----------------------------------------------------

    st.subheader("⏱️ Phase-wise Analysis")

    phase_data = deliveries.copy()

    phase_data["PHASE"] = pd.cut(
        phase_data["OVER_NO"],
        bins=[-1, 5, 15, 100],
        labels=[
            "Powerplay",
            "Middle Overs",
            "Death Overs"
        ]
    )

    phase_summary = (
        phase_data
        .groupby(
            "PHASE",
            observed=False
        )
        .agg(
            RUNS=("TOTAL_RUNS", "sum"),
            WICKETS=("IS_WICKET", "sum"),
            BALLS=("DELIVERY_ID", "count")
        )
        .reset_index()
    )

    phase_summary["RUN_RATE"] = (
        phase_summary["RUNS"] * 6
        /
        phase_summary["BALLS"].replace(
            0,
            pd.NA
        )
    )

    phase_summary["RUN_RATE"] = (
        phase_summary["RUN_RATE"]
        .fillna(0)
        .round(2)
    )

    st.dataframe(
        phase_summary,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        phase_summary,
        x="PHASE",
        y="RUNS",
        text="RUNS",
        title="Runs by Match Phase"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# 3. TEAM / VENUE ANALYSIS
# =========================================================

elif section == "🏆 Team / Venue Analysis":

    st.header("🏆 Team / Venue Analysis")

    # -----------------------------------------------------
    # TEAM PERFORMANCE
    # -----------------------------------------------------

    st.subheader("🏆 Team Performance")

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
    ].sort_values(
        "WINS",
        ascending=False
    )

    st.dataframe(
        team_display,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        team_display.sort_values(
            "WIN_PERCENTAGE"
        ),
        x="WIN_PERCENTAGE",
        y="TEAM_NAME",
        orientation="h",
        text="WIN_PERCENTAGE",
        title="Team Winning Percentage"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # -----------------------------------------------------
    # PERFORMANCE BY FORMAT
    # -----------------------------------------------------

    st.subheader("🏏 Performance by Format")

    format_performance = (
        matches
        .groupby("FORMAT")
        .agg(
            MATCHES=("MATCH_ID", "nunique"),
            DECIDED_MATCHES=(
                "WINNER_TEAM_ID",
                lambda x: x.notna().sum()
            )
        )
        .reset_index()
    )

    fig = px.bar(
        format_performance,
        x="FORMAT",
        y="MATCHES",
        text="MATCHES",
        title="Matches by Format"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------------------------------
    # WINNING TRENDS
    # -----------------------------------------------------

    st.subheader("📈 Winning Trends")

    winning_matches = matches[
        matches["WINNER_TEAM_ID"].notna()
    ].copy()

    if not winning_matches.empty:

        winning_matches["MATCH_DATE"] = (
            pd.to_datetime(
                winning_matches["MATCH_DATE"]
            )
        )

        winning_trend = (
            winning_matches
            .groupby("MATCH_DATE")
            .size()
            .reset_index(
                name="DECIDED_MATCHES"
            )
        )

        fig = px.line(
            winning_trend,
            x="MATCH_DATE",
            y="DECIDED_MATCHES",
            markers=True,
            title="Winning / Decided Match Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # -----------------------------------------------------
    # VENUE ANALYSIS
    # -----------------------------------------------------

    st.subheader("📍 Venue Analysis")

    venue_data = (
        matches
        .groupby("VENUE_ID")
        .agg(
            MATCHES=("MATCH_ID", "nunique"),
            DECIDED_MATCHES=(
                "WINNER_TEAM_ID",
                lambda x: x.notna().sum()
            )
        )
        .reset_index()
    )

    venue_data = venue_data[
        venue_data["VENUE_ID"].notna()
    ]

    if not venue_data.empty:

        fig = px.bar(
            venue_data,
            x="VENUE_ID",
            y="MATCHES",
            text="MATCHES",
            title="Matches by Venue"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            venue_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Venue data is not available in the current match dataset."
        )

    st.divider()

    


# =========================================================
# 4. BALL-BY-BALL EXPLORER
# =========================================================

elif section == "🔍 Ball-by-Ball Explorer":

    st.header("🔍 Ball-by-Ball Explorer")

    explorer = deliveries.copy()

    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        match_filter = st.selectbox(
            "Match ID",
            ["All"]
            +
            sorted(
                explorer["MATCH_ID"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    with col2:

        innings_filter = st.selectbox(
            "Innings",
            ["All"]
            +
            sorted(
                explorer["INNINGS_NO"]
                .dropna()
                .unique()
                .tolist()
            )
        )

    with col3:

        over_filter = st.selectbox(
            "Over",
            ["All"]
            +
            sorted(
                explorer["OVER_NO"]
                .dropna()
                .unique()
                .tolist()
            )
        )

    with col4:

        wicket_filter = st.selectbox(
            "Wicket",
            [
                "All",
                "Wicket",
                "No Wicket"
            ]
        )

    # -----------------------------------------------------
    # APPLY FILTERS
    # -----------------------------------------------------

    if match_filter != "All":

        explorer = explorer[
            explorer["MATCH_ID"].astype(str)
            == match_filter
        ]

    if innings_filter != "All":

        explorer = explorer[
            explorer["INNINGS_NO"]
            == innings_filter
        ]

    if over_filter != "All":

        explorer = explorer[
            explorer["OVER_NO"]
            == over_filter
        ]

    if wicket_filter == "Wicket":

        explorer = explorer[
            explorer["IS_WICKET"] == 1
        ]

    elif wicket_filter == "No Wicket":

        explorer = explorer[
            explorer["IS_WICKET"] == 0
        ]

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Deliveries",
        len(explorer)
    )

    c2.metric(
        "Runs",
        int(explorer["TOTAL_RUNS"].sum())
    )

    c3.metric(
        "Wickets",
        int(explorer["IS_WICKET"].sum())
    )

    st.divider()

    # -----------------------------------------------------
    # BALL-BY-BALL TABLE
    # -----------------------------------------------------

    st.subheader("📋 Delivery Details")

    display_columns = [
        "DELIVERY_ID",
        "MATCH_ID",
        "INNINGS_NO",
        "OVER_NO",
        "BALL_NO",
        "BATTING_TEAM_ID",
        "BOWLING_TEAM_ID",
        "STRIKER_PLAYER_ID",
        "BOWLER_PLAYER_ID",
        "BATSMAN_RUNS",
        "WIDES",
        "NO_BALLS",
        "TOTAL_RUNS",
        "IS_WICKET",
        "DISMISSAL_TYPE",
        "IS_FOUR",
        "IS_SIX",
        "IS_DOT_BALL"
    ]

    st.dataframe(
        explorer[display_columns],
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # EXPORT
    # -----------------------------------------------------

    csv_data = explorer[
        display_columns
    ].to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Export Filtered Data",
        data=csv_data,
        file_name="cricket_ball_by_ball.csv",
        mime="text/csv"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.success(
    "✅ Cricket Analytics Dashboard loaded successfully!"
)

st.caption(
    "Snowflake + dbt + Airflow + Python + Streamlit + Plotly"
)
