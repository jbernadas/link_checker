#! /usr/bin/python3

from bs4 import BeautifulSoup, SoupStrainer
import lxml
import requests
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urljoin
import time
import datetime
import re

class bcolors:
  OKGREEN = '\033[92m'
  CYAN = '\u001b[36m'
  WARNING = '\033[93m'
  BRIGHT_RED = '\u001b[31;1m'
  MAGENTA = '\u001b[35m'
  ENDC = '\033[0m'

# Store links that have already been searched here
searched_links = []
# Store broken links here
broken_links = []
# Counts broken links found 
broken_link_count = 0
# This holds the name of our broken links text report 
filenetloc = ''
# For use by the filenetloc block
run_once = 0
# The time in seconds to limit our crawl, set this so that we don't hit server too hard
rate_limit = 0.25
# Used for timer
start_time = time.time()

# timeoutsec = 120
# target_folder = domainToSearch.split('.')[0]
# target_urls_file = open('./site_report/' + target_folder + '/' + target_folder + '-urls.txt', 'r')

#  Opens the file and read the target URL pages we will be crawiing
target_urls_file = open('./target-sitemap.txt', 'r')

# Replaces target url list new line with commas
target_urls_content = target_urls_file.read().replace('\n', ',')

# Holds target URLs list
target_urls = target_urls_content.split(',')

# Closes the file we opened above
target_urls_file.close()

# List of file extensions our crawler should not parse as HTML
skipthese = [
  '.pdf', '.mp4', '.xlxs', '.png', '.docx', \
  '.doc', '.gif', '.jpg', '.jpeg', '.tar', \
  '.gz', '.zip', '.mov', '.mp3', '.wrf', \
  '.xlx', '.txt', '.dmg', '.tgz', '.mov', \
  '.wmv', '.swf', '.pptx', '.ppt', '.pps', \
  '.jpg?*'
  ]

