from urllib.parse import urlparse
import requests
import re
import os

# Debug setting
debug = True

# specify the urlof the MagPi page, with the "Download Free" button
urlList = []
urlList.append('https://magpi.raspberrypi.org/issues')
#urlList.append('https://hackspace.raspberrypi.org/issues/')
#urlList.append('https://wireframe.raspberrypi.org/issues/')

# Place to put the files (Yes, I developed it on windows!)
# CHANGE THIS FOR YOUR OWN PATH
output_dir = "D:\\MagPi\\"

fileNo = 1

def GetPage(url):
    global fileNo
    if debug:
        print("Downloading " + str(url))

    page = ''
    # query the website and return the html to the variable 'page'
    try:
        r = requests.get(url, allow_redirects=True)
        if debug:
            open('D:\\Page_' + str(fileNo) + '.txt', 'wb').write(r.content)
            fileNo += 1
        page = r.content
    except Exception as err:
        print("There was an error")
        print(err)

    return page

def ProcessFirstLinks(page):
    #<a class="c-issue-actions__link c-link u-text-bold" href="/issues/24/pdf">Download Free PDF</a>
    #<a class="c-button c-button--secondary u-mb-x2" href="/issues/23/pdf">Free Download</a>
    firstSearch = '<a class=\"c-issue-actions__link c-link u-text-bold\" href=\"(?P<link>.+?pdf)\">Download Free PDF</a>'
    secondSearch = '<a class=\"c-button c-button--secondary u-mb-x2\" href=\"(?P<link>.+?pdf)\">Free Download</a>'
    ret = []
    ret += re.findall(firstSearch, str(page), flags=re.IGNORECASE)
    ret += re.findall(secondSearch, str(page), flags=re.IGNORECASE)
    return ret

def ProcessSecondPage(page):
    #<a class="c-link" download="beginners-guide-2nd-ed.pdf" href="https://magazines-static.raspberrypi.org/books/full_pdfs/000/000/001/original/Beginners_Guide_v2.pdf?1568891625">click here to get your free PDF</a>
    #<a class="c-link" download="hackspace-magazine-issue-24.pdf" href="https://magazines-static.raspberrypi.org/issues/full_pdfs/000/000/260/original/HackSpaceMagazine24.pdf?1571837861">click here to get your free PDF</a>
    linkRef = '<a class=\"c-link\" download=\".+?\" href=\"(?P<link>.+?)\">click here to get your free pdf</a>'
    return re.findall(linkRef, str(page), flags=re.IGNORECASE)
    
#    if debug:
#        print("Now doing a RegEx on the page text with regex='" + regEx + "'")
#        #print(str(page))

#    # Go through the page and find all the "Download Free" links
#    return re.findall(regEx, str(page), flags=re.IGNORECASE)


# Path to MagPi Magazines
magpi_path = os.path.join(output_dir, "Magazines")
# Path to Essentials
essen_path = os.path.join(output_dir, "Essentials")
# Path to Other Magazines
other_path = os.path.join(output_dir, "Other")
# HackSpace magazine
hs_path = os.path.join(output_dir, "HackSpace")
# WireFrame magazine
wf_path = os.path.join(output_dir, "WireFrame")

# Populate the paths for the appropriate types
paths = dict()
paths['MagPi'] = magpi_path
paths['Essentials'] = essen_path
paths['Hack'] = hs_path
paths['Wire'] = wf_path
paths['WF'] = wf_path
paths['_HS_'] = hs_path
paths['Other'] = other_path

# Make sure the output folders is available
for key in paths:
    if not os.path.exists(paths[key]):
        print("Creating '{0}' now".format(paths[key]))
        os.makedirs(paths[key])

# create a base links
links = []
# Get the links from all the pages, using the RegEx supplied
for item in urlList:
    page = GetPage(item)
    secondPages = ProcessFirstLinks(page)
    urlParts = urlparse(item)
    prependLink = urlParts.scheme + '://'+ urlParts.netloc
    for primeLink in secondPages:
        page = GetPage(prependLink + primeLink)
        links += ProcessSecondPage(page)
        print("links len:" + str(len(links)))
        for link in links:
            print(link)

if False:
    if debug:
        print("---------------------------------------------------------------------------------------")
        print(links)
        print("---------------------------------------------------------------------------------------")

    for link in links:
        print("Looking at {0} now".format(str.split(link, '/')[-1]))

        # Find the last / and extract the file name
        last_pos = link.rfind("/")
        if last_pos == -1:
            print("Link is malformed, unable to process")
        else:
            #grab the filename
            filename = link[last_pos+1:]

            # Check to see if there's a ? in the filename, trim it all off if there is
            last_pos = filename.rfind("?")
            if last_pos != -1:
                filename = filename[:last_pos]

            if debug:
                print(filename)

            # Default the output_dir
            output_dir = paths['Other']

            # Work out what sort of PDF it is, and set the output folder accordingly
            for key in paths:
                if filename.startswith(key) or key in filename:
                    output_dir = paths[key]

            # Create the output filename
            output_file = os.path.join(output_dir, filename)


            # Check to see if the download has already been done
            if os.path.exists(output_file):
                # Tell the user the file already exists
                print("File already exists")
            else:
                # Open the remote file, download and write to disk.
                # TODO: add some error checking/Try-Except here!
                print("Downloading file now")
                r = requests.get(link, allow_redirects=True)
                open(output_file, 'wb').write(r.content)
                #download = urllib2.urlopen(link)
                #with open(output_file,'wb') as output:
                #    output.write(download.read())

print("Done...")