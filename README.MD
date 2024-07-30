# Data Analysis Test

This repository contains data analysis projects for the Junior Data Analyst assessment. The projects are organized into different directories, each focusing on a specific analysis task.

## Project Structure

- **Average Speed Of Car Calculation**
- **Cheapest Winter Hotel**
- **data**
  - `Junior Data Analyst Questions.xlsx`
- **Median Age In Oxford**
- **Popular Passport Locations**
  - **output**
    - `passport_search_volume_sorted.csv`
  - `popular_passport_location.py`
- `config.py`
- `IGNORE_html_parser.py`
- `IGNORE_play.py`
- `Junior Data Analyst Questions answers.xlsx`

## Setup

To run the projects, you need to have Python installed. Follow the steps below to set up the environment and run the scripts.

### 1. Clone the repository:

```bash
git clone git@github.com:AlexCUkah/Data-Analysis.git

2. Navigate to the project directory:

bash

cd Data_Analysis_Test

3. Create a virtual environment:

bash

python -m venv .venv

4. Activate the virtual environment:

    On Windows:

bash

.venv\Scripts\activate

    On macOS and Linux:

bash

source .venv/bin/activate

5. Install the required packages:

bash

pip install -r requirements.txt

Running the Scripts
Popular Passport Locations

This script analyzes the search volume for passport applications by state.

bash

cd "Popular Passport Locations"
python popular_passport_location.py

Cheapest Winter Hotel

This script analyzes hotel prices to determine and rank which US states have the cheapest winter hotels.

bash

cd "Cheapest Winter Hotel"
python cheapest_winter_hotel.py

Analysis Details
Popular Passport Locations

To determine which state has the most popular passport applications based on search volume, I followed these steps:
Data Cleaning and Preparation:
- Loaded the data from the provided Excel file.
- Removed irrelevant rows and columns.
- Converted the search volume data to numeric format.
Data Analysis:
- Sorted the data by search volume in descending order to identify the state with the highest search volume.
Visualization:
- Created a bar chart to visualize the search volumes for passport applications by state. The chart helps in quickly identifying the states with the highest and lowest search volumes.
State with the Highest Search Volume:
- State: California
- Search Volume: 90,500
Python Script:
To complement the analysis done in Excel, I have written a Python script that performs the same steps programmatically. The script is attached as popular_passport_location.py.


Median Population Age 
Data Source

Office for National Statistics (ONS) - Census 2021
URL: https://www.ons.gov.uk/releases/initialfindingsfromthe2021censusinenglandandwales
Data Preparation Steps

    Imported raw data from the Census 2021 dataset.
    Combined age group data for men and women.
    Calculated total population for each age group.

Calculation Methodology

    Calculated cumulative population for each age group.
    Identified the age group where the cumulative population reaches or exceeds half of the total population.
    Estimated the median age using the identified age group.




Average Car Speed From orignal position to point A back to orignal position

Input Data:
        Entered the speed to point A (60 mph) and the speed from point A (20 mph) in the Excel   sheet.
        Defined the distance to point A as a variable, D.

Calculation Methodology

    Total Distance Calculation:
        The total distance for the round trip is twice the distance to point A.
        Formula: Total Distance = 2 * Distance to Point A

    Time Calculation:
        Calculated the time taken to travel to point A.
            Formula: Time to Point A = Distance to Point A / Speed to Point A
        Calculated the time taken to travel from point A.
            Formula: Time from Point A = Distance to Point A / Speed from Point A
        Summed the times to get the total travel time.
            Formula: Total Time = Time to Point A + Time from Point A

    Average Speed Calculation:
        Used the formula for average speed: Average Speed = Total Distance / Total Time

Results

The calculations show that the average speed for the round trip is 30 mph.
Python Script:

To complement the analysis done in Excel, the following Python script performs the same steps programmatically:


Cheapest Winter Hotel
Summary

    Objective: Rank US states by average prices of the five cheapest winter hotels.
    Methodology: Data collected using Amadeus API (Only had access to some details). Extracted hotel prices for each state, calculated average of the five cheapest hotels, and ranked states based on these averages.
    Key Findings: Top 5 states with the cheapest average hotel prices. Detailed hotel prices.

State Rankings

    Columns: State, Average Price
    Data: Sorted list of states by average price of 5 lowest-cost hotels.

Top 5 States

    Columns: State, Average Price
    Data: Top 5 states with the lowest average hotel prices.
    Cheapest State: Maryland

Hotel Prices

    Columns: State, Hotel Name, City, Check-in Date, Check-out Date, Total Price, Currency
    Data: Detailed hotel price information for all states and cities.
