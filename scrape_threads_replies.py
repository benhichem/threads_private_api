import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd
import random
import sys

posts_data = []
def scroll_and_collect_posts(driver,max_scrolls = 100):
    scroll_count = 0
    no_new_posts_count = 0

    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(random.randint(7,10))
        scroll_count += 1
        
        try: 
            posts= driver.find_elements(By.XPATH,"/html/body/div[2]/div/div/div[2]/div[2]/div/div/div/div[1]/div[1]/div/div/div[2]/div[1]/div[4]/div/div[1]/div")

        except Exception as e:
            print(f"Error finding posts: {e}")
            continue

        if(len(posts) ==0):
            print('No posts found, stopping')
            break

        current_post_count = len(posts_data)
               # Check if we have new posts
        if len(posts) <= current_post_count:
            no_new_posts_count += 1
            print(f"No new posts found after scroll ({no_new_posts_count}/3)")
            
            # If we haven't found new posts in 3 consecutive scrolls, stop
            if no_new_posts_count >= 3:
                print("No new posts after 3 scrolls, stopping")
                break
            continue
     # Reset the counter since we found new posts
        no_new_posts_count = 0

        # Get only the new posts (posts we haven't processed yet)
        new_posts = posts[current_post_count:]
        print(f"Found {len(new_posts)} new posts")
           # Process each new post
        for reply_container in new_posts:
            try: 
               
               reply_inner_container = reply_container.find_element(By.TAG_NAME, "div") 
               child_nodes = driver.execute_script("""
               var nodes = arguments[0].childNodes; 
               let results = []
               for (var i = 0; i< nodes.length; i++){
                    let x = nodes[i]
                    console.log(x.innerText)
                    results.push(x.innerText)
               }
               return results
               """, reply_inner_container) 

               if len(child_nodes) < 2 : continue 

               split_replied_to = child_nodes[0].split('\n')
               split_reply = child_nodes[1].split('\n')

              
               if len(split_replied_to) > 2 and len(split_reply) > 2:
                    person = split_replied_to[0]
                    caption = split_replied_to[3]
                    date = split_replied_to[1]

                    reply_caption = split_reply[2]
                    date = split_reply[1]

                    data = {
                        "original_post_owner": person,
                        "original_post_caption": caption,
                        "original_post_creation": date,
                        "reply_caption": reply_caption,
                        "reply_date": date
                    }
                    posts_data.append(data) 
               
                
            
            except Exception as e:
                # print(f"Error finding inner container for replies")
                print(e)
                pass
                
        print(f"Total posts collected: {len(posts_data)}")



    return

def scrapeProfileReplies(url:str):
    driver = uc.Chrome(headless=False, use_subprocess=False, version_main=135, user_data_dir="profile1")
    # sleep(50000)
    driver.get(url)
    scroll_and_collect_posts(driver, 50)
    return
   



def main():
    if(len(sys.argv) <2):
        print('Usage: python scrape_threads_replies.py <username>')
        return

    username = sys.argv[1] 
    url = f"https://www.threads.com/@{username}/replies"
    fn = f"var/replies/{username}.csv"
    scrapeProfileReplies(url)
    df = pd.DataFrame(posts_data)
    df.to_csv(fn, index=True)
    return

if __name__ == "__main__":
    main()
