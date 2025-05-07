import requests 
from dotenv import load_dotenv 
import os 
import json 
load_dotenv()
token = os.getenv("RAPIDAPIKEY")

print(token)
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
            return None
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    followers = get_followers(63451528020,"20")
    print(followers)

