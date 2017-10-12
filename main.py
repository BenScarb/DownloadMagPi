from bs4 import BeautifulSoup
import urllib2
import re
import os

# Debug setting
debug = False


# specify the urlof the MagPi page, with the "Download Free" button
base_url = 'https://www.raspberrypi.org/magpi/'
# Place to put the files (Yes, I developed it on windows!)
output_dir = "D:\\MagPi\\"

# Make sure the output folder is available
if not os.path.exists(output_dir):
	print("Creating '{0}' now".format(output_dir))
	os.makedirs(output_dir)

# query the website and return the html to the variable 'page'
page = urllib2.urlopen(base_url)
# parse the html using beautiful soap and store in variable 'soup'
# (Guess this could be done with a reg ex, this seems easier!)
soup = BeautifulSoup(page, 'html.parser')

# Find the "Download Free" link for the latest issue
# It has the CSS Class "pdf-butt", so find the first instance of that.
free_download_link = soup.find('a', attrs={'class': 'pdf-butt'})

if debug:
	print(free_download_link)

# Make sure the download link has an HREF available
if free_download_link.has_attr('href'):
	# Get a HTTP link for the current issue
	current_issue_link = free_download_link['href']
	if debug:
		print(current_issue_link)

	# Use RegEx to find the number of the issue
	issue_val = re.search('MagPi(?P<Numb>\d+)\.pdf', current_issue_link, flags=re.IGNORECASE)

	# Make sure there was something found
	if issue_val != None:
		if debug:
			print(issue_val.group('Numb'))

		# Create the link for looping with (the {0:02s} can now easily be formatted with the wanted issue number)
		multi_download_link = current_issue_link.replace(issue_val.group('Numb') + ".pdf", "{0:02d}.pdf")

		if debug:
			print(multi_download_link)

		# Convert the issue number to an Int (via string as it was Unicode to start with!)
		for i in range(1, int(str(issue_val.group('Numb')))+1):
			# Fill in the issue number with the current number
			to_download = multi_download_link.format(i)
			if debug:
				print(to_download)

			# Extract the filename to use for the download
			this_issue = re.search('MagPi(?P<Numb>\d+)\.pdf', to_download, flags=re.IGNORECASE)
			# Give the user some feed back
			print("Checking for issue {0:02d}, filename {1}, from '{2}'".format(i, this_issue.group(0), to_download))

			# Get the full path and file name to write out to
			output_file = os.path.join(output_dir, this_issue.group(0))

			# Check to see if the download has already been done
			if os.path.exists(output_file):
				# Tell the user the file already exists
				print("File already exists")
			else:
				# Open the remote file, download and write to disk.
				# TODO: add some error checking/Try-Except here!
				download = urllib2.urlopen(to_download)
				print("Downloading file now")
				with open(output_file,'wb') as output:
					output.write(download.read())
