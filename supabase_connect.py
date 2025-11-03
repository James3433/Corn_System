import os
import io
import joblib
import httpx
import pandas as pd
import streamlit as st

from PIL import Image
from supabase import create_client

# # Supabase credentials
# url = 'https://kuatxxlypaanlqqlnbyq.supabase.co'
# key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1YXR4eGx5cGFhbmxxcWxuYnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI2Nzk5MDIsImV4cCI6MjAzODI1NTkwMn0.LHKU3A9Usqfz3TLDA0ONp6JiULfIsw0nY7d1JKtkAOc'
# supabase = create_client(url, key)

# Supabase credentials
url = "https://hedpecluzdcgxfoyzilf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlZHBlY2x1emRjZ3hmb3l6aWxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExOTY0MzYsImV4cCI6MjA3Njc3MjQzNn0.ZozpjOCqXNR9hZwCUt0cELF95MOvtIpMVmaw76oJ4Lw"

supabase = create_client(url, key)

bucket_name = "predictormodels"



def get_corn_price(corn_type, province_id):
    response = supabase.table('corn_price_data').select('*').eq('corn_type', corn_type).eq('province_id', province_id).execute()

    response = pd.DataFrame(response.data)

    if corn_type == 1:
        response = response.drop(['id', 'province_id', 'corn_type', 'retail_corngrains_price'], axis=1)

    elif corn_type == 2:
        response = response.drop(['id', 'province_id', 'corn_type', 'retail_corngrits_price'], axis=1)

    return response





def count_id():
    response = supabase.table('users').select('id').execute()
    if response.data:
        return len(response.data)
    return 0 

def insert_user(fname, mname, lname, age, type, gender, hashed_password):
    count = supabase.table('users').select('id').execute()
    if count.data:
        id = len(count.data)+1
    else:
        id = 1 

    data = {
        "id": id,
        "fname": fname,
        "mname": mname,
        "lname": lname,
        "age": age,
        "gender": gender,
        "user_type": type,
        "password": hashed_password
    }
    
    response = supabase.table('users').insert(data).execute()
    return response

def insert_comments(user_id, comments):
    data = {
        "user_id": user_id,
        "comments": comments
    }
    response = supabase.table('comments').insert(data).execute()
    return response

def user_exists(fname, mname, lname):
    # Query the database to check if the user already exists
    response = supabase.table('users').select('*').eq('fname', fname).eq('mname', mname).eq('lname', lname).execute()
    
    # If the data is not empty, the user exists
    return len(response.data) > 0

def get_user_by_name(fname, lname):
    response = supabase.table('users').select('*').eq('fname', fname).eq('lname', lname).execute()
    if response.data:
        user = response.data[0] # Get the first user found
        return user 
    return None

def get_user_id(fname, lname):
    response = supabase.table('users').select('id').eq('fname', fname).eq('lname', lname).execute()
    if response.data:
        user = response.data[0] # Get the first user found
        return user['id']
    return None

def get_user_name(id):
    response = supabase.table('users').select('fname','lname', 'user_type').eq('id', id).execute()
    if response.data:
        user = response.data[0] # Get the first user found
        return user['fname'], user['lname'], user['user_type']
    return None

def get_all_comments():
    response = supabase.table('comments').select('user_id', 'comments').execute()  # Select all first and last names
    if response.data:
        data = [(data['user_id'], data['comments']) for data in response.data]  # List of tuples (fname, lname)
        return data
    return None


def get_user_by_user_type(user_type):
    response = supabase.table('users').select('id, fname, mname, lname').eq('user_type', user_type).execute()
    if response.data:
        usernames = [f"{data['fname']} {data['mname']} {data['lname']} = {data['id']}" for data in response.data]  # List of tuples (id, fname, mname, lname)
        return usernames
    return None


def get_unique_years():
    response = supabase.table('fertilizer_data').select('*').eq('corn_type', 1).eq('province_id', 1).execute()
    years = [row['year'] for row in response.data]
    unique_years = sorted(set(years))
    # print(unique_years)
    return unique_years




def get_fertilizer_data():
    response = supabase.table('fertilizer_data').select('*').gte('year', 2020).execute()

    return response.data



def get_white_corn_price_data():
    response = supabase.table('corn_price_data').select('*').eq('corn_type', 1).gte('year', 2020).execute()

    return response.data



def get_yellow_corn_price_data():
    response = supabase.table('corn_price_data').select('*').eq('corn_type', 2).gte('year', 2020).execute()

    return response.data



