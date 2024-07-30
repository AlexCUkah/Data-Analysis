import csv
import os


def calculate_average_speed(distance, speed_to, speed_from):
    """
    Calculate the average speed for a round trip.

    Parameters:
    distance (float): The distance to point A.
    speed_to (float): The speed to point A (mph).
    speed_from (float): The speed from point A (mph).

    Returns:
    float: The average speed (mph).
    """
    # Calculate the total distance
    total_distance = 2 * distance

    # Calculate the time taken to travel to point A and return
    time_to = distance / speed_to
    time_from = distance / speed_from

    # Calculate the total time taken for the round trip
    total_time = time_to + time_from

    # Calculate the average speed for the round trip
    average_speed = total_distance / total_time

    return average_speed


def save_to_csv(file_name, distance, speed_to, speed_from, average_speed):
    """
    Save the calculation details and average speed to a CSV file.

    Parameters:
    file_name (str): The name of the CSV file.
    distance (float): The distance to point A.
    speed_to (float): The speed to point A (mph).
    speed_from (float): The speed from point A (mph).
    average_speed (float): The average speed (mph).
    """
    # Check if the directory exists, if not, create it
    directory = os.path.dirname(file_name)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check if the file already exists
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write the header only if the file does not exist
        if not file_exists:
            writer.writerow(['Distance to Point A (miles)', 'Speed to Point A (mph)', 'Speed from Point A (mph)',
                             'Average Speed (mph)'])
        # Write the data row
        writer.writerow([distance, speed_to, speed_from, average_speed])
    print(f"Data has been saved to {file_name}")


def main():
    # Define the distance and speeds for the trip
    distance = 60  # Enter the distance to point A
    speed_to = 60  # Speed to point A in mph
    speed_from = 20  # Speed from point A in mph

    # Calculate the average speed for the round trip
    average_speed = calculate_average_speed(distance, speed_to, speed_from)
    print(f"The average speed for the round trip is {average_speed} mph.")

    # Save the results to a CSV file
    file_name = os.path.join('Average Speed Of Car Calculation', 'average_speed.csv')
    save_to_csv(file_name, distance, speed_to, speed_from, average_speed)


if __name__ == "__main__":
    main()
