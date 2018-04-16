
import PIL, PIL.Image, PIL.ImageFilter, PIL.ImageMorph, PIL.ImageDraw, PIL.ImageChops
import pytesseract as t


def process(im):
    # grow to connect tiny gaps
    oim = im
    im = PIL.ImageMorph.MorphOp(op_name='dilation4').apply(im)[1]
    #im = PIL.ImageMorph.MorphOp(op_name='dilation4').apply(im)[1]
    
    # collect lines
    hlines,vlines = find_lines(im, 150, maxthick=None)

    # draw lines
    lineimg = PIL.Image.new('1', im.size, 0)
    draw = PIL.ImageDraw.Draw(lineimg)
    for s,e in hlines:
        draw.line(s+e, fill=255)
    for s,e in vlines:
        draw.line(s+e, fill=255)
    lineimg.show()

    

##    # ALT1: thin lines to single pixel
##    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    #lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    #lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    #lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    #lineimg.show()
##    for _ in range(30):
##        print _
##        lineimg = PIL.ImageMorph.MorphOp(patterns=['4(000 .1. 111)->0','4(.00 110 .1.)->0',
##                                                   '1(111 111 000)->1','1(110 110 110)->1',
##                                                    ]).apply(lineimg)[1]
##    lineimg.show()

    # ALT2: collect new lines, only 1 per maxthick pixels
    # TODO: compare all neighbouring lines and get longest one
    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
    lineimg.show()
    hlines,vlines = find_lines(lineimg, 150, maxthick=30, offset=5)

    # draw lines
    lineimg = PIL.Image.new('1', im.size, 0)
    draw = PIL.ImageDraw.Draw(lineimg)
    for s,e in hlines:
        draw.line(s+e, fill=255)
    for s,e in vlines:
        draw.line(s+e, fill=255)
    lineimg.show()


    

    # find corners
    # ALT1: from image corners
    cornimg = PIL.ImageMorph.MorphOp(patterns=['1(... ... ...)->0',
                                           '4(010 110 000)->1', #right corner
                                           '4(000 110 000)->1',#right tip
                                           '4(010 111 000)->1',#3way junction
                                           '1(010 111 010)->1',#4way junction
                                           ]).apply(lineimg)[1]

    PIL.ImageMorph.MorphOp(op_name="dilation8").apply(cornimg)[1].show()

    # thin each corner to one pixel
    corners = []
    pixels = cornimg.load()
    for y in range(cornimg.height):
        for x in range(cornimg.width):
            val = pixels[x,y]
            if val:
                similar = any((abs(x-cx)<10 and abs(y-cy)<10
                              for cx,cy in corners))
                # dont add if a similar one has already been added, < 10 pixels
                if similar:
                    continue
                corners.append((x,y))
                
    newcornimg = PIL.Image.new('1', cornimg.size, 0)
    pixels = newcornimg.load()
    for x,y in corners:
        pixels[x,y] = 255
        
    PIL.ImageMorph.MorphOp(op_name="dilation8").apply(newcornimg)[1].show()

    # ALT2: instead, if we already have all straight connected lines, then just get the list of all their geom intersections
    # ...




    

    # find boxes
    boxes = find_boxes(newcornimg)

    # test
##    for box in boxes:
##        text = get_text(oim, box)
##        print box, text

    # find all lines that are really long
    hlines,vlines = find_lines(lineimg, 1000)
    print hlines

    # draw lines
    tablineimg = PIL.Image.new('1', im.size, 0)
    draw = PIL.ImageDraw.Draw(tablineimg)
    for s,e in hlines:
        draw.line(s+e, fill=255)
    tablineimg.show()

    # two top ones defines the fields region, bottom ones the column/data region
    tabfieldtop = hlines[0][1]
    tabfieldbottom = hlines[1][1]
    tabdattop = hlines[1][1]
    tabdatbottom = hlines[2][1]



    # loop through all topleft corners of boxes inside the fields region, left to right, ignoring ca duplicate x corners

    # for each corner, find ca duplicate x corners

    # loop bboxes of those duplicate corners, top to bottom

    # define field name as their concatenated texts

    # define bbox width as the bottom bbox width

    # define column bbox as same width, but extending from lower fields lines to lower table line

    # add as field obj


    # loop through fields

    # for each, consider its data column bbox

    # loop through column text lines via image_to_data, top to bottom

    # for each text, consider the bottom to be the top of the next text

    # if full height is bigger than the actual text height, consider this to be a header/grouping

    # loop through all fields and check for text/data within the top/bottom range of the text

    # if no data, means this is only the first of multiple lines, consider the bottom to be the top of the next text, and try again

    # if data, add row as dict

    # if firstval is indented, consider a subunit

    

