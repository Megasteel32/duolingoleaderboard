import requests
import json
import datetime
import os
from collections import defaultdict
import pytz

def convert_to_json(old_file_path, new_file_path):
    data = {}

    with open(old_file_path, 'r') as old_file:
        for line in old_file:
            date, user_xp_data = line.strip().split(':', 1)
            data[date] = json.loads(user_xp_data)

    with open(new_file_path, 'w') as new_file:
        json.dump(data, new_file)

def get_total_xp(username):
    url = f"https://www.duolingo.com/2017-06-30/users?username={username}"
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0'  # Add a User-Agent header
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Request to {url} failed with status code {response.status_code}")
        return None

    data = json.loads(response.text)
    if "users" not in data:
        print(f"Key 'users' not found in the response data: {data}")
        return None

    user_data = data["users"][0]  # Access the first user dictionary
    if "totalXp" not in user_data or "name" not in user_data:
        print(f"Key 'totalXp' or 'name' not found in the user data: {user_data}")
        return None

    name = user_data["name"]
    if name == "Bella":
        name = "Ekta"
    if name == "Fred":
        name = "Elliot"

    return name, user_data["totalXp"]

def load_previous_data(file_path):
    data_by_day = []
    data_by_month = defaultdict(list)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                timestamp, user_xp_data = line.strip().split(':', 1)
                date = datetime.datetime.strptime(timestamp, '%Y-%m-%d').date()
                data_by_day.append((date, json.loads(user_xp_data)))
                month_year = (date.year, date.month)
                data_by_month[month_year].append((date, json.loads(user_xp_data)))
    return data_by_day, data_by_month

def update_data(file_path, user_xp_list):
    current_date = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
    timestamp = current_date.strftime('%Y-%m-%d')
    data_entry = f"{timestamp}:{json.dumps(user_xp_list)}\n"

    temp_file = file_path + '.tmp'
    with open(file_path, 'r') as file, open(temp_file, 'w') as temp:
        found = False
        for line in file:
            if line.startswith(timestamp):
                temp.write(data_entry)
                found = True
            else:
                temp.write(line)
        if not found:
            temp.write(data_entry)

    os.replace(temp_file, file_path)

def main():
    usernames = ["megasteel32", "bella_247", "eliastread", "nickht1", "nicolassalazar1", "fred137179"]  # Replace with your list of usernames
    user_xp_list = []

    for username in usernames:
        user_info = get_total_xp(username)
        if user_info is not None:
            user_xp_list.append(user_info)

    file_path = 'user_xp_data.txt'
    data_by_day, data_by_month = load_previous_data(file_path)
    current_date = datetime.datetime.now(pytz.timezone('US/Eastern')).date()

    update_data(file_path, user_xp_list)
    print("Data updated for the current day.")

    print("\nCurrent data:")
    user_xp_list.sort(key=lambda x: x[1], reverse=True)  # Sort user_xp_list based on XP in decreasing order
    for name, xp in user_xp_list:
        print(f"{name}: Current XP = {xp}")


    # Reload the data after updating it
    data_by_day, data_by_month = load_previous_data(file_path)

    if len(data_by_day) > 1:
        print("\nDifference between the previous day and today:")
        previous_day_data = data_by_day[-2][1]
        current_day_data = data_by_day[-1][1]
        diff_data = [(name, current_xp - previous_day_data[i][1]) for i, (name, current_xp) in enumerate(current_day_data)]
        diff_data.sort(key=lambda x: x[1], reverse=True)  # Sort diff_data based on XP difference in decreasing order
        for name, diff in diff_data:
            print(f"{name}: XP Difference = {diff}")

    print("\nDifference between the start and end of each month:")
    for month, month_data in data_by_month.items():
        start_date, start_data = month_data[0]
        end_date, end_data = month_data[-1]
        print(f"\nMonth: {month[0]}-{month[1]:02d} (Start: {start_date}, End: {end_date})")
        diff_data = [(name, end_xp - start_data[i][1]) for i, (name, end_xp) in enumerate(end_data)]
        diff_data.sort(key=lambda x: x[1], reverse=True)  # Sort diff_data based on XP difference in decreasing order
        for name, diff in diff_data:
            print(f"{name}: XP Difference = {diff}")

if __name__ == "__main__":
    main()

