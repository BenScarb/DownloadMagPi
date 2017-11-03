# DownloadMagPi
Simple Python Script to download the main MagPi magazine (Windows, Linux and Mac)

Edit the main.py or all_issues.py file, change the "output_dir" to the place you want the files stored, then set it running.
It'll open the page, check the RapsberryPi.org site for the latest issue, then download all the issues from 1 to the latest.
Anything that's already in the download folder will be skipped.

main.py uses the "BeautifulSoup3" library for Python
all_issues.py uses a RegEx to search the page for the download links, this also gets ALL the magazine types, not just the main issues.

Run it each month to get the latest issue.  Something for a Cron job :)

TODO
Work out why the TODO list is all on one line!
