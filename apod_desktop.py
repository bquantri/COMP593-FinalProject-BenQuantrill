""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_dir_path [apod_date]

Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)

History:
  Date        Author    Description
  2022-03-11  J.Dalby   Initial creation 
"""
from sys import argv, exit
from datetime import datetime, date
from hashlib import sha256
from os import path

import hashlib
import requests
import sqlite3
import os
import ctypes

def main():

    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)
    
    # Download today's APOD
    image_url = apod_info_dict['url']
    image_msg = download_apod_image(image_url)
    image_sha256 = hashlib.sha256(image_msg).hexdigest()
    image_size = -1 + len(image_msg)
    image_path = get_image_path(image_url, image_dir_path)

    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)

def get_image_dir_path():
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date():
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    return apod_date

def get_image_path(image_url, dir_path):
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """

    new_image_url = os.path.basename(os.path.normpath(image_url))

    os.path.normpath(dir_path)

    return os.path.join(dir_path, new_image_url)

def get_apod_info(date):
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """    
    nasaAPI = "EMwuI4VvmRz1wy7lwzfzXwrXjektW832S3gBEEjN"

    apodURL = 'https://api.nasa.gov/planetary/apod/'
    params = {
        'api_key': nasaAPI,
        'date': date,
    }

    response = requests.get(apodURL,params=params)

    if response.status_code == 200:
        print("Getting APOD info from NASA... success!")        
    else:
        print("Close, but no cigar", response.status_code)

    url = response.json()['url']
    return {'url':url}

def print_apod_info(image_url, image_path, image_size, image_sha256):
    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """    
    print("APOD Information:")
    print("     URL:", image_url)
    print("     File Path:", image_path)
    print("     File Size:", image_size, "bytes")
    print("     SHA-256:", image_sha256)

    return #TODO

def download_apod_image(image_url):
    """
    Downloads an image from a specified URL.

    :param image_url: URL of image
    :returns: Response message that contains image data
    """

    urlresponse = requests.get(image_url)

    if urlresponse.status_code == 200:
        print("downloading APOD from NASA... success!")
    else:
        print("Close, but no cigar", urlresponse.status_code)

    return urlresponse.content

def save_image_file(image_msg, image_path):
    """
    Extracts an image file from an HTTP response message
    and saves the image file to disk.

    :param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    """

    with open(image_path, 'wb') as handler:
        handler.write(image_msg)

    print("Saving Image File... Success!")

    return

def create_image_db(db_path):
    """
    Creates an image database if it doesn't already exist.

    :param db_path: Path of .db file
    :returns: None
    """

    #Retrieve Connection Object and create a cursor object
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    #create the database
    image_db = '''CREATE TABLE IF NOT EXISTS apod_images (
                    "date" TEXT,
                    "full_path" TEXT,
                    "File_size" TEXT,
                    "SHA_256" TEXT
                    ) '''

    cursor.execute(image_db)
    connection.commit()
    connection.close()

    return

def add_image_to_db(db_path, image_path, image_size, image_sha256):
    """
    Adds a specified APOD image to the DB.

    :param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """

    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    apod_to_db = """INSERT INTO apod_images (
                    "date",
                    "full_path",
                    "File_size",
                    "SHA_256")
                    VALUES (?, ?, ?, ?) """

    image_info = (db_path,
                  image_path,
                  image_size,
                  image_sha256,)

    cursor.execute(apod_to_db, image_info)
    connect.commit()
    connect.close()

    return

def image_already_in_db(db_path, image_sha256):
    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """ 

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    compareHash = """SELECT SHA_256 FROM apod_images
                     WHERE SHA_256"""
    
    cursor.execute(compareHash)
    results = cursor.fetchall()

    if results == image_sha256:
        print("New Image already in database")
        return True
    elif results != image_sha256:
        print("New Image not in cache")
        return False
    
     
def set_desktop_background_image(image_path):
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """

    set_wallpaper = image_path
    ctypes.windll.user32.SystemParametersInfoW(20, 0, set_wallpaper, 3)

    print("setting Desktop Wallpaper... Success!")

    return #TODO

main()