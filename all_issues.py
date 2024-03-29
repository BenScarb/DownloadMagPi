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
    linkSearch = '<a class=\"c-button c-button--secondary c-button--block\" href=\"(?P<link>.+?pdf)\">Get PDF</a>'
    return re.findall(linkSearch, str(page), flags=re.IGNORECASE)

def HelloWorldMagazineLink(page):
    linkSearch = '<a class=\"(?:c-issue-actions__link c-link u-text-bold|c-button c-button--secondary u-mb-x2)\" href=\"(?P<link>.+?pdf)\">(?:Download Free PDF|Free Download)</a>'
    return re.findall(linkSearch, str(page), flags=re.IGNORECASE)

def BookLinks(page):
    #<a class="c-button c-button--secondary c-button--block" href="/books/unity-fps/pdf">Free Download</a>
    linkRef = '<a class="c-button c-button--secondary c-button--block" href="(?P<link>.+?)">Get PDF</a>'
    return re.findall(linkRef, str(page), flags=re.IGNORECASE)

# URLs for all the Raspberry Pi Foundation Free magazines and books
# With a locaiton and template filename
urlList = []
urlList.append(('https://magpi.raspberrypi.org/issues', os.path.join(output_dir, "MagPi", "MagPi<NUMB>.pdf"), MagazineLink, "download"))
urlList.append(('https://hackspace.raspberrypi.org/issues/', os.path.join(output_dir, "HackSpace", "HackSpaceMagazine<NUMB>.pdf"), MagazineLink, "download"))
urlList.append(('https://helloworld.raspberrypi.org/issues', os.path.join(output_dir, "HelloWorld", "HelloWorld_<NUMB>.pdf"), HelloWorldMagazineLink, ""))
urlList.append(('https://magpi.raspberrypi.org/books', os.path.join(output_dir, "Books", "<BOOK>"), BookLinks, "download"))
urlList.append(('https://hackspace.raspberrypi.org/books/', os.path.join(output_dir, "HackSpace_Books", "<BOOK>"), BookLinks, "download"))

# Wireframe things need updating
# https://whynowgaming.com/product-category/wireframe-pdf-magazines/
# Seems to be the URL, sadly paged listing not one nice long list.
# Very sadly no more issues, but good for getting the collection
#urlList.append(('https://wireframe.raspberrypi.org/issues/', os.path.join(output_dir, "WireFrame", "Wireframe<NUMB>.pdf"), MagazineLink, "download"))
#urlList.append(('https://wireframe.raspberrypi.org/books/', os.path.join(output_dir, "Wireframe_Books", "<BOOK>"), BookLinks, "download"))

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
        # Find the "Click if it didn't start" link with the actual download URL
        #<a class="c-link" href="/downloads/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBa0FUIiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--d855b2aaf5533eb0d127165dafa32e8cb09fd523/HS%2342_Digital.pdf">click here to get your free PDF</a>.
        #linkRegEx = "<a class=\"c-link\"[ download=\".+?\"]? href=\"(?P<link>.+)\">click here to get your free PDF</a>"
        linkRegEx = "<a class=\"c-link\".+href=\"(?P<link>.+)\">click here to get your free PDF</a>"
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
for (url, template, _, _) in urlList:
    dir = os.path.dirname(template)
    if not os.path.exists(dir):
        print("Creating '{0}' now".format(dir))
        os.makedirs(dir)

# Get the links from all the pages, using the RegEx supplied
for (url, template, processor, link_addition) in urlList:
    if len(link_addition) > 0:
        link_addition = "/" + link_addition
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
                CheckAndDownloadFile(prependLink + link + link_addition, outFile)

                if doBackIssues:
                    # Turn the main link into a template
                    templateLink = (prependLink + link + link_addition).replace("/" + fileParts[2] + "/", "/<NUMB>/")
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
                CheckAndDownloadFile(prependLink + link + link_addition, outFile)

print("Done...")
