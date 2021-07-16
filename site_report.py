#!/usr/bin/python3

import os
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
from urllib.parse import urljoin
import getopt
import sys
import re
import sitemap_gen
from pprint import pprint
import requests
from lxml import etree
from datetime import datetime

help_text = """
  ######################################################
  ####   SITEREPORT.py version 0.0.1 (2020-09-06)   ####
  ######################################################

  This command line program initiates a site report and can also
  download documents. Command line syntax:

  python3 site_report.py <options> <target URL>

  Available options:

  -h          --help            Print this help text
  -v          --verbose         Verbose command line output
  -d          --download        Download all downloadable files. Available arguments for this are: yes, no, doc or img.
  -l          --linkcheck       Check for broken links


  Usage example:

  python3 site_report.py -d no -l no http://target.llnl.gov

  or

  python3 site_report.py --download yes --linkcheck yes http://target.llnl.gov

"""

# Finds the generated .xml report inside ./site_report directory
def find_xml_report(directory):
  for file in os.listdir(directory):
    if file.endswith(".xml"):
      return file

# Counter - counts how many type of files based on qualifiers
def counter_func(qualifiers, targetSplit):
  xml_file = find_xml_report('./site_report/' + targetSplit)
  doc = etree.parse('./site_report/' + targetSplit + '/' + xml_file)
  root = doc.getroot()
  counter = 0
  for i in range(0, len(root.getchildren())):
    for item in qualifiers:
      if (root[i][0]).text.endswith(item):
        counter += 1
  return counter

# DOCUMENT & IMAGE Downloader - downloads either docs or images
def downloader(qualifiers, upload_folder, targetSplit, session):
  xml_file = find_xml_report('./site_report/' + targetSplit)
  # folder = './site_report/' + target_split
  doc = etree.parse('./site_report/' + targetSplit + '/' + xml_file)
  root = doc.getroot()
  count = 0
  count_type = counter_func(qualifiers, targetSplit)

  for i in range(0, len(root.getchildren())):
    for qualifier in qualifiers:
      if (root[i][0]).text.endswith(qualifier):
        filename = os.path.join(upload_folder, root[i][0].text.split('/')[-1])
        with open(filename, 'wb') as im:
          im.write(session.get(root[i][0].text).content)
          count += 1
          # Limit 2 requests per second
          time.sleep(0.5)
          if '.pdf' in qualifiers:
            print("Downloading document {}/{}".format(count, count_type))
          else:
            print("Downloading image {}/{}".format(count, count_type))
  
  if '.pdf' in qualifiers:
    print("Finished downloading {} files!".format(count))
  else:
    print("Finished downloading {} images!".format(count))


