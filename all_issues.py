from urllib.parse import urlparse
import requests
import re
import os

# Debug setting
debug = False

# Place to put the files (Yes, I developed it on windows!)
# CHANGE THIS FOR YOUR OWN PATH
output_dir = "D:\\MagPi\\"

# URLs for all the Raspberry Pi Foundation Free magazines and books
# With a locaiton and template filename
urlList = []
urlList.append(('https://magpi.raspberrypi.org/issues', os.path.join(output_dir, "Magazines", "MagPi<NUMB>.pdf")))
urlList.append(('https://magpi.raspberrypi.org/books', os.path.join(output_dir, "Books", "<BOOK>")))
urlList.append(('https://hackspace.raspberrypi.org/issues/', os.path.join(output_dir, "HackSpace", "HackSpaceMagazine<NUMB>.pdf")))
urlList.append(('https://wireframe.raspberrypi.org/issues/', os.path.join(output_dir, "WireFrame", "Wireframe<NUMB>.pdf")))
urlList.append(('https://helloworld.raspberrypi.org/issues', os.path.join(output_dir, "HelloWorld", "HelloWorld_<NUMB>.pdf")))
urlList.append(('https://wireframe.raspberrypi.org/books/', os.path.join(output_dir, "Wireframe_Books", "<BOOK>")))

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

# Make sure the output folders is available
for (url, template) in urlList:
    dir = os.path.dirname(template)
    if not os.path.exists(dir):
        print("Creating '{0}' now".format(dir))
        os.makedirs(dir)

# create a base links
links = []
# Get the links from all the pages, using the RegEx supplied
for (url, template) in urlList:
    print("URL: " + url + " - Template:" + template)
    # Get the primary page, with all the links
    page = GetPage(url)
    # Process the page, get the links
    secondPages = ProcessFirstLinks(page)
    # Get the URL parts we need
    urlParts = urlparse(url)
    prependLink = urlParts.scheme + '://'+ urlParts.netloc
    # Go through the links
    for primeLink in secondPages:
        # Set up the var for processing
        page = ""
        outFile = ""

        # Check to see if there's a number in the URL
        fileParts = primeLink.split('/')
        if fileParts[2].isnumeric():
            # Generate the output filename from the template
            outFile = template.replace("<NUMB>", "{:02d}".format(int(fileParts[2])))
            # Check to make sure the file doesn't already exist, don't bother getting
            # the linked page if it exists, less load on severs.
            if not os.path.isfile(outFile):
                page = GetPage(prependLink + primeLink)
        else:
            # No number, so get the file name from the link (later)
            page = GetPage(prependLink + primeLink)

        # If there's not page to process, skip it
        if not page == "":
            # Get the actual download link
            downloadLink = ProcessSecondPage(page)
            # If no name has been supplied
            if outFile == "":
                # Get the on disk name from the URL
                fileParts = downloadLink[0].split('/')
                outFile = template.replace("<BOOK>", fileParts[-1].split('?')[0])

            # Check to see if the file exists already (mainly for the books section)
            if not os.path.isfile(outFile):
                print("Getting :" + outFile)
                r = requests.get(downloadLink[0], allow_redirects=True)
                open(outFile, 'wb').write(r.content)

print("Done...")