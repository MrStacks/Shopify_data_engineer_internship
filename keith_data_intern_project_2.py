"""Searchable Image Repository

This script allows the user to store encrypted images and accompanying 
keywords in a database. The user can then search the images via keyword 
search. 

Program accepts the following image file types: .bmp, .jpeg, .jpg, .png, .tiff

This script requires the following to be installed within the Python environment
you are running the script in: 
`os` `sys` `cv2` `glob``pandas` `cryptography.fernet` `uuid`

This file can also be imported as a module and contains the following
functions:

    * get_key() - returns an encryption key for the file
    * get_dataframe() - returns Pandas dataframe of existing database, or creates a new one
    * encrypt_file() - returns image file in encrypted format
    * image_data() - requests image attributes from user & populates corresponding values
    * store_images() - stores image(s) in the database
    * search_images() - requests image keyword(s) & returns corresponding image(s) 
    * main - main function permits user interactivity with the script

The script is a submission to the Summer 2022 Shopify Data Engineering 
Internship Challenge. It is intended to be used as a base program which
can later be expanded for greater functionality. (E.g., to use a SQL or 
other database, expanded image search via machine learning derived features, 
etc.)
"""

## Import modules
import os
import sys
import cv2
import glob
import pandas as pd
from cryptography.fernet import Fernet
import uuid

## Constants
KEY_FILENAME = './key.key'
DATA_FILENAME = './data.csv'

## MOCKFunction
def get_input(prompt = ''):
    return input(prompt)

## Functions
def get_key():
    '''
    Generates encryption key, if one doesn't already exist. 
    :return: Fernet generated encryption key
    '''
    if os.path.exists(KEY_FILENAME):
        with open(KEY_FILENAME, 'rb') as key_file:
            return key_file.read()
    else:
        KEY = Fernet.generate_key() # encryption key
        with open(KEY_FILENAME, 'wb') as key_file:
            key_file.write(KEY)
        return KEY

def get_dataframe():
    '''
    Checks if a dataframe (serving as the database) exists. 
    If so, returns the existing database. If not, creates a new
    dataframe -> database. 
    :return: CSV version of dataframe with headerdata ready for images
    '''
    if os.path.exists(DATA_FILENAME): #if there is already a dataframe, use it
        frame = pd.read_csv(DATA_FILENAME, dtype=str)
        return frame
    else: # if there is no dataframe, create one
        DATA_DF = pd.DataFrame({
            'image_name': pd.Series(dtype='str'),
            'image_code': pd.Series(dtype='str'),
            'image_keywords': pd.Series(dtype='str'),
            'image_features':pd.Series(dtype='str'),
            'image_access':pd.Series(dtype='str'),
            'user_pass':pd.Series(dtype='str'),
            'unique_uuid':pd.Series(dtype='str')
        })
        return DATA_DF

def encrypt_file(image_path, image_format):
    '''
    Converts image to encrypted code
    :param image_path: filepath from which image was obtained
    :param image_format: file extension as a String 
    :return: encrypted image
    ''' 
    F = Fernet(get_key()) 
    image = cv2.imread(image_path)
    img_encode = cv2.imencode('.'+image_format, image)[1].tobytes() #TODO check if tobytes() is actually being called
    encrypted = F.encrypt(img_encode)
    return encrypted