def site_report(download, linkCheck, targetSite, session):
  # parse the URL of targetSite
  urlParsed = urlparse(targetSite)
  targetSplit = urlParsed.hostname.split(".")[0]
  targetFolder = "./site_report/" + targetSplit

  print("#####################################")
  print("#### SITE REPORT SCRIPT STARTED! ####")
  print("#####################################")
  start_time = datetime.now()
  print("Start time: %s" % (str(start_time).split('.')[0]))
  print('-------------')

  try:
    # create the directory if it does not exist
    os.mkdir(targetFolder)
    print(f"Directory for {targetFolder.upper()} report created.")
  except FileExistsError:
    print("Directory " + targetFolder + " already exists, not recreating it. ")
  print('-------------')


  # recreate original URL
  urlOrig = targetSite

  # only include web pages
  # onlyWebPages = "-b tif -b mpg -b txt -b zip -b psd -b mpeg -b wmv -b mp3 -b xls -b gz -b tar -b png -b jpg -b jpeg -b gif -b mov -b mp4 -b xlsx -b doc -b docx -b pdf"

  # exclude tif mpg txt zip psd mpeg mp3 gz tar
  exclude = "-b tif -b mpg -b txt -b zip -b psd -b mpeg -b mp3 -b gz -b tar"

  # executeSitemapGenXml = "python ./sitemap_gen.py {} -r {} -o {} {}".format(exclude, 0, os.path.join(targetFolder, targetSplit) + ".xml", urlOrig)
  executeSitemapGenTxt = "python ./sitemap_gen.py {} -r {} -o {} {}".format(exclude, 0, os.path.join(targetFolder, targetSplit) + ".txt", urlOrig)

  ## run sitemap_gen.py
  # os.system(executeSitemapGenXml)
  os.system(executeSitemapGenTxt)

  DOCS_FOR_UPLOAD = './site_report/' + targetSplit + '/docs_for_upload'
  IMGS_FOR_UPLOAD = './site_report/' + targetSplit + '/imgs_for_upload'

  DOC_QUALIFIERS = [
    '.pdf',
    '.doc',
    '.docx',
    '.xls',
    '.xlsx'
  ]

  IMG_QUALIFIERS = [
    '.jpg',
    '.png',
    '.gif',
    'jpeg'
  ]

  if download.upper() == "YES":
    # wait for <n> seconds to give last session time to close
    print("Preparing to download documents and images.")
    
    doc_count = counter_func(DOC_QUALIFIERS, targetSplit)
    img_count = counter_func(IMG_QUALIFIERS, targetSplit)

    print("Begin document download!")

    downloader(DOC_QUALIFIERS, DOCS_FOR_UPLOAD, targetSplit, session)

    print('-------------')

    print("Preparing to begin image download!")

    downloader(IMG_QUALIFIERS, IMGS_FOR_UPLOAD, targetSplit, session)
  
  if download.upper() == "DOC":

    os.mkdir(targetFolder + '/docs_for_upload')
    print(f"{targetFolder}/docs_for_upload directory created.")

    doc_count = counter_func(DOC_QUALIFIERS, targetSplit)

    print("Begin document download!")

    downloader(DOC_QUALIFIERS, DOCS_FOR_UPLOAD, targetSplit, session)

  if download.upper() == "IMG":

    os.mkdir(targetFolder + '/imgs_for_upload')
    print(f"{targetFolder}/imgs_for_upload directory created.")

    img_count = counter_func(IMG_QUALIFIERS, targetSplit)

    print("Begin image download!")
    downloader(IMG_QUALIFIERS, IMGS_FOR_UPLOAD, targetSplit, session)
  
  if linkCheck.upper() == "YES":
    os.system(f'python3 ./link_checker.py -r 0.25 {targetSplit}')

def main():
  session = requests.Session()

  try:
    opts, args =  getopt.getopt(sys.argv[1:], "hdl:v", ["help", "download=", "linkcheck="])
  except getopt.GetoptError as err:
    print(str(err))
    sys.stderr.write(help_text)
    sys.exit(2)

  download = ""
  linkcheck = ""

  for opt, arg in opts:
    if opt == "-v":
      verbose = True
    elif opt in ("-h", "--help"):
      sys.stderr.write(help_text)
      return 1
    elif opt in ("-d", "--download"):
      if arg.upper() == "YES":
        download = "YES"
      if arg.upper() == "Y":
        download = "YES"
      if arg.upper() == "DOC":
        download = "DOC"
      if arg.upper() == "DOCS":
        download = "DOC"
      if arg.upper() == "IMG":
        download = "IMG"
      if arg.upper() == "IMGS":
        download = "IMG"
      else:
        download = "NO"
    elif opt in ("-l", "--linkcheck"):
      if arg.upper() == "YES":
        linkcheck = "YES"
      if arg.upper() == "Y":
        linkcheck = "YES"
      else:
        linkcheck = "NO"
    else:
      assert False, "unhandled option"
  
  if not args:
    sys.stderr.write("You must provide the target URL.")
    return 1
  
  site_report(args[0], args[2], args[3], session)

  print("Finish time: %s" % (datetime.now()))
  
if __name__ == "__main__":
  main()
