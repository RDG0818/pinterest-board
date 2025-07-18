import os

def rename_files_in_directory(directory):
    for filename in os.listdir(directory):
        # Check if filename contains spaces
        if ' ' in filename:
            new_filename = filename.replace(' ', '_')
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)
            # Rename the file
            os.rename(old_path, new_path)
            print(f'Renamed: "{filename}" -> "{new_filename}"')

if __name__ == "__main__":
    folder_path = input("Enter the directory path: ").strip()
    if os.path.isdir(folder_path):
        rename_files_in_directory(folder_path)
    else:
        print("Invalid directory path.")
