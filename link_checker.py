#!/usr/bin/python3

from bs4 import BeautifulSoup, SoupStrainer
import lxml
import getopt
import requests
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urljoin
import time
import datetime
import urllib3
import re
import sys
from itertools import islice
import warnings
import random
## For debugging starts
import logging
import http.client

http.client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
# End of For debugging

# Used for timer
start_time = ''
# Counts broken links found 
broken_link_count = 0
link_checker_version = "1.0.2"
verifyVar = True
time_out = (2, 60)
sitename = ''

class bcolors:
    OKGREEN = '\033[92m'
    WHITETXTGREENBAK = '\033[1;37;42m'
    CYAN = '\u001b[36m'
    WARNING = '\033[93m'
    BRIGHT_RED = '\u001b[31;1m'
    MAGENTA = '\u001b[35m'
    ENDC = '\033[0m'


help_text = """

  ######################################################
  ############  LINK CHECKER version %s  ############
  ################ by: Joseph Bernadas #################

  This command line program crawls a website based on a previously
  generated sitemap list of URLs. Command line syntax:

  python3 link_checker.py <options> <target URL>

  Available options:

  -h          --help            Print this help text
  -v          --verbose         Verbose command line output
  -r          --rate-limit      A float in seconds that determines how 
                                fast the crawler should query the site


  Usage example:

  python3 link_checker.py -r 0.25 example-folder

  In the above example, 0.25 seconds is the rate-limit
  and 'example-folder' is the name of the folder 
  inside of the 'site_report' directory where our list
  of URLs are located in a text file.

""" % (link_checker_version)

