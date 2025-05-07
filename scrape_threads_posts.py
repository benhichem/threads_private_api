import undetected_chromedriver as uc 
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd
import random

posts_data = []
def scroll_and_collect_posts(driver, max_scrolls = 50):
    scroll_count = 0
    no_new_posts_count = 0

    while scroll_count < max_scrolls:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(random.randint(7,10))  # Wait for content to load
        scroll_count += 1
          # Find posts
        try:
            posts = driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/div[2]/div[2]/div/div/div/div[1]/div[1]/div/div/div[2]/div[1]/div[4]/div/div[1]/div")
        except Exception as e:
            print(f"Error finding posts: {e}")
            continue

        # Check if we found any posts
        if len(posts) == 0:
            print("No posts found, stopping")
            break

        # Get the current post count
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
        for post in new_posts:
            try:
                post_text = post.text.split("\n")
                
                # Make sure we have enough elements in the split result
                if len(post_text) >= 3:
                    caption = post_text[2]
                    date = post_text[1]
                    
                    data = {
                        "caption": caption,
                        "date": date
                    }
                    
                    posts_data.append(data)
                    print(f"Added post: {data['date'][:10]}... - {data['caption'][:20]}...")
                else:
                    print(f"Post text format unexpected: {post_text}")
            except Exception as e:
                print(f"Error processing post: {e}")
                
        print(f"Total posts collected: {len(posts_data)}")

    return posts_data 

def scrapeProfilePosts(username):
    driver = uc.Chrome(headless=False, use_subprocess=False, version_main=135, user_data_dir="profile1")
    # sleep(50000)
    driver.get(f'https://www.threads.net/@{username}')
    fn = f"var/posts/{username}.csv"
    psts = scroll_and_collect_posts(driver, 50)
    print(psts)
    df = pd.DataFrame(psts)
    df.to_csv(fn, index=True)

        
         

    print(posts_data)

def main():
    scrapeProfilePosts("puppiwii")
    return
if __name__ == "__main__":
    main()
