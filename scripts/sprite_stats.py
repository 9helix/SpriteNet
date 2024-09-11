import os


def count_files_and_unique_values(folder_path):
    # Initialize variables
    file_count = 0
    unique_values = set()

    # Iterate through files in the folder
    for filename in os.listdir(folder_path):
        # Check if it's a file
        if os.path.isfile(os.path.join(folder_path, filename)):
            file_count += 1

            # Extract the value between the first and second underscore
            parts = filename.split("_")
            if len(parts) > 2:
                value = parts[2]
                unique_values.add(value)

    # Print results
    print(f"Number of files in folder: {file_count}")
    print(
        f"Number of unique values between first and second underscore: {len(unique_values)}"
    )
    print(f"Unique values: {sorted(unique_values)}")


# Specify the folder path
folder_path = input("Folder path: ")  # Replace with your folder path

# Call the function
count_files_and_unique_values(folder_path)
