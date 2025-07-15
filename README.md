# Viewership-SQL
This project solves a SQL-based data engineering challenge using Python and SQLite. It analyzes three datasets containing episode ratings, series summaries, and top-rated seasons. The goal is to ingest the data into a relational database, perform SQL queries, and generate clean reports.

---

## 🗂️ Project Structure

```
📁 Teleparty-Project
├── all-episode-ratings.csv
├── all-series-ep-average.csv
├── top-seasons-full.csv
├── telepartyproj.py       # Main executable script
├── README.md              # This file
```

---

## 🛠️ Tools Used

- Python 3
- SQLite3 (in-memory DB)
- Pandas
- Tabulate (for terminal output)
- Mermaid.js (for diagrams)

---

## 📥 Data Ingestion

All 3 CSV files are loaded into in-memory SQLite tables:

- `episode_ratings`
- `series_summary`
- `top_seasons`

These tables are used for running real SQL queries.

---

## ⚙️ Queries Answered

### ✅ Query 1: Display all shows with rating ≤ 5
- Option 1: Episode-based (any episode ≤ 5)
- Option 2: Series-based (overall rating ≤ 5)
- Option 3: Average rating (rating_mean ≤ 5)
- Subquery: Shows from each option with > 1 season

### ✅ Query 2: Show with highest rating count and lowest rank
- Also includes total episodes & seasons

### ✅ Query 3: Show with lowest rating count and highest rank
- Also includes total episodes & seasons

---

## 🔍 Example Output (Terminal)

```
📊 1️⃣ OPTION 1: Shows with ANY episode rated ≤ 5
╒════╤═══════════╤════════════════════╕
│ No │ code      │ title              │
╞════╪═══════════╪════════════════════╡
│  1 │ tt1234567 │ Dexter             │
│  2 │ tt2345678 │ Top Gear           │
╘════╧═══════════╧════════════════════╛
```

---

## 📊 System Architecture (Mermaid Diagram)

```mermaid
graph TD
    A[CSV Files] --> B[(SQLite DB)]
    B --> C[episode_ratings]
    B --> D[series_summary]
    B --> E[top_seasons]
    C & D --> F[SQL Query Layer]
    F --> G[DataFrame Results]
    G --> H[Formatted Reports using Tabulate]
```

---

## 🚀 How to Run

```bash
pip install pandas tabulate
python3 telepartyproj.py
```

---

## 👤 Author
Sreethi Reddy

---

## 📄 License
This project is part of an academic coding challenge and is intended for learning purposes.