def get_white_corn_production_data():
    response = supabase.table('corn_production_data').select('*').eq('corn_type', 1).gte('year', 2020).execute()

    return response.data



def get_yellow_corn_production_data():
    response = supabase.table('corn_production_data').select('*').eq('corn_type', 2).gte('year', 2020).execute()

    return response.data



def get_weather_data():
    response = supabase.table('weather_data').select('*').gte('year', 2020).execute()

    return response.data






def get_fertilizer_dataset():
    response = supabase.table('fertilizer_data').select('*').limit(5000).execute()
    print(response.count)  # Total rows available in the table (if supported)
    print(len(response.data))  # Number of rows fetched
    response = pd.DataFrame(response.data)

    return response

def get_corn_price_dataset():
    response = supabase.table('corn_price_data').select('*').limit(5000).execute()
    response = pd.DataFrame(response.data)

    return response

def get_corn_production_dataset():
    response = supabase.table('corn_production_data').select('*').limit(5000).execute()
    response = pd.DataFrame(response.data)

    return response

def get_weather_dataset():
    response = supabase.table('weather_data').select('*').limit(5000).execute()
    response = pd.DataFrame(response.data)

    return response



def get_white_davao_region_dataset(id):
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 1).eq('province_id', id).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 1).eq('province_id', id).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 1).eq('province_id', id).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 1).eq('province_id', id).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type', 'retail_corngrains_price'], axis=1)

    return merged_dataset

    

def get_yellow_davao_region_dataset(id):
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 2).eq('province_id', id).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 2).eq('province_id', id).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 2).eq('province_id', id).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 2).eq('province_id', id).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type', 'retail_corngrits_price'], axis=1)
    
    return merged_dataset
    




def get_production_dataset_for_edit(month, year, province_id):
    w_response = supabase.table('corn_production_data').select('*').eq('corn_type', 1).eq('month', month).eq('year', year).eq('province_id', province_id).execute()
    y_response = supabase.table('corn_production_data').select('*').eq('corn_type', 2).eq('month', month).eq('year', year).eq('province_id', province_id).execute()
    
    w_production = w_response.data[0]['corn_production']
    y_production = y_response.data[0]['corn_production']

    return w_production, y_production


def get_fertilizer_dataset_for_edit(month, year, province_id):
    w_response = supabase.table('fertilizer_data').select('*').eq('corn_type', 1).eq('month', month).eq('year', year).eq('province_id', province_id).execute()

    return (w_response.data[0]['ammophos_price'], 
            w_response.data[0]['ammosul_price'], 
            w_response.data[0]['complete_price'], 
            w_response.data[0]['urea_price'])


def get_weather_dataset_for_edit(month, year, province_id):
    w_response = supabase.table('weather_data').select('*').eq('corn_type', 1).eq('month', month).eq('year', year).eq('province_id', province_id).execute()

    return (
    w_response.data[0]['feelslike'],
    w_response.data[0]['dew'],
    w_response.data[0]['humidity'],
    w_response.data[0]['precip'],
    w_response.data[0]['precipcover'],
    w_response.data[0]['windgust'],
    w_response.data[0]['windspeed'],
    w_response.data[0]['winddir'],
    w_response.data[0]['sealevelpressure'],
    w_response.data[0]['visibility'],
    w_response.data[0]['severerisk'],
    w_response.data[0]['conditions'])
            

def get_price_dataset_for_edit(month, year, province_id):
    w_response = supabase.table('corn_price_data').select('*').eq('corn_type', 1).eq('month', month).eq('year', year).eq('province_id', province_id).execute()
    y_response = supabase.table('corn_price_data').select('*').eq('corn_type', 2).eq('month', month).eq('year', year).eq('province_id', province_id).execute()

    return (w_response.data[0]['farmgate_corngrains_price'], 
            w_response.data[0]['retail_corngrits_price'], 
            w_response.data[0]['wholesale_corngrits_price'], 
            w_response.data[0]['wholesale_corngrains_price'],
            y_response.data[0]['farmgate_corngrains_price'], 
            y_response.data[0]['retail_corngrains_price'], 
            y_response.data[0]['wholesale_corngrits_price'], 
            y_response.data[0]['wholesale_corngrains_price'])





