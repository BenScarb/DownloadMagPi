import requests
import re
import os

# Debug setting
debug = False


# specify the urlof the MagPi page, with the "Download Free" button
base_url = 'https://www.raspberrypi.org/magpi/issues/'
base_anchor = '5px;\"><a href=\"(?P<link>.+?pdf)\".+?>Download Free</a>'
base2_url = 'https://hackspace.raspberrypi.org/issues/'
base2_anchor = 'download=\"true\" href=\"(?P<link>.+?\\.pdf\\?[0-9]{0,20})\">Download free PDF</a>'
base3_url = 'https://wireframe.raspberrypi.org/issues/'
base3_anchor = 'download=\"true\" href=\"(?P<link>.+?\\.pdf\\?[0-9]{0,20})\">Download free PDF</a>'

#base2_anchor = '                  href=\"(?P<link>.+?\.pdf\?[0-9]{0,20})\">Download free PDF</a>'
# Place to put the files (Yes, I developed it on windows!)
# CHANGE THIS FOR YOUR OWN PATH
output_dir = "D:\\MagPi\\"

# Global Var, used only in debugging
fileNo = 1

def GetLinks(url, regEx):
	global fileNo
	if debug:
		print("Downloading " + url)

	page = ''
	try:
		r = requests.get(url, allow_redirects=True)
		if debug:
			open(os.join(output_dir, 'Page_' + str(fileNo) + '.txt'), 'wb').write(r.content)
			fileNo += 1
		page = r.content
	except Exception as e:
		print("There was an error")
		print(err)

	if debug:
		print("Now doing a RegEx on the page text with regex='" + regEx + "'")
		print(str(page))

	# Go through the page and find all the "Download Free" links
	return re.findall(regEx, str(page), flags=re.IGNORECASE)


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
if not os.path.exists(hs_path):
	print("Creating '{0}' now".format(hs_path))
	os.makedirs(hs_path)
if not os.path.exists(wf_path):
	print("Creating '{0}' now".format(wf_path))
	os.makedirs(wf_path)


if debug:
	print("Getting links for first URL")
links = GetLinks(base_url, base_anchor)
if debug:
	print("Getting links for second URL")
links += GetLinks(base2_url, base2_anchor)
if debug:
	print("Getting links for third URL")
links += GetLinks(base3_url, base3_anchor)


for link in links:
	print("Looking at {0} now".format(link))

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

		# Work out what sort of PDF it is
		if filename.startswith("MagPi"):
			output_dir = magpi_path
		elif filename.startswith("Essentials"):
			output_dir = essen_path
		elif filename.startswith("Hack"):
			output_dir = hs_path
		elif filename.startswith("HS"):
			output_dir = hs_path
		elif "_HS_" in filename:
			output_dir = hs_path
		elif filename.startswith("Wire"):
			output_dir = wf_path
		elif filename.startswith("WF"):
			output_dir = wf_path
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
			# TODO: add some error checking/Try-Except here
			print("Downloading file now")
			r = requests.get(link, allow_redirects=True)
			open(output_file, 'wb').write(r.content)

print("Done...")
