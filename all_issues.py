import urllib2
import re
import os

# Debug setting
debug = False


# specify the urlof the MagPi page, with the "Download Free" button
base_url = 'https://www.raspberrypi.org/magpi/issues/'
# Place to put the files (Yes, I developed it on windows!)
# CHANGE THIS FOR YOUR OWN PATH
output_dir = "D:\\MagPi\\"


# Path to MagPi Magazines
magpi_path = os.path.join(output_dir, "Magazines")
# Path to Essentials
essen_path = os.path.join(output_dir, "Essentials")
# Path to Other Magazines
other_path = os.path.join(output_dir, "Other")

# Make sure the output folders is available
if not os.path.exists(magpi_path):
	print("Creating '{0}' now".format(magpi_path))
	os.makedirs(magpi_path)
if not os.path.exists(essen_path):
	print("Creating '{0}' now".format(essen_path))
	os.makedirs(essen_path)
if not os.path.exists(other_path):
	print("Creating '{0}' now".format(other_path))
	os.makedirs(other_path)

if debug:
	print("Downloading " + base_url)

# query the website and return the html to the variable 'page'
response = urllib2.urlopen(base_url)
page = response.read()
response.close()

if debug:
	print("Now doing a RegEx on the page text")

# Go through the page and find all the "Download Free" links
links = re.findall(r"<a href=\"(?P<link>.+?pdf)\".+?>Download Free<\/a>", str(page), flags=re.IGNORECASE)

for link in links:
	print("Looking at {0} now".format(link))

	# Find the last / and extract the file name
	last_pos = link.rfind("/")
	if last_pos == -1:
		print("Link is malformed, unable to process")
	else:
		#grab the filename
		filename = link[last_pos+1:]

		if debug:
			print(filename)

		# Work out what sort of PDF it is
		if filename.startswith("MagPi"):
			output_dir = magpi_path
		elif filename.startswith("Essentials"):
			output_dir = essen_path
		else:
			output_dir = other_path

		# Create the output filename
		output_file = os.path.join(output_dir, filename)


		# Check to see if the download has already been done
		if os.path.exists(output_file):
			# Tell the user the file already exists
			print("File already exists")
		else:
			# Open the remote file, download and write to disk.
			# TODO: add some error checking/Try-Except here!
			download = urllib2.urlopen(link)
			print("Downloading file now")
			with open(output_file,'wb') as output:
				output.write(download.read())

print("Done...")