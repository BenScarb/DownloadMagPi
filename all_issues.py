from urllib.parse import urlparse
import requests
import re
import os

# Debug setting
debug = False

# Do you want to check for all back issues as well?
doBackIssues = True

# Place to put the files (Yes, I developed it on windows!)
# CHANGE THIS FOR YOUR OWN PATH
output_dir = "D:\\MagPi\\"

def MagazineLink(page):
    #<a class="c-issue-actions__link c-link u-text-bold" href="/issues/24/pdf">Download Free PDF</a>
    linkSearch = '<a class=\"c-issue-actions__link c-link u-text-bold\" href=\"(?P<link>.+?pdf)\">Download Free PDF</a>'
    return re.findall(linkSearch, str(page), flags=re.IGNORECASE)

def BookLinks(page):
    #<a class="c-button c-button--secondary c-button--block" href="/books/unity-fps/pdf">Free Download</a>
    linkRef = '<a class="c-button c-button--secondary c-button--block" href="(?P<link>.+?)">Free Download</a>'
    return re.findall(linkRef, str(page), flags=re.IGNORECASE)

# URLs for all the Raspberry Pi Foundation Free magazines and books
# With a locaiton and template filename
urlList = []
urlList.append(('https://magpi.raspberrypi.org/issues', os.path.join(output_dir, "MagPi", "MagPi<NUMB>.pdf"), MagazineLink))
urlList.append(('https://hackspace.raspberrypi.org/issues/', os.path.join(output_dir, "HackSpace", "HackSpaceMagazine<NUMB>.pdf"), MagazineLink))
urlList.append(('https://wireframe.raspberrypi.org/issues/', os.path.join(output_dir, "WireFrame", "Wireframe<NUMB>.pdf"), MagazineLink))
urlList.append(('https://helloworld.raspberrypi.org/issues', os.path.join(output_dir, "HelloWorld", "HelloWorld_<NUMB>.pdf"), MagazineLink))
urlList.append(('https://magpi.raspberrypi.org/books', os.path.join(output_dir, "Books", "<BOOK>"), BookLinks))
urlList.append(('https://wireframe.raspberrypi.org/books/', os.path.join(output_dir, "Wireframe_Books", "<BOOK>"), BookLinks))
urlList.append(('https://hackspace.raspberrypi.org/books/', os.path.join(output_dir, "HackSpace_Books", "<BOOK>"), BookLinks))

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

def CheckAndDownloadFile(url, outfile):
    # Check to make sure the file doesn't already exist, don't bother getting
    # the linked page if it exists, less load on severs.
    if not os.path.isfile(outFile):
        # Get the download page
        page = GetPage(url)
        # Find the iFrame with the actual download link
        #<iframe src="https://magazines-attachments.raspberrypi.org/issues/full_pdfs/000/000/462/original/MagPi99.pdf?1603959693" class="u-hidden"></iframe>
        linkRegEx = "<iframe src=\"(?P<link>.+?)\" class=\"u-hidden\"></iframe>"
        dllink = re.search(linkRegEx, str(page), flags=re.IGNORECASE)

        if dllink is None:
            print("Download link not found")
        else:
            print("Getting :" + outFile)
            if dllink.group("link").startswith("http"):
                url = dllink.group("link")
            else:
                # Get the URL parts we need
                urlParts = urlparse(url)
                # Reconstruct the URL
                url = urlParts.scheme + '://'+ urlParts.netloc +  dllink.group("link")

            r = requests.get(url, allow_redirects=True)
            open(outFile, 'wb').write(r.content)        

# Make sure the output folders is available
for (url, template, _) in urlList:
    dir = os.path.dirname(template)
    if not os.path.exists(dir):
        print("Creating '{0}' now".format(dir))
        os.makedirs(dir)

# Get the links from all the pages, using the RegEx supplied
for (url, template, processor) in urlList:
    print("URL: " + url + " - Template:" + template)
    # Get the primary page, with all the links
    page = GetPage(url)
    # Process the page, get the first link found
    mainLinks = processor(page)

    if len(mainLinks) == 0:
        print("No main link(s) found")
    else:
        for link in mainLinks:            
            # Get the URL parts we need
            urlParts = urlparse(url)
            prependLink = urlParts.scheme + '://'+ urlParts.netloc
            # Check to see if there's a number in the URL (at a certain position)
            fileParts = link.split('/')
            if fileParts[2].isnumeric():
                # Generate the output filename from the template
                outFile = template.replace("<NUMB>", "{:02d}".format(int(fileParts[2])))
                # Check for the link and download
                CheckAndDownloadFile(prependLink + link + "/download", outFile)

                if doBackIssues:
                    # Turn the main link into a template
                    templateLink = (prependLink + link + "/download").replace("/" + fileParts[2] + "/", "/<NUMB>/")
                    # Go from the beginning to one before the last issue.
                    for issueNumb in range(1, int(fileParts[2])):
                        # Generate the output filename from the template
                        outFile = template.replace("<NUMB>", "{:02d}".format(issueNumb))
                        # Check for the link and download
                        CheckAndDownloadFile(templateLink.replace("<NUMB>", str(issueNumb)), outFile)
            else:
                # Do a book template replace
                outFile = template.replace("<BOOK>", fileParts[2] + ".pdf")
                # Generate the download link and pass it off
                CheckAndDownloadFile(prependLink + link + "/download", outFile)

print("Done...")
