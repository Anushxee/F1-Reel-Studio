import fastf1
from fastf1.ergast import Ergast

def get_latest_race_results():
    try:
        ergast = Ergast()
        races = ergast.get_race_results(season='current', round='last')
        if races.empty:
            return []

        results = []
        for _, row in races.iterrows():
            driver_name = f"{row['Driver.familyName']}, {row['Driver.givenName']}"
            time = row['Time.time'] if not pd.isna(row['Time.time']) else "N/A"
            results.append({
                "position": row["position"],
                "name": driver_name,
                "time": time
            })

        return results

    except Exception as e:
        print("Error fetching race data:", e)
        return []
