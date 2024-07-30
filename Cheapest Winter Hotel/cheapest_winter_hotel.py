import requests
import concurrent.futures
import time
from states_and_cities import state_cities, state_names, city_names
import csv
import matplotlib.pyplot as plt

def get_access_token(api_key, api_secret):
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": api_secret
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to get access token: " + response.text)

def get_hotels_by_city(access_token, city_code, radius=5, radius_unit="KM", hotel_source="ALL"):
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {
        "cityCode": city_code,
        "radius": radius,
        "radiusUnit": radius_unit,
        "hotelSource": hotel_source
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to retrieve hotels: " + response.text)

def get_hotel_offers(access_token, hotel_ids, check_in_date, check_out_date, adults=1):
    url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {
        "hotelIds": ",".join(hotel_ids),
        "adults": adults,
        "checkInDate": check_in_date,
        "checkOutDate": check_out_date
    }

    retries = 3
    for i in range(retries):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Rate limit exceeded
            print(f"Rate limit exceeded, retrying in {2 ** i} seconds...")
            time.sleep(10 ** i)
        else:
            break
    raise Exception("Failed to retrieve hotel offers: " + response.text)

def process_city(access_token, state, city_code, city_name):
    state_full_name = state_names.get(state, state)
    try:
        hotels_data = get_hotels_by_city(access_token, city_code)
        print(f"Hotels in {city_name}, {state_full_name}:")

        hotel_ids = [hotel["hotelId"] for hotel in hotels_data["data"]]
        if hotel_ids:
            # Set check-in and check-out dates to December 25, 2024, to December 27, 2024
            check_in_date = "2024-12-25"
            check_out_date = "2024-12-27"
            offers_data = get_hotel_offers(access_token, hotel_ids, check_in_date, check_out_date)

            for hotel in offers_data["data"]:
                hotel_name = hotel["hotel"]["name"]
                hotel_city = city_names.get(hotel["hotel"]["cityCode"], hotel["hotel"]["cityCode"])
                for offer in hotel["offers"]:
                    try:
                        price_total = offer["price"]["total"]
                        currency = offer["price"]["currency"]

                        hotel_info = {
                            "State": state_full_name,
                            "Hotel Name": hotel_name,
                            "City": hotel_city,
                            "Check-in Date": check_in_date,
                            "Check-out Date": check_out_date,
                            "Total Price": price_total,
                            "Currency": currency
                        }
                        hotel_prices.append(hotel_info)
                    except KeyError:
                        print(f"Error processing offer for hotel {hotel_name}: missing total price.")
                        continue
        else:
            print(f"No hotels found for city {city_code}, {state_full_name}")

    except Exception as e:
        print(f"Error processing city {city_code} in state {state_full_name}: {e}")

# Replace with your Amadeus API key and secret
api_key = "WV22KiKdTSzwAg14CMgf5cMNzeAJQHgh"
api_secret = "bLQgKxilAzelA76N"

hotel_prices = []

try:
    access_token = get_access_token(api_key, api_secret)
    print("Access Token:", access_token)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_city = {
            executor.submit(process_city, access_token, state, city, city_names.get(city, city)): (state, city) for
            state, cities in state_cities.items() for city in cities}

        for future in concurrent.futures.as_completed(future_to_city):
            state, city = future_to_city[future]
            try:
                future.result()
            except Exception as e:
                print(f"City {city} in state {state} generated an exception: {e}")

except Exception as e:
    print(e)

# Get the 5 lowest-cost hotels from each state
state_lowest_hotels = {}
for hotel in hotel_prices:
    state = hotel["State"]
    if state not in state_lowest_hotels:
        state_lowest_hotels[state] = []
    state_lowest_hotels[state].append(hotel)

for state in state_lowest_hotels:
    state_lowest_hotels[state] = sorted(state_lowest_hotels[state], key=lambda x: float(x["Total Price"]))[:5]

# Calculate average price of the 5 lowest-cost hotels for each state
state_avg_prices = {}
for state, hotels in state_lowest_hotels.items():
    total_price = sum(round(float(hotel["Total Price"]), 2) for hotel in hotels)
    avg_price = round(total_price / len(hotels), 2)
    state_avg_prices[state] = avg_price

# Find the cheapest hotel out of all states
all_hotels_sorted = sorted(hotel_prices, key=lambda x: float(x["Total Price"]))
cheapest_hotel = all_hotels_sorted[0]

# Rank states based on average price of their cheapest winter hotels
ranked_states = sorted(state_avg_prices.items(), key=lambda x: x[1])

# Write hotel prices to CSV
with open('hotel_prices.csv', 'w', newline='') as csvfile:
    fieldnames = ["State", "Hotel Name", "City", "Check-in Date", "Check-out Date", "Total Price", "Currency"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for state, hotels in state_lowest_hotels.items():
        writer.writerows(hotels)

# Write ranked states to CSV
with open('ranked_states.csv', 'w', newline='') as csvfile:
    fieldnames = ["State", "Average Price"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for state, avg_price in ranked_states:
        writer.writerow({"State": state, "Average Price": avg_price})

# Write top 5 states to CSV
with open('top_5_states.csv', 'w', newline='') as csvfile:
    fieldnames = ["State", "Average Price"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for state, avg_price in ranked_states[:5]:
        writer.writerow({"State": state, "Average Price": avg_price})

# Print the cheapest hotel for each state
for state, hotels in state_lowest_hotels.items():
    cheapest_hotel_state = hotels[0]
    print(f"Cheapest hotel in {state}: {cheapest_hotel_state['Hotel Name']} in {cheapest_hotel_state['City']} at ${cheapest_hotel_state['Total Price']} {cheapest_hotel_state['Currency']}")

# Print the overall cheapest hotel
print(f"Cheapest hotel overall: {cheapest_hotel['Hotel Name']} in {cheapest_hotel['City']} at ${cheapest_hotel['Total Price']} {cheapest_hotel['Currency']}")

# Data Visualization
# Bar chart for average prices of states
states = [state for state, _ in ranked_states]
avg_prices = [avg_price for _, avg_price in ranked_states]

plt.figure(figsize=(14, 7))
plt.bar(states, avg_prices, color='skyblue')
plt.xlabel('State')
plt.ylabel('Average Price ($)')
plt.title('Average Prices of the 5 Lowest-Cost Hotels by State')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('average_prices_by_state.png')
plt.show()

# Highlight top 5 states in a separate bar chart
top_5_states = states[:5]
top_5_avg_prices = avg_prices[:5]

plt.figure(figsize=(10, 5))
plt.bar(top_5_states, top_5_avg_prices, color='lightgreen')
plt.xlabel('State')
plt.ylabel('Average Price ($)')
plt.title('Top 5 States with the Lowest Average Hotel Prices')
plt.tight_layout()
plt.savefig('top_5_states.png')
plt.show()

print("Data and visualizations have been generated.")