def checklink(base_href, url, target, session, searched_links, broken_links, sLinkStatus):
  global broken_link_count

  scheme = re.compile(r'^(?:http)s?:\/\/')
  link = target
  if target.get('href').startswith(' '):
    href = link.get('href').strip()
  else:
    href = link.get('href')

  # If there is regular URL scheme and netloc, i.e., https://example.com then execute the below
  if scheme in urlparse(href):
    response = session.get(href, verify=verifyVar, timeout=time_out)
    status = response.status_code
    if status == 200:
      print(f"{bcolors.OKGREEN}Link Url: {href} " + f"| Status Code: {status}{bcolors.ENDC}")
      # Prints the link text without duplicate spaces and new lines
      print(f"{bcolors.OKGREEN}Link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      print('-------------')
    # 404 errors will be printed in console as RED and printed in the report
    elif status == 404:
      print(f"{bcolors.BRIGHT_RED}On this page: {url}{bcolors.ENDC}")
      broken_links.append(f"On this page: {url}")
      print(f"{bcolors.BRIGHT_RED}Broken link Url: {href} " + f"| Status Code: {status}{bcolors.ENDC}")
      broken_links.append(f"Broken link Url: {href} " + f"| Status Code: {status}")
      # Prints the broken link text without duplicate spaces and new lines
      print(f"{bcolors.BRIGHT_RED}Broken link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      broken_links.append(f"Broken link text: {' '.join(link.text.split())}")
      print('-------------')
      broken_links.append('-------------')
      broken_link_count += 1
    elif status == 301:
      print(f"{bcolors.BRIGHT_RED}On this page: {url}{bcolors.ENDC}")
      broken_links.append(f"On this page: {url}")
      print(f"{bcolors.BRIGHT_RED}Moved permanently link Url: {href} " + f"| Status Code: {status}{bcolors.ENDC}")
      broken_links.append(f"Moved permanently link Url: {href} " + f"| Status Code: {status}")
      # Prints the broken link text without duplicate spaces and new lines
      print(f"{bcolors.BRIGHT_RED}Moved permanently link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      broken_links.append(f"Moved permanently link text: {' '.join(link.text.split())}")
      print('-------------')
      broken_links.append('-------------')
      broken_link_count += 1
    # All other error status codes will show in console as color MAGENTA, but will not be printed in report 
    elif status != 200 or status != 301 or status != 404:
      print(f"{bcolors.MAGENTA}Link Url: {href} " + f"| Status Code: {status}{bcolors.ENDC}")
      # Prints the link text without duplicate spaces and new lines
      print(f"{bcolors.MAGENTA}Link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      print('-------------')
      
    searched_links.append(sLinkStatus(href, status, url))

  # If there is NO URL scheme and base_href is populated, then do the below
  if scheme not in urlparse(href) and base_href:
    # Prepends base_href to request
    response = session.get(urljoin(base_href, href), verify=verifyVar, timeout=time_out)
    status = response.status_code
    if status == 200:
      print(f"{bcolors.OKGREEN}Link Url:  {urljoin(base_href, href)} " + f"| Status Code: {status}{bcolors.ENDC}")
      print(f"{bcolors.OKGREEN}Link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      print('-------------')
    # 404 errors will be printed in console as RED and printed in the report
    elif status == 404:
      print(f"{bcolors.BRIGHT_RED}On this page: {url}{bcolors.ENDC}")
      broken_links.append(f"On this page: {url}")
      print(f"{bcolors.BRIGHT_RED}Broken link Url:  {urljoin(base_href, href)} " + f"| Status Code: {status}{bcolors.ENDC}")
      broken_links.append(f"Broken link Url:  {urljoin(base_href, href)} " + f"| Status Code: {status}")
      # Prints the broken link text without duplicate spaces and new lines
      print(f"{bcolors.BRIGHT_RED}Broken link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      broken_links.append(f"Broken link text: {' '.join(link.text.split())}")
      print('-------------')
      broken_links.append('-------------')
      broken_link_count += 1
    elif status == 301:
      print(f"{bcolors.BRIGHT_RED}On this page: {url}{bcolors.ENDC}")
      broken_links.append(f"On this page: {url}")
      print(f"{bcolors.BRIGHT_RED}Moved permanently link Url: {href} " + f"| Status Code: {status}{bcolors.ENDC}")
      broken_links.append(f"Moved permanently link Url: {href} " + f"| Status Code: {status}")
      # Prints the broken link text without duplicate spaces and new lines
      print(f"{bcolors.BRIGHT_RED}Moved permanently link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      broken_links.append(f"Moved permanently link text: {' '.join(link.text.split())}")
      print('-------------')
      broken_links.append('-------------')
      broken_link_count += 1
    # All other error status codes will show in console as color MAGENTA, but will not be printed in report
    elif status != 200 or status != 301 or status != 404:
      print(f"{bcolors.MAGENTA}Link Url:  {urljoin(base_href, href)} " + f"| Status Code: {status}{bcolors.ENDC}")
      # Prints the link text without duplicate spaces and new lines
      print(f"{bcolors.MAGENTA}Link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      print('-------------')
    
    # searched_links.append(link.get(urljoin('https://' + urlp.netloc, link.get('href'))))
    # searched_links.append(link.get('href'))
    searched_links.append(sLinkStatus(href, status, url))
    
  # If there is NO URL scheme and base_href is NOT populated, then do the below
  if scheme not in urlparse(href) and not base_href:
    # Attaches URL scheme and netloc to request
    response = session.get(urljoin(url, href), verify=verifyVar, timeout=time_out)
    status = response.status_code
    if status == 200:
      print(f"{bcolors.OKGREEN}Link Url:  {urljoin(url, href)} " + f"| Status Code: {status}{bcolors.ENDC}")
      print(f"{bcolors.OKGREEN}Link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      print('-------------')
    # 404 errors will be printed in console as RED and printed in the report
    elif status == 404:
      print(f"{bcolors.BRIGHT_RED}On this page: {url}{bcolors.ENDC}")
      broken_links.append(f"On this page: {url}")
      print(f"{bcolors.BRIGHT_RED}Broken link Url:  {urljoin(url, href)} " + f"| Status Code: {status}{bcolors.ENDC}")
      broken_links.append(f"Broken link Url:  {urljoin(url, href)} " + f"| Status Code: {status}")
      # Prints the broken link text without duplicate spaces and new lines
      print(f"{bcolors.BRIGHT_RED}Broken link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      broken_links.append(f"Broken link text: {' '.join(link.text.split())}")
      print('-------------')
      broken_links.append('-------------')
      broken_link_count += 1
    elif status == 301:
      print(f"{bcolors.BRIGHT_RED}On this page: {url}{bcolors.ENDC}")
      broken_links.append(f"On this page: {url}")
      print(f"{bcolors.BRIGHT_RED}Moved permanently link Url: {href} " + f"| Status Code: {status}{bcolors.ENDC}")
      broken_links.append(f"Moved permanently link Url: {href} " + f"| Status Code: {status}")
      # Prints the broken link text without duplicate spaces and new lines
      print(f"{bcolors.BRIGHT_RED}Moved permanently link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      broken_links.append(f"Moved permanently link text: {' '.join(link.text.split())}")
      print('-------------')
      broken_links.append('-------------')
      broken_link_count += 1
    # All other error status codes will show in console as color MAGENTA, but will not be printed in report
    elif status != 200 or status != 301 or status != 404:
      print(f"{bcolors.MAGENTA}Link Url:  {urljoin(url, href)} " + f"| Status Code: {status}{bcolors.ENDC}")
      # Prints the link text without duplicate spaces and new lines
      print(f"{bcolors.MAGENTA}Link text: {' '.join(link.text.split())}{bcolors.ENDC}")
      print('-------------')

    # searched_links.append(link.get(urljoin('https://' + urlp.netloc, link.get('href'))))
    # searched_links.append(link.get('href'))
    searched_links.append(sLinkStatus(href, status, url))
  else:
    pass

def link_checker(netlocSplit, session, rateLimit=0.5):
  global start_time
  global current_date
  global broken_link_count
  global sitename

  sitename = netlocSplit
  
  start_time = time.time()
  print("###############################")
  print("#### LINK CHECKER STARTED! ####")
  print("###############################")

  class sLinkStatus:
    def __init__(self, uri, status, parent=None):
      self.uri = uri
      self.parent = parent
      self.status = status

  # Store links that have already been searched here
  searched_links = []
  # Store broken links here
  broken_links = []
  # This holds the name of our broken links text report 
  filenetloc = ''
  # For use by the filenetloc block
  run_once = 0
  # The time in seconds to limit our crawl, set this so that we don't hit server too hard
  rate_limit = rateLimit

  # timeoutsec = 120
  # target_folder = domainToSearch.split('.')[0]
  # target_urls_file = open('./site_report/' + target_folder + '/' + target_folder + '-urls.txt', 'r')

  #  Opens the file and read the target URL pages we will be crawiing
  target_urls_file = open(f'./site_report/{netlocSplit}/{netlocSplit}-urls.txt', 'r')

  # Replaces target url list new line with commas
  target_urls_content = target_urls_file.read().replace('\n', ',')
  # Removes the last comma
  target_urls_content = target_urls_content.rstrip(',')

  # Holds target URLs list
  target_urls = target_urls_content.split(',')
  # Removes the first duplicate line
  # target_urls = islice(target_urls, 1, None)

  # Closes the file we opened above
  target_urls_file.close()

  # List of file extensions our crawler should not parse as HTML (please use uppercase)
  skipthese = [
    '.PDF', '.MP4', '.XLXS', '.PNG', '.DOCX', \
    '.DOC', '.GIF', '.JPG', '.JPEG', '.TAR', \
    '.GZ', '.ZIP', '.MOV', '.MP3', '.WRF', \
    '.XLX', '.TXT', '.DMG', '.TGZ', '.MOV', \
    '.WMV', '.SWF', '.PPTX', '.PPT', '.PPS', \
    '.TIFF'
    ]

  # Loops through our target pages
  for target_url in target_urls:
    
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
    page = session.get(url)

    # Get the response code of given URL
    response_code = str(page.status_code)
    print(f"{bcolors.WHITETXTGREENBAK}Opening page {url} " + f" | Status Code: {response_code}{bcolors.ENDC}")
    searched_links.append(sLinkStatus(url, page.status_code))

    #####  TO DO: CREATE AN IF, ELIF, ELSE COND HERE TO CHECK IF PAGE IS 200, 404 OR NOT
    #####  THEN PRINT IT ALSO IF BROKEN

    special_extension = re.compile("\.jpg\?.*")

    # If URL ends with a file extension in skipthese, we don't need to check for children links, we will pass it
    if url.upper().endswith(tuple(skipthese)) or special_extension.search(url):
      print(f"{bcolors.CYAN}Skipping, this has no children links, going to next URL.{bcolors.ENDC}")
      searched_links.append(sLinkStatus(url, page.status_code))
      pass

    # Else, we are going to check if this page has children links
    else:
      try:
        # Get the text of the URL
        data = page.text
        # Use BeautifulSoup to use the built-in methods
        soup = BeautifulSoup(data, 'lxml')
        # target_group = soup.find(id="onelab-content") ##### !!!COMMENTED THIS OUT BECAUSE SOME WEBSITES DON'T HAVE THIS ID!!!
        target_soup = soup
        base_href = ''

        # If base href is defined in headers, set base_href
        if target_soup.base:
          base_href = target_soup.base.attrs['href']

        # If there are no 'a' tags on page, put it in
        if not target_soup.find_all('a'):
          print(f"{bcolors.CYAN}Skipping, this page has no children links, going to next URL.{bcolors.ENDC}")
          searched_links.append(sLinkStatus(url, page.status_code))
          pass
        # Else, we check all links in target_soup.find_all('a')  
        else:
          # Iterate over all links on the given URL with the response code next to it
          for link in target_soup.find_all('a'):
            # time.sleep(rate_limit)
            # Make sure this link has not been checked yet, if it has, skip it
            # TO DO, IF LINK HAS BEEN SEARCHED AND IT IS BROKEN, CHECK IF PARENT URL IS THE SAME, 
            # IF NOT SAME PARENT URL, THEN WE NEED TO PUT INTO BROKEN LINKS REPORT
            # if link.get('href') in searched_links:
            # meets_criteria = (any(searched_link.uri) == link.get('href') for searched_link in searched_links)

            # for index, searched_link in enumerate(searched_links):
            #   if searched_link.uri == link.get('href') and searched_link.status == 200 and searched_link.parent not url:
            # if any(searched_link.uri == link.get('href') for searched_link in searched_links) and any(searched_link.parent == url for searched_link in searched_links):
              # for searched_link in searched_links:
              #   if searched_link.uri == link.get('href') and searched_link.status == 404 and searched_link.parent != url:
              #     checklink(base_href, url, link, session, searched_links, broken_links, sLinkStatus)
              #   elif searched_link.uri == link.get('href') and searched_link.status == 200 and searched_link.parent == url:
            if any(searched_link.uri == link.get('href') for searched_link in searched_links):
              print(f'{bcolors.WARNING}Skipping. This child link has already been checked ({link.get("href")}).{bcolors.ENDC}')
              print('-------------')
              pass
            else:
              if (not link.get('href') == None) and (not link.get('href').startswith("mailto:")) and (not ("javascript:" in link.get('href'))):
                try:
                  time.sleep(rate_limit)
                  checklink(base_href, url, link, session, searched_links, broken_links, sLinkStatus)
                except requests.exceptions.RequestException as e:
                  print(e)
                  print('-------------')
                  requestObj = "No response"
                  # searched_links.append(link)
                  searched_links.append(sLinkStatus(link.get('href'), requestObj, url))
                  pass
              else:
                pass
            # time.sleep(rate_limit)
      except AttributeError as error:
        print(f'AttributeError: {error}')
        warnings.simplefilter('ignore')
        # print(f"{bcolors.WARNING}This page has no children links. Skipping to next target URL.{bcolors.ENDC}")
        # searched_links.append(url)
        searched_links.append(sLinkStatus(link.get('href'), error, url))
        pass
    # Wait a little bit before hitting another page
    time.sleep(rate_limit)

  current_date = datetime.datetime.now()
  with open(f"./site_report/{netlocSplit}/{netlocSplit}-broken-links-{current_date.month:02d}{current_date.day:02d}{current_date.year}{current_date.hour:02d}{current_date.minute:02d}.txt", 'w') as f:
    f.write("{} - Broken Links Report (404 Only)\n".format(netlocSplit.upper()))
    f.write("(This link checker can be configured to look for any HTTP status code.)\n")
    f.write(f"Version: {link_checker_version}")
    f.write("\n")

    # If it finds 2 or more broken links then write this
    if broken_link_count >= 2:
      f.write("Found {} broken links.\n".format(broken_link_count))
      # Put 2 extra spaces
      f.write("\n\n")

    if broken_link_count == 0:
      f.write("Found 0 broken_links.\n")
      # Put 2 extra spaces
      f.write("\n\n")

      f.write("-------------")
   
    # Else then write this
    else:
      f.write("Found {} broken link.".format(broken_link_count))
      # Put 2 extra spaces
      f.write("\n\n")
          
    
    for line in broken_links:
      f.write("{}\n".format(line))
    f.write("\n")
    f.write(f"This report was generated on {current_date.month:02d}/{current_date.day:02d}/{current_date.year} at {current_date.hour:02d}{current_date.minute:02d}H\n")
    f.write(f"Link checker finished in {str(datetime.timedelta(seconds=(time.time() - start_time))).split('.')[0]}\n")
    f.write(f"---- The End. ----")

def main():

  user_agent_list = [
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16'
  ]

  session = requests.Session()
  user_agent = random.choice(user_agent_list)
  headers = {'User-Agent': user_agent}
  session.headers.update(headers)
  session.keep_alive = True

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hr:v", ["help", "rate-limit"])
  except getopt.GetoptError as err:
    print(str(err))
    sys.stderr.write(help_text)
    sys.exit(2)
  
  for opt, arg in opts:
    if opt == "-v":
      verbose = True
    elif opt in ("-h", "--help"):
      sys.stderr.write(help_text)
      return 1
    elif opt in ("-r", "--ratelimit"):
      ratelimit = float(arg)
    else:
      assert False, "unhandled option"
  
  if not args:
    sys.stderr.write("You must provide the folder name. Try the -h option for help.\n")
    return 1

  # Start the process
  link_checker(args[0], session)
  print('\n')
  print(f"Finished checking {sitename}")
  print(f"Link checker finished in {str(datetime.timedelta(seconds=(time.time() - start_time))).split('.')[0]}")
  print(f"Found {broken_link_count} broken link/s.")
  print("----- The End -----")

if __name__ == "__main__":
  main()  