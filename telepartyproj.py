import pandas as pd
import sqlite3
from tabulate import tabulate

# Loading and cleaning CSV files
ep_df = pd.read_csv("all-episode-ratings.csv")
series_df = pd.read_csv("all-series-ep-average.csv")
top_seasons_df = pd.read_csv("top-seasons-full.csv")

# Renaming and cleaning columns
ep_df.columns = ['id_code', 'season', 'episode', 'rating', 'code']
ep_df = ep_df[['code', 'season', 'episode', 'rating']]

series_df.columns = ['code', 'title', 'rating', 'rating_count', 'rank', 'rating_mean']
series_df['rating_count'] = series_df['rating_count'].replace(',', '', regex=True).astype(int)
series_df['rank'] = series_df['rank'].astype(int)
series_df['rating'] = series_df['rating'].astype(float)
series_df['rating_mean'] = series_df['rating_mean'].astype(float)

top_seasons_df.columns = ['code', 'title', 'season', 'rating_mean', 'number_of_episodes']

# Creating in-memory SQLite DB
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Creating tables with composite primary keys manually
cursor.executescript("""
CREATE TABLE series_summary (
  code TEXT PRIMARY KEY,
  title TEXT,
  rating FLOAT,
  rating_count INTEGER,
  rank INTEGER,
  rating_mean FLOAT
);

CREATE TABLE episode_ratings (
  code TEXT,
  season INTEGER,
  episode INTEGER,
  rating FLOAT,
  PRIMARY KEY (code, season, episode),
  FOREIGN KEY (code) REFERENCES series_summary(code)
);

CREATE TABLE top_seasons (
  code TEXT,
  season INTEGER,
  title TEXT,
  rating_mean FLOAT,
  number_of_episodes INTEGER,
  PRIMARY KEY (code, season),
  FOREIGN KEY (code) REFERENCES series_summary(code)
);
""")

# Loading data into manually created tables
ep_df.to_sql("episode_ratings", conn, index=False, if_exists='replace')
series_df.to_sql("series_summary", conn, index=False, if_exists='replace')
top_seasons_df.to_sql("top_seasons", conn, index=False, if_exists='replace')

# Helper to run SQL , print 1-indexed results & Using Tabulate for printing pretty tables
def print_query(title, query):
    df = pd.read_sql_query(query, conn)
    df.index += 1
    print(f"\n {title}")
    if df.empty:
        print("No results found.\n")
    else:
        print(tabulate(df, headers="keys", tablefmt="fancy_grid"))

#  QUERY 1 [Display all shows (include the show title) with a rating less than or equal to 5
#              - Which shows from this data had more than 1 season] 
# Option 1: Episode-based rating <= 5
print_query("1-OPTION 1: Table with Ratings-Shows with ANY episode rated ≤ 5", """
SELECT DISTINCT s.code, s.title, e.season, e.episode, e.rating
FROM episode_ratings e
JOIN series_summary s ON e.code = s.code
WHERE e.rating <= 5;
""")

print_query("1-OPTION 1: Table without Ratings-Shows with ANY episode rated ≤ 5", """
SELECT DISTINCT s.code, s.title
FROM episode_ratings e
JOIN series_summary s ON e.code = s.code
WHERE e.rating <= 5;
""")

# Subquery: Option 1 + more than 1 season
print_query("1-a.Shows with episode ≤ 5 AND more than 1 season", """
SELECT s.code, s.title, MIN(e.rating) AS lowest_rating
FROM episode_ratings e
JOIN series_summary s ON e.code = s.code
WHERE e.rating <= 5
GROUP BY s.code
HAVING COUNT(DISTINCT e.season) > 1;
""")

# Option 2: Series-based overall rating <= 5
print_query("1-OPTION 2: Shows with SERIES rating ≤ 5", """
SELECT code, title, rating
FROM series_summary
WHERE rating <= 5;
""")

# Subquery: Option 2 + more than 1 season
print_query("1-b.Shows with series rating ≤ 5 AND more than 1 season", """
SELECT s.code, s.title, s.rating
FROM series_summary s
WHERE s.rating <= 5
  AND s.code IN (
    SELECT code
    FROM episode_ratings
    GROUP BY code
    HAVING COUNT(DISTINCT season) > 1
  );
""")

# Option 3: Series rating_mean ≤ 5 
print_query("1-OPTION 3: Shows with average episode rating (rating_mean) ≤ 5", """
SELECT code, title, rating_mean
FROM series_summary
WHERE rating_mean <= 5;
""")

# Subquery: Option 3 + more than 1 season
print_query("1-c.Shows with rating_mean ≤ 5 AND more than 1 season", """
SELECT s.code, s.title, s.rating_mean
FROM series_summary s
WHERE s.rating_mean <= 5
  AND s.code IN (
    SELECT code
    FROM episode_ratings
    GROUP BY code
    HAVING COUNT(DISTINCT season) > 1
  );
""")
#   QUERY 2 Display the show(s) that have the highest rating count and the lowest rank
#                 - How many episodes do these shows have?
#                 - How many seasons do these shows have?
# Highest rating count & the lowest rank
print_query("2-i)Show with HIGHEST rating count & the LOWEST rank","""
SELECT title, rating_count, rank
FROM series_summary
WHERE rating_count = (SELECT MAX(rating_count) FROM series_summary)
  AND rank = (SELECT MIN(rank) FROM series_summary);
""")

# Episodes and seasons for the above
print_query("2-ii) Episode & Season count for HIGHEST rating & LOWEST rank shows", """
SELECT s.title, COUNT(e.episode) AS total_episodes, COUNT(DISTINCT e.season) AS total_seasons
FROM episode_ratings e
JOIN series_summary s ON e.code = s.code
WHERE s.rating_count = (SELECT MAX(rating_count) FROM series_summary)
  AND s.rank = (SELECT MIN(rank) FROM series_summary)
GROUP BY s.code;

""")

# QUERY 3 Display the show(s) that have the lowest rating count and the highest rank
#             - How many episodes do these shows have?
#             - How many seasons do these shows have?
# Lowest rating count and the highest rank
print_query("3-i)Show with LOWEST rating count & the HIGHEST rank", """
SELECT s.title, COUNT(e.episode) AS total_episodes, COUNT(DISTINCT e.season) AS total_seasons
FROM episode_ratings e
JOIN series_summary s ON e.code = s.code
WHERE s.rating_count = (SELECT MIN(rating_count) FROM series_summary)
  AND s.rank = (SELECT MAX(rank) FROM series_summary)
GROUP BY s.code;

""")

# Episodes and seasons for the above
print_query("3-ii) Episode & Season count for LOWEST rating & HIGHEST rank shows", """
SELECT s.title, COUNT(e.episode) AS total_episodes, COUNT(DISTINCT e.season) AS total_seasons
FROM episode_ratings e
JOIN series_summary s ON e.code = s.code
WHERE s.rating_count = (SELECT MIN(rating_count) FROM series_summary)
  AND s.rank = (SELECT MAX(rank) FROM series_summary)
GROUP BY s.code;

""")