# Loops through our target pages
for target_url in target_urls:
  # Make sure the url has not been searched already
  if (not target_url in searched_links):
    
    url = target_url
    
    urlp = urlparse(url)
    
    # Only run this block if run_once is equal to 0
    if run_once == 0:
      # Initialize the filenetloc to this variable, 
      # this is for naming the broken links file output
      filenetloc = urlp.netloc.split('.')[0]
      # Set run_once to 1, 
      # so this block will never run again
      run_once = 1

    # Make a request to get the URL
    page = requests.get(url)

    # Get the response code of given URL
    response_code = str(page.status_code)
    print(f"{bcolors.OKGREEN}Opening page {url} " + f" | Status Code: {response_code}{bcolors.ENDC}")
    searched_links.append(url)

    #####  TO DO: CREATE AN IF, ELIF, ELSE COND HERE TO CHECK IF PAGE IS 200, 404 OR NOT
    #####  THEN PRINT IT ALSO IF BROKEN

    special_extension = re.compile("\.jpg\?.*")

    # If URL ends with a file extension in skipthese, pass it
    if url.endswith(tuple(skipthese)) or special_extension.search(url):
      print(f"{bcolors.CYAN}Skipping, this page has no children links, going to next URL.{bcolors.ENDC}")
      searched_links.append(url)
      pass
  
    else:
      try:
        # Get the text of the URL
        data = page.text
        # Use BeautifulSoup to use the built-in methods
        soup = BeautifulSoup(data, 'lxml')
        # target_group = soup.find(id="onelab-content") ##### !!!COMMENTED THIS OUT BECAUSE SOME WEBSITES DON'T HAVE THIS ID!!!
        target_soup = soup

        if not target_soup.find_all('a'):
          print(f"{bcolors.CYAN}Skipping, this page has no children links, going to next URL.{bcolors.ENDC}")
          searched_links.append(url)
          pass
          
        else:
          # Iterate over all links on the given URL with the response code next to it
          for link in target_soup.find_all('a'):
            # Make sure this link has not been searched yet, if it is, skip it
            if (link.get('href') in searched_links):
              print(f'{bcolors.CYAN}Skipping. This link has already been searched ({link.get("href")}).{bcolors.ENDC}')
              print('-------------')
              pass
            else:
              if (not link.get('href') == None) and (not link.get('href').startswith("mailto:")) and (not ("javascript:" in link.get('href'))):
                try:
                  # If there is regular URL scheme and netloc, i.e., https://example.com then do the below
                  if urlp.scheme in urlparse(link.get('href')):
                    response = requests.get(link.get('href'), verify=False)
                    status = response.status_code
                    if status == 200:
                      print(f"Link Url: {link.get('href')} " + f"| Status Code: {status}")
                      print(f"Link text: {link.text}")
                      print('-------------')
                    # 404 errors will be printed in console as RED and printed in the report
                    elif status == 404:
                      print(f"{bcolors.BRIGHT_RED}On this page: {url}{bcolors.ENDC}")
                      broken_links.append(f"On this page: {url}")
                      print(f"{bcolors.BRIGHT_RED}Broken link Url: {link.get('href')} " + f"| Status Code: {status}{bcolors.ENDC}")
                      broken_links.append(f"Broken link Url: {link.get('href')} " + f"| Status Code: {status}")
                      print(f"{bcolors.BRIGHT_RED}Broken link text: {link.text}{bcolors.ENDC}")
                      broken_links.append(f"Broken link text: {link.text}")
                      print('-------------')
                      broken_links.append('-------------')
                      broken_link_count += 1
                    # All other error status codes will show in console as color MAGENTA, but will not be printed in report 
                    elif status != 200 or status != 404:
                      print(f"{bcolors.MAGENTA}Link Url: {link.get('href')} " + f"| Status Code: {status}{bcolors.ENDC}")
                      print(f"{bcolors.MAGENTA}Link text: {link.text}{bcolors.ENDC}")
                      print('-------------')
                      
                    searched_links.append(link.get('href'))
                  # If there is NO URL scheme and netloc, i.e., https://example.com then do the below
                  if urlp.scheme not in urlparse(link.get('href')):
                    # Attaches URL scheme and netloc to request
                    response = requests.get(urljoin('https://' + urlp.netloc, link.get('href')), verify=False)
                    status = response.status_code
                    if status == 200:
                      print(f"Link Url:  {urljoin('https://' + urlp.netloc, link.get('href'))} " + f"| Status Code: {status}")
                      print(f"Link text: {link.text}")
                      print('-------------')
                    # 404 errors will be printed in console as RED and printed in the report
                    elif status == 404:
                      print(f"{bcolors.BRIGHT_RED}On this page: {url}{bcolors.ENDC}")
                      broken_links.append(f"On this page: {url}")
                      print(f"{bcolors.BRIGHT_RED}Broken link Url:  {urljoin('https://' + urlp.netloc, link.get('href'))} " + f"| Status Code: {status}{bcolors.ENDC}")
                      broken_links.append(f"Broken link Url:  {urljoin('https://' + urlp.netloc, link.get('href'))} " + f"| Status Code: {status}")
                      print(f"{bcolors.BRIGHT_RED}Broken link text: {link.text}{bcolors.ENDC}")
                      broken_links.append(f"Broken link text: {link.text}")
                      print('-------------')
                      broken_links.append('-------------')
                      broken_link_count += 1
                    # All other error status codes will show in console as color MAGENTA, but will not be printed in report
                    elif status != 200 or status != 404:
                      print(f"{bcolors.MAGENTA}Link Url:  {urljoin('https://' + urlp.netloc, link.get('href'))} " + f"| Status Code: {status}{bcolors.ENDC}")
                      print(f"{bcolors.MAGENTA}Link text: {link.text}{bcolors.ENDC}")
                      print('-------------')

                    # searched_links.append(link.get(urljoin('https://' + urlp.netloc, link.get('href'))))
                    searched_links.append(link.get('href'))
                  else:
                    pass
                except requests.exceptions.RequestException as e:
                  requestObj = "No response"
                  searched_links.append(link)
                  pass
              else:
                pass
            time.sleep(rate_limit)
      except AttributeError as error:
        print(f"{bcolors.WARNING}This page has no children links. Skipping to next target URL.{bcolors.ENDC}")
        searched_links.append(url)
        pass
  # Wait a little bit befor hitting another page
  time.sleep(rate_limit)

with open(f"./broken_links/{filenetloc}-broken-links.txt", 'w') as f:
  f.write("{} Broken Links Report (404 Only)".format(urlp.netloc.upper()))
  f.write("\n\n")
  if broken_link_count >= 2 or broken_link_count == 0:
    f.write("There were {} broken links found.".format(broken_link_count))
  else:
    f.write("There was {} broken link found.".format(broken_link_count))
  f.write("\n\n")
  for line in broken_links:
    f.write("{}\n".format(line))

print(f"Broken links checker finished in {str(datetime.timedelta(seconds=(time.time() - start_time))).split('.')[0]}")
print(f"Found {broken_link_count} broken link/s.")
print("----- The End -----")
      