def get_text(im, bbox):
    (x1,y1),(x2,y2) = bbox
    crop = im.crop([x1,y1,x2,y2])
    crop.show()
    text = t.image_to_string(crop, lang='eng+fra')
    print text

def find_lines(im, minlength, maxthick=10, offset=0):
    # collect lines
    pixels = im.load()

    hlines = []
    for y in range(im.size[1]):
        start = None
        end = None

        if maxthick and hlines and abs(y-hlines[-1][0][1]) <= maxthick:
            # dont collect new lines that are close together
            continue
        
        for x in range(im.size[0]):
            val = pixels[x,y]
            if val:
                if start:
                    end = (x,y)
                else:
                    start = (x,y)
                    #print 'start',start
            else:
                if (end and x - end[0] <= 1):
                    pass
                elif start and pixels[x,y+1]:
                    #y+=1
                    end = (x,y)
                elif start and pixels[x,y-1]:
                    #y-=1
                    end = (x,y)
                elif start:
                    if x - start[0] > minlength:
                        #print 'end',end
                        #print 'line', (start,end)
                        start = (start[0],start[1]+offset)
                        end = (end[0],end[1]+offset)
                        hlines.append((start,end))
                    start = None
                    end = None
                else:
                    pass

    print len(hlines)

    vlines = []
    for x in range(im.size[0]):
        start = None
        end = None

        if maxthick and vlines and abs(x-vlines[-1][0][0]) < maxthick:
            # dont collect new lines that are close together
            continue
        
        for y in range(im.size[1]):
            val = pixels[x,y]
            if val:
                if start:
                    end = (x,y)
                else:
                    start = (x,y)
                    #print 'start',start
            else:
                if (end and y - end[1] <= 1):
                    pass
                elif start and pixels[x+1,y]:
                    #x+=1
                    end = (x,y)
                elif start and pixels[x-1,y]:
                    #x-=1
                    end = (x,y)
                elif start:
                    if y - start[1] > minlength:
                        #print 'end',end
                        #print 'line', (start,end)
                        start = (start[0]+offset,start[1])
                        end = (end[0]+offset,end[1])
                        vlines.append((start,end))
                    start = None
                    end = None
                else:
                    pass

    print len(vlines)

    return hlines,vlines

def find_boxes(im):
    out = im
    # create rectangles
    boxes = []
    pixels = out.load()
    def onvals():
        for x in range(out.size[0]):
            for y in range(out.size[1]):
                val = pixels[x,y]
                if val:
                    yield x,y

    corners = list(onvals())
    print len(corners)

    testview = out.convert('RGB')
    draw = PIL.ImageDraw.Draw(testview)

    for x,y in corners:
        scanrights = sorted((p for p in corners
                            if p != (x,y)
                            and abs(p[1]-y) < 20 # around same y as current (+-5pix)
                            and p[0] > x
                            and abs(p[0]-x) > 10 # avoid same cluster
                            ), key=lambda p: p[0]) # closest to the right
        scandowns = sorted((p for p in corners
                            if p != (x,y)
                            and abs(p[0]-x) < 20 # around same x as current (+-5pix)
                            and p[1] > y
                            and abs(p[1]-y) > 10 # avoid same cluster
                            ), key=lambda p: p[1]) # closest from below 

        if not (scanrights and scandowns):
            continue

        scanright = scanrights[0]
        scandown = scandowns[0]
        bbox = [ (x,y), (scanright[0],scandown[1]) ]
        boxes.append(bbox)

        print (x,y), bbox

        draw.rectangle(bbox, fill=None, outline='red')

    testview.show()

    return boxes


if __name__ == '__main__':
    im = PIL.Image.open('testpng.png-000021.png').convert('1').point(lambda v: v==0)
    process(im)

