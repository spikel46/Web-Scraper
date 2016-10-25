"""
Quick web scraper I wrote. Realized I couldnt load javascript so I'm building a new one, but consider this version 1.0
"""
import sys, os, re, requests
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup as bs
from imgurpython import ImgurClient


#register a client here https://api.imgur.com/oauth2/addclient
client_id = "Your Client ID"
client_secret = "Your Client Secret"

client = ImgurClient(client_id, client_secret)


#OPTION NUMBERS
NUM_OPTIONS = 3
NUM_RANGE = NUM_OPTIONS+1

SEARCH = 1
PAGE = 2
SINGLE = 3

#ARGUMENT NUMBERS
URL_NUM = 1
OPT_NUM = 2

#http://codereview.stackexchange.com/questions/19663/http-url-validating
html_regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def menu():
    descriptors = ["A download searching for specific titles",
                   "A download of all images on the given link",
                   "Single image download"]
    choice = 0

    print("This tool allows for {} types of downloads".format(NUM_OPTIONS))

    for i in range(NUM_OPTIONS):
        print(i+1,": ",descriptors[i])

    #better way to handle invalid inputs???
    while choice not in range(1, NUM_RANGE):
        choice =int(input("Please enter your choice ({} for quit): ".format(NUM_OPTIONS+1)))
        if choice == NUM_RANGE:
            exit()
    return choice

def get_folder():
    folder = input("Please give a name for the output folder: ")
    out_folder = "./"+folder+"/"
    if(not os.path.exists(out_folder)):
        os.mkdir(out_folder)
    return out_folder

def download_image(url, out_folder):
    res = requests.get(url)
    #res.raise_for_status()
    title = url.split('/')[-1]
    outpath = os.path.join(out_folder,title)
    fileWrite = open(outpath, 'wb')
    for block in res.iter_content(100000):
        fileWrite.write(block)
    fileWrite.close()

#pick a diff way to name files. resource exhaustive without being helpful
def download_page(url, out_folder, domain):
    if (domain == "imgur"):
        album_id = url.split("/")[-1]
        items = client.get_album_images(album_id)
        for item in range(len(items)):
            #print(item.link)
            image_url = urllib.parse.urljoin(url, items[item].link)
            filename = str(item) + " " + (items[item].link).split("/")[-1]
            outpath = os.path.join(out_folder, filename)
            urllib.request.urlretrieve(image_url,outpath)
    else:
        page = urllib.request.urlopen(url)
        soup = bs(page)

        for image in soup.find_all("img"):
            if(domain in (image["src"])):
                print ("Image: {}".format(image))
                image_url = urllib.parse.urljoin(url, image["src"])
                filename = image["src"].split("/")[-1]
                outpath = os.path.join(out_folder, filename)
                urllib.request.urlretrieve(image_url,outpath)

#this function assumes a form of Title->Link with no newlines in between
def find_links(url, out_folder, query, domain):
    page = urllib.request.urlopen(url)
    soup = bs(page)
    str_soup = str(soup)
    find = re.compile(r"{}.+{}".format(query,"</a>"))
    full_list = find.findall(str_soup)
    link = re.compile(r"{}(\S+){}".format("href=\"", "\""))

    for part in range(len(full_list)):
        extracted = link.search(full_list[part])
        sub_folder = os.path.join(out_folder, str(part))
        if(not os.path.exists(sub_folder)):
            os.mkdir(sub_folder)
        download_page(extracted.group()[6:-1],sub_folder, domain)

#MAIN CODE
if (len(sys.argv) != 2) and (len(sys.argv) !=3):
    print("Invalid number of arguments, please read documentation")
    exit()

if(len(sys.argv) == 2):
    choice = menu()
elif(len(sys.argv) == 3):
    choice = int(sys.argv[OPT_NUM])
    if choice not in range(1,NUM_RANGE):
        print("Please enter a valid choice")
        choice = menu()

main_url = sys.argv[URL_NUM]
result = html_regex.search(main_url)

if(not result):
    print("Unaccepted web address.")
    exit()

domain = (urllib.parse.urlparse(main_url).netloc).split(".")[-2]

out_folder = get_folder()

if choice == SEARCH:
    query = input("Please enter your search query: ")
    find_links(main_url, out_folder, query, domain)
elif choice == PAGE:
    download_page(main_url, out_folder, domain)
elif choice == SINGLE:
    download_image(main_url, out_folder)

else:
    print("Unexpected error, please send me a screenshot of your choices")