def image_data(image_path):
    '''
    Requests or generates a unique name, encode, kewords, 
    and features for each image. Populates them into dataframe values.
    :param image_path: filepath of the image 
    '''
    filename, file_format = os.path.splitext(image_path)
    filename = os.path.basename(filename)
    
    # encrypt the image
    image_code = encrypt_file(image_path, file_format)
    image_access = 'private' #default
    
    # get features from the user
    print('Image found: ' + filename)
    
    # Get image keywords, process to remove unneccesary spaces
    image_keywords = get_input("Enter the relavant keywords about this image (separate with ','): ").split(',')
    for i in range(len(image_keywords)):
        image_keywords[i] = image_keywords[i].strip() # removes spaces on frotn and back of string
    image_keywords = ",".join(image_keywords)
    
    # get image permission from the user
    permission = get_input("Do you want to store this image as a public image (y/n): ").lower().strip()
    while permission != 'y' and permission != 'n':
        if permission == 'y':
            image_access = 'public'
        elif permission == 'n':
            image_access = 'private'
        else:
            permission = get_input("Do you want to store this image as a public image (y/n): ").lower()

    unique_uuid = uuid.uuid4() # generate unique UUID (for future MySQL database implementation)
    
    # Process same as image_keywords
    image_features = get_input("Please list any features of the image (separate with ','): ").split(',')
    for i in range(len(image_features)):
        image_features[i] = image_features[i].strip()
    image_features = ",".join(image_features)
    user_pass = "12345"
    
    ### TODO in the future add an "auto naming & auto featuring" function via extracting image features 
    ### TODO with image processing algorithms (ML) here

    return {
        "image_name": filename, 
        "image_code": image_code, 
        "image_keywords": image_keywords, 
        "image_features": image_features, 
        "image_access": image_access, 
        "user_pass": user_pass,
        "unique_uuid": unique_uuid
    }

def store_images(directory):
    '''
    Stores image(s) in the database by loading the image (via filepath),
    converting it to a dictionary of values, appends the dictionary to 
    the Pandas Dataframe, and writes Dataframe to a csv file.
    :param directory: current directory from which user wants to upload images
    '''
    IMAGE_FORMATS = ['.bmp', '.jpeg', '.jpg', '.png', '.tiff']

    DATA_DF = get_dataframe()
    
    # Check if the directory is a file or a directory
    files = glob.glob(os.path.join(directory,'*')) # glob searches over every file in the directory that the user entered
    
    if os.path.isfile(directory):
        files = [directory]

    for file in files:
        extension = os.path.splitext(file)
        if not extension[1] in IMAGE_FORMATS: #is this one of the image formats we want
            continue
        
        filename = os.path.basename(extension[0])
        if DATA_DF is not None and DATA_DF['image_name'].str.contains(filename).any():
            continue

        DATA_DF = DATA_DF.append([image_data(file)]) # create a List of the image data

    DATA_DF.to_csv(DATA_FILENAME)

def search_images(column):
    '''
    Searches the database for the image keywords entered by the user by 
    comparing the existing keywords with the keywords searched. 
    :return: images whose keywords correspond to keywords searched
    '''
    DATA_DF = get_dataframe()
    keyword_search = get_input("Please enter the keywords(s) that you want to search (separate with ','): ").lower().split(',')
    images_found = []
    
    keyword_list = DATA_DF[column].to_list()
    for i in range(len(keyword_list)):
        keywords = keyword_list[i].split(',')
        for keyword in keyword_search:
            keyword_strip = keyword.strip()
            if keyword_strip in keywords:
                images_found.append(DATA_DF.iloc[i])
                break
    
    return images_found   

def main():
    '''
    Program logic first requests a directory path from the user
    (or using current directory) and then requests a mode of 
    search, store, or exit. 
    '''
    while True:
        directory = get_input('Enter directory path (if you want the current directory press Enter): ')
        if directory == '': # if user doesn't enter a directory
            directory = os.getcwd() # ow.getcwd() returns current directory user is functioning in (output of pwd)
            
        if os.path.exists(directory):
            break
        
        print('You did not enter an appropriate directory, please try again.')
            
    while True:
        print("Menu")
        print("1. Store images in directory")
        print("2. Search images by keyword")
        print("3. Search images by feature")
        print("q. Quit")
        phase = get_input().lower().strip()
        if phase == '1':
            store_images(directory)
        elif phase == '2':
            print(search_images('image_keywords'))
        elif phase == '3':
            print(search_images('image_features'))
        elif phase == 'q':
            sys.exit()

# main guard
if __name__ == '__main__':
    main()
