import os

import pandas as pd
import matplotlib.pyplot as plt
from config import EXCEL_FILE_PATH
def save_sorted_data_to_csv(data, filename='passport_search_volume_sorted.csv'):
    # Save the sorted data to a CSV file
    data.to_csv(filename, index=False)
    print(f"Data has been saved to {filename}")
def find_popular_passport_location(excel):
    # Load the data from the Excel file
    # Row skipped because of format in Excel document, if table starts at A1 put skiprows=0
    data_new = pd.read_excel(excel, "Sheet1", skiprows=4)

    # Rename the columns for better clarity
    data_new.columns = ['Question', 'State', 'Search Volume']

    # Drop the initial rows that do not contain relevant data
    # if table starts at A1 delete this one line code below
    data_new = data_new.drop([0, 1]).reset_index(drop=True)

    # Drop the 'Question' column
    data_new = data_new.drop(columns=['Question'])

    # Convert 'Search Volume' to numeric (it might be read as a string)
    data_new['Search Volume'] = pd.to_numeric(data_new['Search Volume'], errors='coerce')

    # Drop rows with missing 'Search Volume'
    data_new = data_new.dropna(subset=['Search Volume'])

    # Sort the dataframe by 'Search Volume' in descending order
    data_sorted = data_new.sort_values(by='Search Volume', ascending=False).reset_index(drop=True)

    # Save the sorted data to a CSV file
    save_sorted_data_to_csv(data_sorted)

    # Select the state with the highest search volume
    highest_search_volume = data_sorted.iloc[0]

    # Display the state with the highest search volume
    print(f"State with the highest search volume: {highest_search_volume['State']}")
    print(f"Search Volume: {int(highest_search_volume['Search Volume'])}")

    # Plot the data
    plt.figure(figsize=(12, 8))  # Increase figure size for better spacing
    plt.bar(data_sorted['State'], data_sorted['Search Volume'], color='skyblue')
    plt.xlabel('State')
    plt.ylabel('Search Volume')
    plt.title('Passport Applications Search Volume by State')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels and align them to the right
    plt.grid(axis='y', linestyle='--', linewidth=0.7)  # Add horizontal grid lines for better readability

    # Add more ticks on the y-axis based on intervals of 5000 up to the maximum value
    max_value = int(data_sorted['Search Volume'].max())
    plt.yticks(range(0, max_value + 5000, 5000))

    plt.subplots_adjust(bottom=0.25)  # Adjust the bottom margin to add space for x-axis labels
    plt.tight_layout()
    plt.show()


# Add Path to Excel Document

def main(xlsx):
    find_popular_passport_location(xlsx)


if __name__ == "__main__":
    # Verify file path
    absolute_path = os.path.abspath(EXCEL_FILE_PATH)
    print(f"Absolute path to the file: {absolute_path}")

    if os.path.exists(absolute_path):
        print("File found.")
        main(EXCEL_FILE_PATH)
    else:
        print("File not found.")