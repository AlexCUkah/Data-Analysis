import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def create_dataframe():
    """
    Creates a DataFrame with the age distribution data for both men and women.
    """
    # Define the data for each age group and their corresponding populations for men and women
    data = {
        'Age Group': [
            '0-4', '5-9', '10-14', '15-19', '20-24', '25-29',
            '30-34', '35-39', '40-44', '45-49', '50-54', '55-59',
            '60-64', '65-69', '70-74', '75-79', '80-84', '85+'
        ],
        'Men 2021': [
            4000, 4000, 4000, 6000, 12000, 9000,
            8000, 6000, 6000, 5000, 5000, 5000,
            4000, 3000, 2000, 2000, 1000, 1000
        ],
        'Women 2021': [
            4000, 4000, 4000, 4000, 10000, 8000,
            8000, 6000, 6000, 5000, 5000, 5000,
            4000, 3000, 2000, 2000, 1000, 1000
        ]
    }

    # Create a DataFrame using the defined data
    df = pd.DataFrame(data)
    # Add a column for the total population in each age group by summing the men and women populations
    df['Total 2021'] = df['Men 2021'] + df['Women 2021']
    return df


def calculate_cumulative_population(df):
    """
    Adds a cumulative population column to the DataFrame.
    """
    # Calculate the cumulative population for each age group
    df['Cumulative Population'] = df['Total 2021'].cumsum()
    return df


def identify_median_group(df, total_population):
    """
    Identifies the median group and sets the 'Median Group' column to True for the median age group.
    """
    # Calculate the median position in the total population
    median_position = total_population / 2
    # Initialize all values in the 'Median Group' column to False
    df['Median Group'] = False
    cumulative_population = 0

    # Iterate over each row to find the median group
    for index, row in df.iterrows():
        cumulative_population += row['Total 2021']
        if cumulative_population >= median_position:
            # Mark the median group where the cumulative population reaches the median position
            df.at[index, 'Median Group'] = True
            return df, index, median_position

    return df, None, None


def calculate_median_age(df, median_group_index, median_position):
    """
    Calculates the median age based on the cumulative population.
    """
    # Get the median group information
    median_group = df.iloc[median_group_index]
    if median_group_index == 0:
        lower_bound = 0
    else:
        lower_bound = df.iloc[median_group_index - 1]['Cumulative Population']

    upper_bound = median_group['Cumulative Population']
    group_population = median_group['Total 2021']
    group_range = median_group['Age Group']

    # Determine the age range for the median group
    age_range = group_range.split('-')
    if len(age_range) == 2:
        age_start, age_end = int(age_range[0]), int(age_range[1])
    else:
        age_start, age_end = int(age_range[0]), int(age_range[0]) + 5

    # Calculate the median age assuming a uniform distribution within the age group
    if upper_bound != lower_bound:
        median_age = age_start + ((median_position - lower_bound) / group_population) * (age_end - age_start)
    else:
        median_age = age_start

    # Round the median age to the nearest whole number
    median_age = round(median_age)

    return median_age


def visualize_data(df):
    """
    Visualizes the age distribution data using bar plots and line plots.
    """
    # Set the size of the figure for the plots
    plt.figure(figsize=(14, 8))

    # Create a bar plot for the total population by age group
    plt.subplot(2, 1, 1)
    sns.barplot(x='Age Group', y='Total 2021', data=df, hue='Age Group', dodge=False, legend=False, palette='viridis')
    plt.title('Total Population by Age Group')
    plt.xlabel('Age Group')
    plt.ylabel('Total Population')
    plt.xticks(rotation=45)

    # Create a line plot for the cumulative population by age group
    plt.subplot(2, 1, 2)
    sns.lineplot(x='Age Group', y='Cumulative Population', data=df, marker='o', color='blue')
    plt.title('Cumulative Population by Age Group')
    plt.xlabel('Age Group')
    plt.ylabel('Cumulative Population')
    plt.xticks(rotation=45)

    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.show()


def main():
    # Adjust pandas display settings for better readability
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    # Create the DataFrame and perform calculations
    df = create_dataframe()
    df = calculate_cumulative_population(df)
    total_population = df['Total 2021'].sum()
    df, median_group_index, median_position = identify_median_group(df, total_population)
    median_age = calculate_median_age(df, median_group_index, median_position)

    # Print the DataFrame with all relevant columns
    print(df[['Age Group', 'Men 2021', 'Women 2021', 'Total 2021', 'Cumulative Population', 'Median Group']])
    print(f"Estimated Median Age: {median_age}")

    # Save the DataFrame to a CSV file
    df.to_csv('age_distribution.csv', index=False)
    print("DataFrame has been saved to 'age_distribution.csv'.")

    # Visualize the data
    visualize_data(df)


if __name__ == "__main__":
    main()
