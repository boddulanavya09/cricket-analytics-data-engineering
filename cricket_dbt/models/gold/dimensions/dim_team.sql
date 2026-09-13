{{ config(
    materialized='table'
) }}

SELECT
    TEAM_ID,
    TEAM_NAME,
    TEAM_CODE,
    COUNTRY,
    COMPETITION,
    REGION,
    ESTABLISHED_DATE,
    STATUS
FROM {{ ref('stg_cricket_teams') }}