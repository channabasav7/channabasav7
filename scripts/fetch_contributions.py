import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_contributions(username, output_path):
    url = f"https://github.com/users/{username}/contributions"
    print(f"Fetching contributions from: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
        
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Get all contribution calendar days
    day_elements = soup.find_all(class_="ContributionCalendar-day")
    if not day_elements:
        print("Error: Could not find contribution calendar elements in the HTML.")
        # Create folder structure for data if missing
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Write empty template as fallback
        fallback_data = {
            "username": username,
            "total_contributions": 0,
            "longest_streak": 0,
            "current_streak": 0,
            "best_day": {"date": None, "count": 0},
            "days": []
        }
        with open(output_path, "w") as f:
            json.dump(fallback_data, f, indent=2)
        print("Wrote fallback data.")
        return
        
    # Map tooltips by their target element ID
    tooltips = {}
    tooltip_elements = soup.find_all("tool-tip")
    for t in tooltip_elements:
        for_id = t.get("for")
        if for_id:
            tooltips[for_id] = t.get_text(strip=True)
            
    parsed_days = []
    total_contributions = 0
    best_day = {"date": None, "count": 0}
    
    for d in day_elements:
        day_id = d.get("id")
        date_str = d.get("data-date")
        level_str = d.get("data-level", "0")
        
        if not date_str:
            continue
            
        level = int(level_str)
        
        # Get count from tooltip, fallback to estimating based on level if missing
        count = 0
        tooltip_text = tooltips.get(day_id, "")
        if tooltip_text:
            parts = tooltip_text.split()
            first_word = parts[0].replace(",", "") # strip thousands comma
            if first_word.isdigit():
                count = int(first_word)
            elif first_word.lower() == "no":
                count = 0
        else:
            # Fallback estimation
            if level == 0: count = 0
            elif level == 1: count = 2
            elif level == 2: count = 5
            elif level == 3: count = 10
            elif level == 4: count = 18
            
        total_contributions += count
        
        if count > best_day["count"]:
            best_day = {"date": date_str, "count": count}
            
        parsed_days.append({
            "date": date_str,
            "count": count,
            "level": level
        })
        
    # Sort days chronologically
    parsed_days = sorted(parsed_days, key=lambda x: x["date"])
    
    # Calculate streaks
    longest_streak = 0
    temp_streak = 0
    for day in parsed_days:
        if day["count"] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0
            
    current_streak = 0
    if parsed_days:
        # Check last and second-to-last day for active streak
        last_idx = len(parsed_days) - 1
        start_idx = last_idx
        if parsed_days[last_idx]["count"] == 0 and last_idx > 0 and parsed_days[last_idx - 1]["count"] > 0:
            start_idx = last_idx - 1
            
        for i in range(start_idx, -1, -1):
            if parsed_days[i]["count"] > 0:
                current_streak += 1
            else:
                break
                
    # Monthly totals calculation
    monthly_totals = {}
    for day in parsed_days:
        # date format is YYYY-MM-DD
        try:
            dt = datetime.strptime(day["date"], "%Y-%m-%d")
            month_key = dt.strftime("%b %Y") # e.g. "Jul 2026"
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + day["count"]
        except Exception:
            pass
            
    # Compile output data
    output_data = {
        "username": username,
        "total_contributions": total_contributions,
        "longest_streak": longest_streak,
        "current_streak": current_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "days": parsed_days
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Successfully scraped contributions for '{username}'.")
    print(f"Total Contributions: {total_contributions}")
    print(f"Current Streak: {current_streak} days, Longest: {longest_streak} days")
    print(f"Best Day: {best_day['date']} ({best_day['count']} contributions)")
    
if __name__ == "__main__":
    username = "channabasav7"
    if len(sys.argv) > 1:
        username = sys.argv[1]
    elif os.environ.get("GITHUB_USERNAME"):
        username = os.environ.get("GITHUB_USERNAME")
        
    output_path = "data/contributions.json"
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
        
    fetch_contributions(username, output_path)
