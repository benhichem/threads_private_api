import requests 
import os
import sys
import json
import pandas as pd
import logging
from dotenv import load_dotenv

from decorators import retry_on_exception


logging.basicConfig(level=logging.INFO)
load_dotenv()

token = os.getenv('RAPIDAPIKEY')

@retry_on_exception(max_tries=3)
def get_user_id(user:str):
    url = "https://threads-api4.p.rapidapi.com/api/user/info"
    querystring = {"username":user}
    headers = {
        "x-rapidapi-Key": token,
        "x-rapidapi-Host": "threads-api4.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    print(response.text) 
    if(response.status_code ==200):
        try:
            data = response.json()
            user_id = data["data"]["user"]["id"]
            followers_count = data['data']["user"]["follower_count"]
            return {"user_id": user_id, "followers_count":followers_count} 
        except json.JSONDecodeError:
            print("Response was not valid JSON. Raw content:")
            print(response.text)
            raise Exception('Failed to fetch user id')
    else:
        print("Error: ", response.status_code)
        print(response.json())
        raise Exception('Failed to fetch user id')


@retry_on_exception(max_tries=3)
def get_followers(user_id, end_cursor=None):
    """
    Fetch followers for a Threads user
    
    Args:
        user_id (str): The user ID to get followers for
        end_cursor (str, optional): The pagination cursor. Defaults to None.
    
    
    """
    url = "https://threads-api4.p.rapidapi.com/api/user/followers"
    
    # Start with required parameters
    querystring = {"user_id": user_id}
    
    # Add end_cursor parameter only if provided
    if end_cursor:
        querystring["end_cursor"] = end_cursor
    
    headers = {
        'x-rapidapi-key': token,
        'x-rapidapi-host': "threads-api4.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    print(response.text)

    # Check if request was successful
    if response.status_code == 200:
        try:
            # Parse JSON response
            data = response.json()
            followers = data["data"]["user"]['followers']['edges']
            has_next_page = data['data']["user"]['followers']['page_info']['has_next_page']            
            end_cursor_res = data['data']['user']['followers']['page_info']['end_cursor']
            return {"followers":followers, "has_next_page":has_next_page, "end_cursor":end_cursor_res}

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Raw response: {response.text}")
            raise Exception("Failed to parse JSON response")
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        raise Exception("Failed to fetch followers")

def scrape_followers(input_value):
    user = get_user_id(input_value)
    print(user)
    if not user:
        print(f"Failed to get user_id for {input_value}")
        return
    user_id = user["user_id"]
    
    print(f"Scraping followers for user_id: {user_id}")
    next_max_id = None
    followers_data = []
    followers_count = None
    fn = f"var/followers/{user_id}.csv"
    
    while True:
        res = get_followers(user_id, next_max_id)
        if not res:
            print("Failed to fetch followers.")
            break
        
        if not followers_count:
            print("Fetching followers count...")
            followers_count = user["followers_count"]  # Fixed: user instead of user_id
            logging.info(f"Total followers: {followers_count}")
        
        followers = res['followers']
        next_max_id = res['end_cursor']
        logging.info(f"Got {len(followers)} followers, next_max_id: {next_max_id}")
        
        for follower in followers:
            data = {
                "id": follower['node']['id'],
                "pk": follower['node']['pk'],  # Fixed: follower instead of followers
                "username": follower['node']['username'],
                "full_name": follower['node']['full_name'],
                "is_verified": follower['node']['is_verified'],
                "follower_count":follower['node']["follower_count"]
            }
            followers_data.append(data)
        
        df = pd.DataFrame(followers_data)
        df.to_csv(fn, index=False)
        print(df)
        
        # Only break after processing the current batch
        if not res.get('has_next_page'):
            print("No more followers to fetch.")
            break
      
    return followers_data

def main():
    if(len(sys.argv) <2):
        print('Usage: python scrape_followers_rapidapi.py <username>')
        return
    input_value = sys.argv[1]
    scrape_followers(input_value)

if __name__ == "__main__":
    main()