def submit_predictions_fertilizer(predictions_df, user_id):
    # Prepare data for insertion
    data_to_insert = []
    
    for index, row in predictions_df.iterrows():
        data_to_insert.append({
            'year': int(row['year']),  # Assuming 'Year' is a column in predictions_df
            'month': int(row['month']),  # Assuming 'Month' is a column in predictions_df
            'province_id': int(row['province_id']),  # Assuming 'province_id' is already included
            'corn_type': int(row['corn_type']),  # Assuming 'corn_type' is already included
            'ammophos_price': float(row['ammophos_price']),  # Assuming this column exists
            'ammosul_price': float(row['ammosul_price']),  # Assuming this column exists
            'complete_price': float(row['complete_price']),  # Assuming this column exists
            'urea_price': float(row['urea_price']),  # Assuming this column exists
            'user_id': user_id  # Pass the user ID as needed
        })

   
    response = supabase.table('fertilizer_data').insert(data_to_insert).execute()





def submit_predictions_price(predictions_df, user_id):
    # Prepare data for insertion
    data_to_insert = []
    
    for index, row in predictions_df.iterrows():
        data_to_insert.append({
            'year': int(row['year']),  # Assuming 'Year' is a column in predictions_df
            'month': int(row['month']),  # Assuming 'Month' is a column in predictions_df
            'province_id': int(row['province_id']),  # Assuming 'province_id' is already included
            'corn_type': int(row['corn_type']),  # Assuming 'corn_type' is already included
            'farmgate_corngrains_price': float(row['farmgate_corngrains_price']),  # Assuming this column exists
            'retail_corngrits_price': float(row['retail_corngrits_price']),  # Assuming this column exists
            'retail_corngrains_price': float(row['retail_corngrains_price']),  # Assuming this column exists
            'wholesale_corngrits_price': float(row['wholesale_corngrits_price']),  # Assuming this column exists
            'wholesale_corngrains_price': float(row['wholesale_corngrains_price']),  # Assuming this column exists
            'user_id': user_id  # Pass the user ID as needed
        })

    
    response = supabase.table('corn_price_data').insert(data_to_insert).execute()



def submit_predictions_production(predictions_df, user_id):
    # Prepare data for insertion
    data_to_insert = []
    
    for index, row in predictions_df.iterrows():
        data_to_insert.append({
            'year': int(row['year']),  # Assuming 'Year' is a column in predictions_df
            'month': int(row['month']),  # Assuming 'Month' is a column in predictions_df
            'province_id': int(row['province_id']),  # Assuming 'province_id' is already included
            'corn_type': int(row['corn_type']),  # Assuming 'corn_type' is already included
            'corn_production': float(row['corn_production']),  # Assuming this column exists
            'user_id': user_id  # Pass the user ID as needed
        })


    response = supabase.table('corn_production_data').insert(data_to_insert).execute()


def submit_predictions_weather(predictions_df, user_id):
    # Prepare data for insertion
    data_to_insert = []
    
    for index, row in predictions_df.iterrows():
        data_to_insert.append({
            'year': int(row['year']),  # Assuming 'Year' is a column in predictions_df
            'month': int(row['month']),  # Assuming 'Month' is a column in predictions_df
            'province_id': int(row['province_id']),  # Assuming 'province_id' is already included
            'corn_type': int(row['corn_type']),  # Assuming 'corn_type' is already included
            'feelslike': float(row['feelslike']),  # Assuming this column exists
            'dew': float(row['dew']),  # Assuming this column exists
            'humidity': float(row['humidity']),  # Assuming this column exists
            'precip': float(row['precip']),  # Assuming this column exists
            'precipcover': float(row['precipcover']),  # Assuming this column exists
            'windgust': float(row['windgust']),  # Assuming this column exists
            'windspeed': float(row['windspeed']),  # Assuming this column exists
            'winddir': float(row['winddir']),  # Assuming this column exists
            'sealevelpressure': float(row['sealevelpressure']),  # Assuming this column exists
            'visibility': float(row['visibility']),  # Assuming this column exists
            'severerisk': float(row['severerisk']),  # Assuming this column exists
            'conditions': int(row['conditions']),  # Assuming this column exists
            'user_id': user_id  # Pass the user ID as needed
        })

    
    response = supabase.table('weather_data').insert(data_to_insert).execute()






def update_predictions_fertilizer(predictions_df, user_id):
    for index, row in predictions_df.iterrows():
        response = supabase.table('fertilizer_data')\
            .update({
                'ammophos_price': float(row['ammophos_price']),
                'ammosul_price': float(row['ammosul_price']),
                'complete_price': float(row['complete_price']),
                'urea_price': float(row['urea_price']),
                'user_id': user_id
            })\
            .eq('year', int(row['year']))\
            .eq('month', int(row['month']))\
            .eq('province_id', int(row['province_id']))\
            .eq('corn_type', int(row['corn_type']))\
            .execute()


