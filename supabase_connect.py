import os
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
    response_1 = supabase.table('davao_oriental_white_corn_price').select('*').execute()
    response_2 = supabase.table('davao_city_white_corn_price').select('*').execute()
    response_3 = supabase.table('davao_de_oro_white_corn_price').select('*').execute()
    response_4 = supabase.table('davao_del_norte_white_corn_price').select('*').execute()
    response_5 = supabase.table('davao_del_sur_white_corn_price').select('*').execute()
    return response_1.data, response_2.data, response_3.data, response_4.data, response_5.data

def get_yellow_corn_price():
    response_1 = supabase.table('davao_oriental_yellow_corn_price').select('*').execute()
    response_2 = supabase.table('davao_city_yellow_corn_price').select('*').execute()
    response_3 = supabase.table('davao_de_oro_yellow_corn_price').select('*').execute()
    response_4 = supabase.table('davao_del_norte_yellow_corn_price').select('*').execute()
    response_5 = supabase.table('davao_del_sur_yellow_corn_price').select('*').execute()
    return response_1.data, response_2.data, response_3.data, response_4.data, response_5.data

def insert_user(fname, mname, lname, age, gender, type, hashed_password):
    data = {
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