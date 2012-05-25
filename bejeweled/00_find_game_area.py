#!/usr/bin/env python

"""
Find a small template on the screen. The output is the X, Y
location of the pixel where the template starts.

This code is from here: http://notes.sovechkin.com/post/6354903838 .

The process is called "template matching" (thanks Yves).
"""

from PIL import Image #@UnresolvedImport
from PIL import ImageChops #@UnresolvedImport
from grab import grab_whole_screen
from time import sleep
import os

TEMPLATE_SIZE = 25 * 25    # if found, stop


def kill_notify():
    os.system('pkill xmessage')

def notify(msg):
    kill_notify()
    os.system('xmessage "{msg}" &'.format(msg=msg))

def matchTemplate(searchImage, templateImage):
    minScore = -1000
    matching_xs = 0
    matching_ys = 0
    out = False
    # convert images to "L" to reduce computation by factor 3 "RGB"->"L"
    searchImage = searchImage.convert(mode="L")
    templateImage = templateImage.convert(mode="L")
    searchWidth, searchHeight = searchImage.size
    templateWidth, templateHeight = templateImage.size
    # make a copy of templateImage and fill with color=1
    templateMask = Image.new(mode="L", size=templateImage.size, color=1)
    #loop over each pixel in the search image
    for xs in xrange(searchWidth-templateWidth+1):
        if out:
            break
        for ys in xrange(searchHeight-templateHeight+1):
            #set some kind of score variable to "All equal"
            score = templateWidth*templateHeight
            # crop the part from searchImage
            searchCrop = searchImage.crop((xs,ys,xs+templateWidth,ys+templateHeight))
            diff = ImageChops.difference(templateImage, searchCrop)
            notequal = ImageChops.darker(diff,templateMask)
            countnotequal = sum(notequal.getdata())
            score -= countnotequal

            if minScore < score:
                minScore = score
                matching_xs = xs
                matching_ys = ys

            if minScore == TEMPLATE_SIZE:
                out = True
                break

    return (matching_xs, matching_ys)
#    im1 = Image.new('RGB', (searchWidth, searchHeight), (80, 147, 0))
#    im1.paste(templateImage, ((matching_xs), (matching_ys)))
##    #searchImage.show()
##    #im1.show()
#    im1.save('template_matched_in_search.png')


def main():
    print "# You have 3 seconds to switch to the game window..."
    notify('Switch to the game window.')
    sleep(3)
    notify('Taking a screenshot.')
    searchImage = grab_whole_screen()
    templateImage = Image.open('assets/template.png')
    notify('Searching...')
    print '# It will take about 20 seconds...'
    x0, y0 = matchTemplate(searchImage, templateImage)
    print 'x0 =', x0
    print 'y0 =', y0
    print '# paste the coordinates to config.py'
    notify('Done.')
    sleep(1)
    kill_notify()

#############################################################################

if __name__ == "__main__":
    main()