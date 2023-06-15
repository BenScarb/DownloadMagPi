
# DownloadMagPi
Python Script to download the main MagPi magazine (Windows, Linux and Mac)

Edit the all_issues.py file, change the "output_dir" to the place you want the files stored, then set it running.
There's an additional "DoBackIssues" flag, set it to True and as well as the latest issues, it'll check all the previous ones too.

all_issues.py uses a RegEx to search the page for the download links, depending on the URLs in the URL list, it'll get all the types of available PDFs from the Foundation.

Run it each month to get the latest issue.  Something for a Cron job :)

Don't forget, if you like the magzines, BUY THEM TOO!
Otherwise there won't be any PDFs to download.

TODO:
 1. ~~Work out why the TODO list is all on one line! (something to do with
    line breaks..)~~ (Used a wysiwyg editor)
 2. Improve Error handling (as there is some now)
 3. Update the Wireframe to look at the legacy links.
 3. Perhaps make it in to a class

