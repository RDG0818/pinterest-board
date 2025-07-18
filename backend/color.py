import sqlite3
import json

DATABASE_FILE = "backend/fantasy_board.db"

def extract_first_dominant_colors():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT dominant_colors FROM images WHERE dominant_colors IS NOT NULL"
    cursor.execute(query)

    unique_colors = set()

    for row in cursor.fetchall():
        raw = row['dominant_colors']

        # Try to parse JSON first
        try:
            color_list = json.loads(raw)
            if isinstance(color_list, list) and color_list:
                first_color = color_list[0].strip()
                unique_colors.add(first_color)
        except json.JSONDecodeError:
            # Fallback if it's a comma-separated string
            color_list = [c.strip() for c in raw.split(',') if c.strip()]
            if color_list:
                unique_colors.add(color_list[0])

    conn.close()

    return unique_colors


if __name__ == "__main__":
    colors = extract_first_dominant_colors()
    for color in sorted(colors):
        print(color)
