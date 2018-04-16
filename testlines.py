
import PIL, PIL.Image, PIL.ImageFilter, PIL.ImageMorph, PIL.ImageDraw, PIL.ImageChops
import pytesseract as t




# horse
##hr = PIL.Image.open('horse.png').convert('1').point(lambda v: v==0)
##hr.show()
##for _ in range(55):
##    print _
####    out = PIL.ImageMorph.MorphOp(patterns=['1(000 .1. 111)->0','1(.00 110 .1.)->0',
####                                           '1(1.0 110 1.0)->0','1(.1. 110 .00)->0',
####                                           '1(111 .1. 000)->0','1(.1. 011 00.)->0',
####                                           '1(0.1 011 0.1)->0','1(00. 011 .1.)->0',
####                                            ]).apply(out)[1]
##    hr = PIL.ImageMorph.MorphOp(patterns=['4(000 .1. 111)->0','4(.00 110 .1.)->0',
##                                            ]).apply(hr)[1]
##hr.show()
##dfdsfs






# real

im = oim = PIL.Image.open('testpng.png-000021.png').convert('1').point(lambda v: v==0)
im.show()




# clean
#im = im.filter(PIL.ImageFilter.FIND_EDGES)
#im = PIL.ImageMorph.MorphOp(op_name="erosion4").apply(im)[1]
#im.show()



# morph version
##out = PIL.ImageMorph.MorphOp(patterns=['1:(... ... ...)->0',
##                                       "4:(000 111 000)->1",
##                                       #"4:(010 101 000)->1",
##                                       "4(000 010 111)->1",
##                                       "4:(001 110 000)->1",
##                                       "4:(011 110 000)->1",
##                                       "4:(000 101 000)->1"]).apply(im)[1]
##out.show()
##fsdsf

# grow, then thin
im = PIL.ImageMorph.MorphOp(op_name='dilation4').apply(im)[1]
im.show()
##for _ in range(5):
##    print _
##    im = PIL.ImageMorph.MorphOp(patterns=['4(000 .1. 111)->0',
##                                            '4(.00 110 .1.)->0']).apply(im)[1]
##im.show()







# collect lines
pixels = im.load()

hlines = []
for y in range(im.size[1]):
    start = None
    end = None
    for x in range(im.size[0]):
        val = pixels[x,y]
        if val:
            if start:
                end = (x,y)
            else:
                start = (x,y)
                #print 'start',start
        else:
            if (end and x - end[0] <= 0):
                pass
            elif start and pixels[x,y+1]:
                end = (x,y)
            elif start and pixels[x,y-1]:
                end = (x,y)
            elif start:
                if x - start[0] > 150:
                    #print 'end',end
                    #print 'line', (start,end)
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
    for y in range(im.size[1]):
        val = pixels[x,y]
        if val:
            if start:
                end = (x,y)
            else:
                start = (x,y)
                #print 'start',start
        else:
            if (end and y - end[1] <= 0):
                pass
            elif start:
                if y - start[1] > 150:
                    #print 'end',end
                    #print 'line', (start,end)
                    vlines.append((start,end))
                start = None
                end = None
            else:
                pass

print len(vlines)

# draw lines
out = PIL.Image.new('1', im.size, 0)
draw = PIL.ImageDraw.Draw(out)
for s,e in hlines:
    draw.line(s+e, fill=255)
for s,e in vlines:
    draw.line(s+e, fill=255)

# thinning
#out = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(out)[1]
#out = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(out)[1]
#out = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(out)[1]
#out = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(out)[1]
out.show()

for _ in range(10):
    print _
##    out = PIL.ImageMorph.MorphOp(patterns=['1(000 .1. 111)->0','1(.00 110 .1.)->0',
##                                           '1(1.0 110 1.0)->0','1(.1. 110 .00)->0',
##                                           '1(111 .1. 000)->0','1(.1. 011 00.)->0',
##                                           '1(0.1 011 0.1)->0','1(00. 011 .1.)->0',
##                                            ]).apply(out)[1]
    out = PIL.ImageMorph.MorphOp(patterns=['4(000 .1. 111)->0','4(.00 110 .1.)->0',
                                           '1(111 111 000)->1','1(110 110 110)->1',
                                            ]).apply(out)[1]
out.show()
    
##edge = PIL.ImageMorph.MorphOp(op_name="edge").apply(out)[1]
##edge.show()
##diff = PIL.ImageChops.difference(out, edge)
##diff.show()
##out.paste(0, mask=diff)



# find corners
out = PIL.ImageMorph.MorphOp(patterns=['1(... ... ...)->0',
                                       '4(010 110 000)->1', #right corner
                                       #'4(010 010 010)->1', #angled corner
                                       '4(000 110 000)->1',#right tip
                                       #'4(000 010 001)->1',#angled tip
                                       '4(010 111 000)->1',#3way junction
                                       '4(010 111 010)->1',#4way junction
                                       ]).apply(out)[1]
out = PIL.ImageMorph.MorphOp(op_name="dilation8").apply(out)[1]
out = PIL.ImageMorph.MorphOp(op_name="dilation8").apply(out)[1]



# thin each corner to one pixel
for _ in range(10):
    print _
    out = PIL.ImageMorph.MorphOp(patterns=['4(000 .1. 111)->0','4(.00 110 .1.)->0',
                                           '1(111 111 000)->1','1(110 110 110)->1',
                                            ]).apply(out)[1]
out.show()



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
                        and abs(p[1]-y) < 5 # around same y as current (+-5pix)
                        and p[0] > x
                        and abs(p[0]-x) > 5 # avoid same cluster
                        ), key=lambda p: p[0]) # closest to the right
    scandowns = sorted((p for p in corners
                        if p != (x,y)
                        and abs(p[0]-x) < 5 # around same x as current (+-5pix)
                        and p[1] > y
                        and abs(p[1]-y) > 5 # avoid same cluster
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



# testread one box

##from PyPDF2 import PdfFileReader, PdfFileWriter
##from PyPDF2.pdf import RectangleObject
##
##with open('pdfs/SYB5.pdf', 'rb') as fobj:
##    reader = PdfFileReader(fobj)
##    page = reader.getPage(20)
##
##    bbox = (x1,y1),(x2,y2) = boxes[0]
##    page.trimBox.lowerLeft = (x1,im.height-y2)
##    page.trimBox.upperRight = (x2,im.height-y1)
##
##    text = page.extractText()
##    print bbox, text

(x1,y1),(x2,y2) = boxes[0]
crop = oim.crop([x1,y1,x2,y2])
crop.show()
text = t.image_to_string(crop, lang='eng+fra')
print text






            
            

