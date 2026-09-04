WITH team_matches AS (

    SELECT
        TEAM_A_ID AS TEAM_ID,
        MATCH_ID,
        TOSS_WINNER_TEAM_ID,
        WINNER_TEAM_ID,
        RESULT_TYPE,
        MATCH_STATUS
    FROM {{ ref('match_summary') }}

    UNION ALL

    SELECT
        TEAM_B_ID AS TEAM_ID,
        MATCH_ID,
        TOSS_WINNER_TEAM_ID,
        WINNER_TEAM_ID,
        RESULT_TYPE,
        MATCH_STATUS
    FROM {{ ref('match_summary') }}

),

team_stats AS (

    SELECT
        TEAM_ID,

        COUNT(DISTINCT MATCH_ID) AS MATCHES_PLAYED,

        COUNT(DISTINCT CASE
            WHEN WINNER_TEAM_ID = TEAM_ID
            THEN MATCH_ID
        END) AS WINS,

        COUNT(DISTINCT CASE
            WHEN WINNER_TEAM_ID IS NOT NULL
                 AND WINNER_TEAM_ID <> TEAM_ID
            THEN MATCH_ID
        END) AS LOSSES,

        COUNT(DISTINCT CASE
            WHEN TOSS_WINNER_TEAM_ID = TEAM_ID
            THEN MATCH_ID
        END) AS TOSS_WINS,

        COUNT(DISTINCT CASE
            WHEN WINNER_TEAM_ID IS NULL
                 AND MATCH_STATUS = 'COMPLETED'
            THEN MATCH_ID
        END) AS NO_RESULTS

    FROM team_matches

    GROUP BY TEAM_ID

)

SELECT
    t.TEAM_ID,
    t.TEAM_NAME,
    t.TEAM_CODE,
    t.COUNTRY,
    t.COMPETITION,
    t.REGION,
    t.ESTABLISHED_DATE,
    t.STATUS,

    COALESCE(s.MATCHES_PLAYED, 0) AS MATCHES_PLAYED,
    COALESCE(s.WINS, 0) AS WINS,
    COALESCE(s.LOSSES, 0) AS LOSSES,
    COALESCE(s.TOSS_WINS, 0) AS TOSS_WINS,
    COALESCE(s.NO_RESULTS, 0) AS NO_RESULTS,

    CASE
        WHEN COALESCE(s.MATCHES_PLAYED, 0) > 0
        THEN ROUND(
            (COALESCE(s.WINS, 0) * 100.0)
            / s.MATCHES_PLAYED,
            2
        )
        ELSE 0
    END AS WIN_PERCENTAGE

FROM {{ ref('stg_cricket_teams') }} t

LEFT JOIN team_stats s
    ON t.TEAM_ID = s.TEAM_ID