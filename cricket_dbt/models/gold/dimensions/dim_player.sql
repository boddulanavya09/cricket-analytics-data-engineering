{{ config(
    materialized='table'
) }}

SELECT
    PLAYER_ID,
    FIRST_NAME,
    LAST_NAME,
    NATIONALITY,
    BATTING_STYLE,
    BOWLING_STYLE,
    ROLE,
    CURRENT_TEAM_ID,
    CONTRACT_START,
    STATUS,
    UPDATED_AT
FROM {{ ref('stg_cricket_players') }}