def update_predictions_price(predictions_df, user_id):
    for index, row in predictions_df.iterrows():
        response = supabase.table('corn_price_data')\
            .update({
                'farmgate_corngrains_price': float(row['farmgate_corngrains_price']),
                'retail_corngrits_price': float(row['retail_corngrits_price']),  
                'retail_corngrains_price': float(row['retail_corngrains_price']),  
                'wholesale_corngrits_price': float(row['wholesale_corngrits_price']),  
                'wholesale_corngrains_price': float(row['wholesale_corngrains_price']),  
                'user_id': user_id
            })\
            .eq('year', int(row['year']))\
            .eq('month', int(row['month']))\
            .eq('province_id', int(row['province_id']))\
            .eq('corn_type', int(row['corn_type']))\
            .execute()


def update_predictions_production(predictions_df, user_id):
    for index, row in predictions_df.iterrows():
        response = supabase.table('corn_production_data')\
            .update({
                'corn_production': float(row['corn_production']),  # Assuming this column exists
                'user_id': user_id  # Pass the user ID as needed
            })\
            .eq('year', int(row['year']))\
            .eq('month', int(row['month']))\
            .eq('province_id', int(row['province_id']))\
            .eq('corn_type', int(row['corn_type']))\
            .execute()
        

def update_predictions_weather(predictions_df, user_id):
    for index, row in predictions_df.iterrows():
        response = supabase.table('weather_data')\
            .update({
                'feelslike': float(row['feelslike']), 
                'dew': float(row['dew']),  
                'humidity': float(row['humidity']), 
                'precip': float(row['precip']), 
                'precipcover': float(row['precipcover']), 
                'windgust': float(row['windgust']),  
                'windspeed': float(row['windspeed']),  
                'winddir': float(row['winddir']),  
                'sealevelpressure': float(row['sealevelpressure']),  
                'visibility': float(row['visibility']),  
                'severerisk': float(row['severerisk']),  
                'conditions': int(row['conditions']),  
                'user_id': user_id  
            })\
            .eq('year', int(row['year']))\
            .eq('month', int(row['month']))\
            .eq('province_id', int(row['province_id']))\
            .eq('corn_type', int(row['corn_type']))\
            .execute()





# Add and Update Model
def upload_model_to_supabase(model, storage_path):
    # Serialize model to bytes in memory
    bytes_buffer = io.BytesIO()
    joblib.dump(model, bytes_buffer)
    bytes_buffer.seek(0)  # Reset buffer position

    supabase.storage.from_("predictormodels").upload(storage_path, bytes_buffer.read(), file_options={"x-upsert": "true"})


    print(f"Model uploaded successfully:{storage_path}")



# Add and Update Forcested Predictors
def upload_csv_to_supabase(df, storage_path):
    # Convert DataFrame to CSV in-memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode()  # Encode to bytes
    
    supabase.storage.from_("predictormodels").upload(storage_path, csv_bytes, file_options={"x-upsert": "true"})


    print(f"Model uploaded successfully:{storage_path}")



# Add and Update Colorbar Png
def upload_png_to_supabase(colorbar_bytes, storage_path):
    supabase.storage.from_("predictormodels").upload(storage_path ,colorbar_bytes,file_options={"x-upsert": "true"})


    print(f"Png uploaded successfully:{storage_path}")








# Load Model
def load_joblib_from_supabase(storage_path):
    # Download file bytes
    try:
        response = supabase.storage.from_("predictormodels").download(storage_path)
    
    except Exception as e:
        print("Upload failed with exception:", e)
        return  # or handle error appropriately
    
    # Load model from bytes buffer
    bytes_buffer = io.BytesIO(response)
    model = joblib.load(bytes_buffer)
    
    return model


def load_csv_from_supabase(storage_path):
    # Download file bytes
    try:
        response = supabase.storage.from_("predictormodels").download(storage_path)
    
    except Exception as e:
        print("Upload failed with exception:", e)
        return  # or handle error appropriately  
  
    # Load CSV into DataFrame
    csv_buffer = io.StringIO(response.decode('utf-8'))
    df = pd.read_csv(csv_buffer)
    
    return df



def load_png_from_supabase(storage_path):
    # Download file bytes
    try:
        response = supabase.storage.from_("predictormodels").download(storage_path)
        return response  # raw bytes of the image

    except Exception as e:
        print("Upload failed with exception:", e)
        return  # or handle error appropriately 