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


def get_white_corn_price():
    response = supabase.table('white_corn_price').select('*').execute()
    white_corn_df = pd.DataFrame(response.data)
    response_1 = white_corn_df[white_corn_df['region_id'] == 1]
    response_2 = white_corn_df[white_corn_df['region_id'] == 2]
    response_3 = white_corn_df[white_corn_df['region_id'] == 3]
    response_4 = white_corn_df[white_corn_df['region_id'] == 4]
    response_5 = white_corn_df[white_corn_df['region_id'] == 5]

    return response_1, response_2, response_3, response_4, response_5

def get_yellow_corn_price():
    response = supabase.table('yellow_corn_price').select('*').execute()
    yellow_corn_df = pd.DataFrame(response.data)
    response_1 = yellow_corn_df[yellow_corn_df['region_id'] == 1]
    response_2 = yellow_corn_df[yellow_corn_df['region_id'] == 2]
    response_3 = yellow_corn_df[yellow_corn_df['region_id'] == 3]
    response_4 = yellow_corn_df[yellow_corn_df['region_id'] == 4]
    response_5 = yellow_corn_df[yellow_corn_df['region_id'] == 5]

    return response_1, response_2, response_3, response_4, response_5

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
    response = supabase.table('users').select('fname','lname').eq('id', id).execute()
    if response.data:
        user = response.data[0] # Get the first user found
        return user['fname'], user['lname']
    return None

def get_all_comments():
    response = supabase.table('comments').select('user_id', 'comments').execute()  # Select all first and last names
    if response.data:
        data = [(data['user_id'], data['comments']) for data in response.data]  # List of tuples (fname, lname)
        return data
    return None