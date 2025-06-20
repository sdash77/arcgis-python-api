import pathlib
import pandas as pd


def export_file_paths_to_excel_pandas(directory, excel_file):
    file_paths = [str(file) for file in pathlib.Path(directory).rglob('*') if file.is_file()]
    df = pd.DataFrame({'File Path': file_paths})
    df.to_excel(excel_file, index=False)


if __name__ == '__main__':
    directory_path = r"C:\Users\shu12142\Documents\geosaurus_repos\geosaurus\tests\integration"  # Replace with your directory path
    excel_file_path = "file_paths.xlsx"
    export_file_paths_to_excel_pandas(directory_path, excel_file_path)
    print(f"File paths exported to {excel_file_path}")