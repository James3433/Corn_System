import os
import pandas as pd
from supabase import create_client

# # Supabase credentials
# url = 'https://kuatxxlypaanlqqlnbyq.supabase.co'
# key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1YXR4eGx5cGFhbmxxcWxuYnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI2Nzk5MDIsImV4cCI6MjAzODI1NTkwMn0.LHKU3A9Usqfz3TLDA0ONp6JiULfIsw0nY7d1JKtkAOc'
# supabase = create_client(url, key)

# Supabase credentials
url = 'https://tejmfmrngcqvwempifkf.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlam1mbXJuZ2NxdndlbXBpZmtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjY5OTMyNjQsImV4cCI6MjA0MjU2OTI2NH0.ANyif_Z9rudaK2pH7XNF7B11T-D2eno11yatvWZZpGU'
supabase = create_client(url, key)




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



def get_white_davao_region_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 1).eq('province_id', 1).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 1).eq('province_id', 1).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 1).eq('province_id', 1).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 1).eq('province_id', 1).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)

    return merged_dataset

    

def get_white_davao_de_oro_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 1).eq('province_id', 2).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 1).eq('province_id', 2).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 1).eq('province_id', 2).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 1).eq('province_id', 2).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    

def get_white_davao_del_norte_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 1).eq('province_id', 3).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 1).eq('province_id', 3).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 1).eq('province_id', 3).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 1).eq('province_id', 3).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    

def get_white_davao_del_sur_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 1).eq('province_id', 4).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 1).eq('province_id', 4).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 1).eq('province_id', 4).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 1).eq('province_id', 4).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    

def get_white_davao_oriental_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 1).eq('province_id', 5).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 1).eq('province_id', 5).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 1).eq('province_id', 5).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 1).eq('province_id', 5).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    

def get_white_davao_city_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 1).eq('province_id', 6).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 1).eq('province_id', 6).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 1).eq('province_id', 6).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 1).eq('province_id', 6).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    




def get_yellow_davao_region_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 2).eq('province_id', 1).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 2).eq('province_id', 1).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 2).eq('province_id', 1).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 2).eq('province_id', 1).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    

def get_yellow_davao_de_oro_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 2).eq('province_id', 2).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 2).eq('province_id', 2).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 2).eq('province_id', 2).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 2).eq('province_id', 2).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    

def get_yellow_davao_del_norte_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 2).eq('province_id', 3).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 2).eq('province_id', 3).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 2).eq('province_id', 3).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 2).eq('province_id', 3).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    

def get_yellow_davao_del_sur_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 2).eq('province_id', 4).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 2).eq('province_id', 4).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 2).eq('province_id', 4).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 2).eq('province_id', 4).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    

def get_yellow_davao_oriental_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 2).eq('province_id', 5).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 2).eq('province_id', 5).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 2).eq('province_id', 5).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 2).eq('province_id', 5).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    

def get_yellow_davao_city_dataset():
    response_1 = supabase.table('corn_production_data').select('*').eq('corn_type', 2).eq('province_id', 6).execute()
    response_2 = supabase.table('fertilizer_data').select('*').eq('corn_type', 2).eq('province_id', 6).execute()
    response_3 = supabase.table('weather_data').select('*').eq('corn_type', 2).eq('province_id', 6).execute()
    response_4 = supabase.table('corn_price_data').select('*').eq('corn_type', 2).eq('province_id', 6).execute()

    response_1 = pd.DataFrame(response_1.data)
    response_2 = pd.DataFrame(response_2.data)
    response_3 = pd.DataFrame(response_3.data)
    response_4 = pd.DataFrame(response_4.data)

    # Merge datasets on 'user_id' (or another common key)
    merged_dataset = pd.merge(response_1, response_2)
    merged_dataset = pd.merge(merged_dataset, response_3)
    merged_dataset = pd.merge(merged_dataset, response_4)
    merged_dataset = merged_dataset.drop(['id', 'province_id', 'user_id', 'corn_type'], axis=1)
    
    return merged_dataset
    








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
            'wholesale_corngrits_price': float(row['wholesale_corngrits_price']),  # Assuming this column exists
            'user_id': user_id  # Pass the user ID as needed
        })

    
    response = supabase.table('corn_price_data').insert(data_to_insert).execute()



def submit_predictions_production(predictions_df, user_id, corn_type):
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
            'temp': float(row['temp']),  # Assuming this column exists
            'dew': float(row['dew']),  # Assuming this column exists
            'humidity': float(row['humidity']),  # Assuming this column exists
            'precip': float(row['precip']),  # Assuming this column exists
            'precipprob': float(row['precipprob']),  # Assuming this column exists
            'precipcover': float(row['precipcover']),  # Assuming this column exists
            'windgust': float(row['windgust']),  # Assuming this column exists
            'windspeed': float(row['windspeed']),  # Assuming this column exists
            'sealevelpressure': float(row['sealevelpressure']),  # Assuming this column exists
            'visibility': float(row['visibility']),  # Assuming this column exists
            'solarradiation': float(row['solarradiation']),  # Assuming this column exists
            'uvindex': float(row['uvindex']),  # Assuming this column exists
            'severerisk': float(row['severerisk']),  # Assuming this column exists
            'cloudcover': float(row['cloudcover']),  # Assuming this column exists
            'conditions': float(row['conditions']),  # Assuming this column exists
            'user_id': user_id  # Pass the user ID as needed
        })

    
    response = supabase.table('weather_data').insert(data_to_insert).execute()

