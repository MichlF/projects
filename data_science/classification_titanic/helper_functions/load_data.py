# Note: Since VSC is being annoying, you can only import this script when importing it as
# from helper_functions.load_data import load_data
# if you've set the correct path (manually) or check Preference>Settings>"Terminal: execute in file dir" and/or
# add the following workaround to the debug configuration in the settings.json file to also run in debugger:
# {
#     "name": "Python: Debug in file dir",
#     "type": "python",
#     "request": "launch",
#     "program": "${file}",
#     "console": "integratedTerminal",
#     "cwd": "${fileDirname}",
#     "purpose": ["debug-in-terminal"]
# }
# see also: https://lightrun.com/answers/microsoft-vscode-python-option-execute-in-file-dir-ignored-when-use-play-button-debug-python-file-in-terminal

## Import
import pandas as pd


## Classes and functions
def load_data(
    filename: str = "", path_url: str = "", subfolder: str = "data/", *args, **kwargs
) -> pd.DataFrame:
    print(f"Loading in {filename}...")
    try:
        filetype = filename.split(".")[1:][0]  # identify filetype
    except Exception:
        raise Exception(f"ERROR: Probably, no data type provided!")
    if filetype in ["csv", "txt"]:
        try:
            data = pd.read_csv(subfolder + filename, *args, **kwargs)
        except FileNotFoundError:
            print(
                f"Dataset is not stored locally as {subfolder+filename}. Attempting to get it from {path_url}..."
            )
            data = pd.read_csv(path_url, *args, **kwargs)
        except Exception:
            raise Exception("ERROR: Something went wrong...")
    elif (filetype == "xls") or (filetype == "xlsx"):
        try:
            data = pd.read_excel(subfolder + filename, *args, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Dataset is not stored locally as {subfolder+filename}. Download it first or check subfolder!"
            )
        except Exception:
            raise Exception("ERROR: Something went wrong...")
    else:
        raise (f"Unable to load data. File type '{filetype}' unknown.")

    print("Data set successfully loaded.\n")

    return data
