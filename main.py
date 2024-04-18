import requests
import json
import datetime
import os
from collections import defaultdict
import pytz
import re

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
            data = json.load(file)
            for timestamp, user_xp_data in data.items():
                date = datetime.datetime.strptime(timestamp, '%Y-%m-%d').date()
                data_by_day.append((date, user_xp_data))
                month_year = (date.year, date.month)
                data_by_month[month_year].append((date, user_xp_data))
    return data_by_day, data_by_month

def update_data(file_path, user_xp_dict, previous_day_data):
    current_date = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
    timestamp = current_date.strftime('%Y-%m-%d')

    updated_data = []
    for name, xp in user_xp_dict:
        diff = xp - previous_day_data.get(name, 0)
        updated_data.append({"name": name, "totalXp": xp, "diff": diff})

    with open(file_path, 'r') as file:
        data = json.load(file)

    data[timestamp] = updated_data

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def add_diffs_retroactively(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    sorted_dates = sorted(data.keys())

    for i in range(len(sorted_dates)):
        current_date = sorted_dates[i]

        current_day_data = data[current_date]

        if i == 0:  # If it's the first day, set the diff to 0 for all users
            for user_data in current_day_data:
                user_data["diff"] = 0
        else:  # If it's not the first day, calculate the diff as before
            previous_date = sorted_dates[i - 1]
            previous_day_data = {user_data["name"]: user_data["totalXp"] for user_data in data[previous_date]}

            for user_data in current_day_data:
                name = user_data["name"]
                xp = user_data["totalXp"]
                diff = xp - previous_day_data.get(name, 0)
                user_data["diff"] = diff

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def main():
    usernames = ["megasteel32", "bella_247", "eliastread", "nickht1", "nicolassalazar1", "fred137179"]  # Replace with your list of usernames
    user_xp_list = []

    for username in usernames:
        user_info = get_total_xp(username)
        if user_info is not None:
            user_xp_list.append(user_info)

    file_path = 'user_xp_data.json'
    data_by_day, data_by_month = load_previous_data(file_path)
    current_date = datetime.datetime.now(pytz.timezone('US/Eastern')).date()

    previous_day_data = {}
    if len(data_by_day) > 0:
        previous_day_data = {user_data["name"]: user_data["totalXp"] for user_data in data_by_day[-1][1]}

    update_data(file_path, user_xp_list, previous_day_data)
    print("Data updated for the current day.")

    print("\nCurrent data:")
    user_xp_list.sort(key=lambda x: x[1], reverse=True)  # Sort user_xp_list based on XP in decreasing order
    for name, xp in user_xp_list:
        print(f"{name}: Current XP = {xp}")

    # Reload the data after updating it
    data_by_day, data_by_month = load_previous_data(file_path)

    add_diffs_retroactively(file_path)

    if len(data_by_day) > 1:
        print("\nDifference between the previous day and today:")
        previous_day_data = {user_data["name"]: user_data["totalXp"] for user_data in data_by_day[-2][1]}
        current_day_data = data_by_day[-1][1]
        diff_data = [(user_data["name"], user_data["diff"]) for user_data in current_day_data]
        diff_data.sort(key=lambda x: x[1], reverse=True)  # Sort diff_data based on XP difference in decreasing order
        for name, diff in diff_data:
            print(f"{name}: XP Difference = {diff}")

    print("\nDifference between the start and end of each month:")
    for month, month_data in data_by_month.items():
        start_date, start_data = month_data[0]
        end_date, end_data = month_data[-1]
        print(f"\nMonth: {month[0]}-{month[1]:02d} (Start: {start_date}, End: {end_date})")
        diff_data = [(user_data["name"], end_data[i]["totalXp"] - start_data[i]["totalXp"]) for i, user_data in enumerate(end_data)]
        diff_data.sort(key=lambda x: x[1], reverse=True)  # Sort diff_data based on XP difference in decreasing order
        for name, diff in diff_data:
            print(f"{name}: XP Difference = {diff}")

if __name__ == "__main__":
    main()