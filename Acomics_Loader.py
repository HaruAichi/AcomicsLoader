#!/usr/bin/env python3

# Simple utility to get comics from acomics.ru.
# Developed by Aichi Haru
# Strongly violates authors "no download" right :)

# Version 0.5 (2023-10-29)

# --- Change log ---

# Version 0.5 (2023-10-29) - Ctrl-C: SIGINT handler added
# Version 0.4 (2023-10-29) - --new key added, some first-last page fixes
# Version 0.3 (2023-10-21) - ageRestrict cookie set to avoid content limitations
# Version 0.2 (2023-06-23) - --info key added
# Version 0.1 (2023-06-16) - Initial release

# --- Prerequisites ---

# 1. python3
# 2. beautifulsoup v4. Install like apt-get install python3-bs4, pip3 install beautifulsoup4 or somehow either
# 3. argparse module

import os,sys
import time
import bs4
import argparse
import requests
import signal

from urllib.parse import urlparse
from pathlib import Path

program_name = 'Acomics serial image grabber'
program_version = '0.5'

class container():
    def __str__(self):
        return(str({d : getattr(self,d) for d in self.__dict__}))

def get_parsed_page(url):
    reply = container()
    source = requests.get(url)
    if (source.status_code == 200):
        soup = bs4.BeautifulSoup(source.text, features="lxml")
        reply.error = False
        reply.parsed = soup
    else:     
        reply.error = True   
        reply.message = f'Cannot load data from {url}'
    return reply
    

def handle_ctrl_c(signum, frame):
    print(f"\nWarning: Interrupted by user request (Ctrl+C)\n")
    sys.exit(1)

# -[ The mainest main() ]-

def main():

    start_time = time.time()

    default_url_prefix = "https://acomics.ru"

    parser = argparse.ArgumentParser(description=f"{program_name} v.{program_version}")
    parser.add_argument('-i', '--info', dest='info', default=False, action='store_true', help="Show comics info")
    parser.add_argument('-n', '--new', dest='new', default=False, action='store_true', help="Download only new pages")
    parser.add_argument('-r', '--rewrite', dest='rewrite', default=False, action='store_true', help="Rewrite existing files")
    parser.add_argument('-b', '--first-page', type=int, dest='first_page', default=1, help="First page number")
    parser.add_argument('-e', '--last-page',  type=int, dest='last_page',  default=0, help="Last page number")
    parser.add_argument('URL', help='Comic URL https://acomics.ru/~NAME or just NAME')
    parser.add_argument('DIR',  nargs="?", help='Optional directory path')
    
    args = parser.parse_args()

    signal.signal(signal.SIGINT, handle_ctrl_c)

    # Phase 1: parse URL

    if args.URL[-1]=='/': args.URL = args.URL[0:-1] # Remove trailing /

    url = urlparse(args.URL)
    
    source_url = f"{args.URL}" if (url.scheme == 0) else f"{default_url_prefix}/~{args.URL}" # Starting HTML link
    url_prefix = f"{url.scheme}://{url.netloc}" if url.scheme else default_url_prefix          # URL prefix for image download
    
    print(f"{program_name} v.{program_version}\n\nLoading comic data from {source_url}")
    
    dir_name = args.DIR if args.DIR else url.path.replace('~','')

    # Prefetch comic parameters
    page = get_parsed_page(source_url)    
    if page.error:
        print(f"Error: {page.message}")
        sys.exit(1)

    comic = page.parsed

    error_techinfo = comic.find('section',{'class':'errorTechInfo'})
    comic_title    = comic.find('meta', {'property':'og:title'}).get('content')
    comic_desc     = comic.find('meta', {'property':'og:description'}).get('content')
    first_page     = int(comic.find('a', {'class':'read1'}).get('href').split('/')[-1])
    last_page      = int(comic.find('a', {'class':'read2'}).get('href').split('/')[-1])

    if error_techinfo:
        print(f"Error: No comic found at {source_url}")
        sys.exit(1)

    description_text = f"""
    Comic title: {comic_title}
    Description: {comic_desc}
    Number of pages: {last_page - first_page + 1}
    URL: {source_url}
    Download date: {time.ctime()}
    """
    
    print(f"\n{description_text}\n")

    if args.info: sys.exit() # Just show summary

    # Create comic directory and descriprion

    Path(dir_name).mkdir(parents=True, exist_ok=True) # Make dir
    desc_file = f"{dir_name}/description-{comic_title}.txt"
    open(desc_file,'w').write(description_text)
    
    if args.first_page: first_page = min(args.first_page, last_page)
    if args.last_page: last_page = min(last_page, args.last_page)

    if args.new: # Take number of last loaded page
        pages = os.listdir(dir_name)
        max_page = 1
        for page in pages:
            p = page.split('-')
            if p[0] == 'page' and len(p) > 1:
                try:
                    n = int(p[1])
                    if n > max_page: max_page = n
                except: pass
        first_page = min(max_page+1, last_page)
        if first_page == last_page:
            print(f"No new pictures found after {first_page}, nothing to download\n")
            sys.exit(0)

    source_url += f"/{first_page}"

    page_counter = 0
    page_iterator = first_page
    dir_made = False

    print(f"Downloading pages {first_page}..{last_page}\n")
    
    # Phase 2: grab images

    while True:
    
        step_timer = f"{int(time.time()-start_time):05} sec"
        source = requests.get(source_url, cookies={"ageRestrict":"17"})
        if (source.status_code == 200):
        
            # print(source.text)
        
            soup = bs4.BeautifulSoup(source.text, features="lxml")
            main_image = soup.find('img',{'id':'mainImage'})
            next_page = soup.find('a', {'class':'button large comic-nav-next'})

            # Download image
            if (main_image):
                image_src = main_image.get('src')
                if image_src:
                    image_url = f"{url_prefix}/{main_image.get('src')}"
                    file_ext = image_src.split('.')[-1]
                    image_file = f"{dir_name}/page-{page_iterator:04}-{main_image.get('alt').replace('/','_')}.{file_ext}"
                    if not os.path.exists(image_file) or args.rewrite:
                        image_req = requests.get(image_url, allow_redirects=True)
                        if (image_req.status_code == 200):
                           open(image_file,'wb').write(image_req.content)
                           print(f"[{step_timer}] Page {page_iterator}: File {image_file} saved")
                    else:
                        print(f"[{step_timer}] Page {page_iterator}: Warning: file {image_file} already exists")
                else:
                    print(f"[{step_timer}] Page {page_iterator}: Warning: cannot load image from page {source_url}")
                
            #print(f"Image: https://acomics.ru/{main_image.get('src','???')}, File: {main_image.get('alt','???')}, Save name: page-{page_counter}-{main_image.get('alt')}, Next page: {next_page.get('href','???')}")
            #print(f'main_image={main_image}, next_page={next_page}')

            if next_page == None or page_iterator == last_page: break
            page_counter  += 1
            page_iterator += 1
            source_url = next_page.get('href')
            
        else:
            print(f"[{step_timer}] Error: cannot load data from {source_url}")
        
    # Phase 3: Total report

    print(f"{'-'*40}\nTotal: Processed {page_counter} pages in {int(time.time()-start_time)} seconds\n")


# -[ Entry point ]-

if __name__ == "__main__":
    main()

# -[ The end ]-

