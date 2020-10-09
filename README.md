# My-Repository

Do you ever find that your photos/videos folder is a total mess? The videos are all at the bottom of the list, your DSLR and Go Pro gives your files meaningless prefixes, and if you use an Android - it very helpfully separates your regular photos from your videos, panorama shots, screenshots and downloads. Helpful as it may be, it still leaves all of your photos in a somewhat scramble - making it difficult to look over yuor day out or trip away in one nice chronological swoop.

Enter, the pre-processing script!

Whilst ultimately, I will get my photos into a relational database - this will take a while to develop and will require a lot of overhead to migrate your files every time you get a new computer and have to reconfigure all of the applications etc. The pre-processing script is a pragmatic solution to organising my files quickly.

The script works by extracting the most relevant date/time stamps available in your media's metadata (e.g. EXIF data) and renaming each file using a uniform prefix. It then goes one further by allowing for a timezone adjustment, and all gives you the chance to provide a meaningful suffix. E.g. 'Val Thorens'.

LIMITATIONS
---
Obviously, this is a script which will programmatically run exactly the same set of rules on all files. Therefore, if you wish to provide some input to a set A of files, and a different input to a Set B of files - you will need to run the script on those two parts separately. You only have two options for input, and so there are two limitations of the script:
1. You can only apply one suffix. So if your skiing holiday in Val Thorens later progressed into a cultural excursion in Geneva, and you wish to have a different suffix for the two sets of files, you will need to run the script separately for each set of files.
2. You can only apply one specific timezone adjustment for all files in scope. So if, alongside your own phone photos (which is probably timezone aware), you are processing the photos received from your friend in Sydney - and whose camera has been set to Sydney time - you will need to run the script on each set of files separately, so that you can calibrate the timezones appropriately.
