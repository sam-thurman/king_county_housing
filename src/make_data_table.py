import requests
import os
from os import listdir
from os.path import isfile, join
import zipfile
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

path = '../data/' # Path to data Folder

website_url = "https://aqua.kingcounty.gov/extranet/assessor/" # Path to website containing downloads

parcel_url = 'Parcel.zip'                # File extension of parcel
sale_url = 'Real%20Property%20Sales.zip' # File extension of Property Sales
res_url = 'Residential%20Building.zip'   # File extension of Residential Buildings
list_of_files = [parcel_url, sale_url, res_url] # List of all the files to be downloaded


# Call this to build the required data table from the KC website
def build_data_file():
    new_files = make_all_csv()
    print('New files downloaded: ' + str(new_files))
    new_file_path = make_merged_csv(new_files)
    print('Tables merged and saved to: ' + new_file_path)
    delete_files(new_files)
    print('All downloaded files have been deleted.')
    print('Data is now accessible from the data folder.')


    
    
    
def make_all_csv(list_of_files = list_of_files):
    '''
    This will take in a list file names that have a similar web address (website_url)
    and makes a csv file for each of them. The download must be a .zip file
    
    Parameters
    ----------
    list_of_files: A list of file names that have the same web address
    
    Returns
    -------
    A set of the new files that have been created in the path
    '''
    old_files = list_current_data_files()
    for file in list_of_files:
        make_csv(file)
    new_files = list_current_data_files()
    return new_files.difference(old_files)
    

def make_csv(file_name):
    '''
    Takes the filename of a .zip extended off the website_url, downloads it,
    unzips it and removes the .zip
    
    Parameters
    ----------
    file_name: extension for the .zip
    
    Returns
    -------
    nothing :)
    '''
    response = get_response(file_name)
    zip_path = make_zip(response, file_name)
    extract_zip(zip_path, file_name)
    os.remove(zip_path)
    

def get_response(file_name):
    '''
    Takes in a file and gets a response from the website from website_url
    
    Parameters
    ----------
    file_name: File to be downloaded
    
    Returns
    -------
    Response object from the file that was downloaded
    '''
    response = requests.get(website_url + file_name)
    return response


def make_zip(response, file_name):
    '''
    Makes a zip file to path from an API response
    
    Parameters
    ----------
    response: API response on a .zip file
    
    file_name: name the file will have when downloaded
    
    Returns
    -------
    The path to the .zip file
    '''
    zip_path = path + file_name
    open(zip_path, 'wb').write(response.content)
    return zip_path


def extract_zip(zip_path, file_name):
    '''
    Extracts the zip file given its path.
    
    Parameters
    ----------
    zip_path: location of the zip file to be unzipped
    
    file_name: this is the name of the zip file and is used to make the destination for the unzipped file
    
    Returns
    -------
    nothing :)
    '''
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(zip_path.replace(file_name, ''))
        

def list_current_data_files(path = path):
    '''
    Lists all the CSVs in a given path
    
    Parameters
    ----------
    path: Path to search for CSV files.
          Default: global path to data folder
    
    Returns
    -------
    A set of all the CSV files in a given path
    '''
    files = [file for file in listdir(path) if isfile(join(path, file))]
    csv_only = {file for file in files if '.csv' in file}
    return csv_only

        
        

def add_pin(df):
    '''
    Creates a dataframe with a . Uses Major and Minor columns to construct PIN column
    
    Parameters
    ----------
    df: Dataframe containing a Major and Minor column that will be concatonated to make a PIN
        Major is 6 characters and Minor is 4 characters
    
    Returns
    -------
    A dataframe that has a PIN column added to it
    '''
    df['pin'] = df['Major'].astype(str).str.zfill(6) + df['Minor'].astype(str).str.zfill(4)
    return df


def merge_all(df_list, on = 'pin'):
    '''
    Merges all the the dataframes in the list on a shared column
    
    Parameters
    ----------
    df_list: list of dataframes to be merged together. They must all have the column <on>
    on: the column to join the dataframes on. The dataframes must all have this column
        Default: PIN number
    
    Returns
    -------
    A dataframes of all the tables merged
    '''
    merged = df_list[0]
    for df in df_list[1:]:
        merged = pd.merge(merged, df, on = on, how = 'inner')
    return merged


def make_merged_csv(new_files):
    '''
    Creates a merged table of all the new csv files that have been downloaded.
    These files must have a Major and Minor column
    
    Parameters
    ----------
    new_files: The new files that have been downloaded. These are csvs and must have a major column and mino column
    
    Returns
    -------
    The path to the new file that was creted
    '''
    dfs = [pd.read_csv(path + file, encoding = 'latin-1') for file in new_files]
    dfs = [add_pin(df) for df in dfs]
    print('PINs added to tables')
    merged = merge_all(dfs)
    cleaned = merged[(merged['SalePrice'] < 5000000) & (merged['SalePrice'] > 10)]
    cleaned_2019 = cleaned[cleaned['DocumentDate'].str.contains('2019')]
    cleaned_2019.to_csv(path + 'housing2019.csv')
    return path + 'housing2019.csv'


def delete_files(files, path = path):
    '''
    Deletes all files in the list of files in the given path
    
    Parameters
    ----------
    files: list of files to be deleted
    path: Path that contains all the files to be deleted
          Default: data folder in repo (global var)
    
    Returns
    -------
    nothing :)
    
    '''
    for file in files:
        os.remove(path + file)
