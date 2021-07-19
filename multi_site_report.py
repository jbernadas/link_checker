#! /usr/bin/python3

## Note: Before running this script make
## sure the batch.txt file is populated 
## with the base url, i.e., https://example.com

import os

#  Opens the file and read the target URL pages we will be crawiing
target_urls_file = open(f'./batch.txt', 'r')

# Replaces target url list new line with commas
target_urls_content = target_urls_file.read().replace('\n', ',')
# Removes the last comma
target_urls_content = target_urls_content.rstrip(',')

# Holds target URLs list
target_urls = target_urls_content.split(',')

# Closes the file we opened above
target_urls_file.close()

executeOrder65 = "python3 site_report.py -d no -l no {}".format(target_url)

for target_url in target_urls:
  os.system(executeOrder65)
