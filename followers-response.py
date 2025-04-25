# import os 
# from dotenv import load_dotenv
# from rocketapi import InstagramAPI, ThreadsAPI
#

#
# ig_api = InstagramAPI(token)
# threads_api = ThreadsAPI(token)
#
# # res = threads_api.search_users(query='chloeebellaxoxo')
# # print(res)
#
#
# # res2 = threads_api.get_user_info(73924904629)
# res3 = threads_api.get_user_followers(73924904629)
# print(res3)
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('ROCKETAPI_TOKEN')

from rocketapi import ThreadsAPI

# Initialize the API client with your token
threads_api = ThreadsAPI(token=token)

# Replace with the username you want to check
username = "jimmy_neutronss"

# Get the user ID first
user = threads_api.get_user_info(username)
user_id = user['id']

# Fetch followers
# followers = threads_api.get_followers(user_id)
#


followers = threads_api.get_user_followers(user_id)

# Print follower usernames
for follower in followers['users']:
    print(follower['username'])
