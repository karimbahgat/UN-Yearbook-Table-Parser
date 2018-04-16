
import PIL, PIL.Image, PIL.ImageFilter, PIL.ImageMorph, PIL.ImageDraw, PIL.ImageChops
import pytesseract as t




def group_lines(hlines,vlines):
    hgroups = []
    for hl in hlines:
        # related lines
        related = [l for l in hlines if abs(hl[0][1]-l[0][1]) <= 40 and (hl[0][0] <= l[0][0] <= hl[1][0] or hl[0][0] <= l[1][0] <= hl[1][0]
                                                                         or l[0][0] <= hl[0][0] <= l[1][0])]
        if related:
            xmin = min((l[0][0] for l in related))
            xmax = max((l[1][0] for l in related))
            y = (related[0][0][1] + related[-1][1][1]) / 2
            full = (xmin,y),(xmax,y)
            if not any((abs(full[0][1]-l[0][1]) <= 40 and abs(full[0][0]-l[0][0]) <= 40 for l in hgroups)):
                hgroups.append(full)
        else:
            if not any((abs(hl[0][1]-l[0][1]) <= 40 and abs(hl[0][0]-l[0][0]) <= 40 for l in hgroups)):
                hgroups.append(hl)
    vgroups = []
    for vl in vlines:
        # related lines
        related = [l for l in vlines if abs(vl[0][0]-l[0][0]) <= 40 and (vl[0][1] <= l[0][1] <= vl[1][1] or vl[0][1] <= l[1][1] <= vl[1][1]
                                                                         or l[0][1] <= vl[0][1] <= l[1][1])]
        if related:
            ymin = min((l[0][1] for l in related))
            ymax = max((l[1][1] for l in related))
            x = (related[0][0][0] + related[-1][1][0]) / 2
            full = (x,ymin),(x,ymax)
            if not any((abs(full[0][0]-l[0][0]) <= 40 and abs(full[0][0]-l[0][0]) <= 40 for l in vgroups)):
                vgroups.append(full)
        else:
            if not any((abs(vl[0][0]-l[0][0]) <= 40 and abs(vl[0][0]-l[0][0]) <= 40 for l in vgroups)):
                vgroups.append(vl)
    return hgroups,vgroups

def get_text(im, bbox):
    (x1,y1),(x2,y2) = bbox
    crop = im.crop([x1,y1,x2,y2])
    #crop.show()
    text = t.image_to_string(crop, lang='eng+fra') #+equ
    return text

def find_lines(im, minlength, maxthick=10, offset=0, move=True, mingap=1):
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
                    y += offset
                    start = (x,y)
                    #print 'start',start
            else:
                if (end and x - end[0] <= mingap):
                    pass
                elif move and start and pixels[x,y+1]:
                    y+=1
                    end = (x,y)
                elif move and start and pixels[x,y-1]:
                    y-=1
                    end = (x,y)
                elif start:
                    if x - start[0] > minlength:
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

        if maxthick and vlines and abs(x-vlines[-1][0][0]) < maxthick:
            # dont collect new lines that are close together
            continue
        
        for y in range(im.size[1]):
            val = pixels[x,y]
            if val:
                if start:
                    end = (x,y)
                else:
                    x += offset
                    start = (x,y)
                    #print 'start',start
            else:
                if (end and y - end[1] <= mingap):
                    pass
                elif move and start and pixels[x+1,y]:
                    x+=1
                    end = (x,y)
                elif move and start and pixels[x-1,y]:
                    x-=1
                    end = (x,y)
                elif start:
                    if y - start[1] > minlength:
                        #print 'end',end
                        #print 'line', (start,end)
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
    im = PIL.Image.open('testpng.png-000023.png').convert('1').point(lambda v: v==0)

    # grow to connect tiny gaps
    oim = im
    im = PIL.ImageMorph.MorphOp(op_name='dilation4').apply(im)[1]
    #im = PIL.ImageMorph.MorphOp(op_name='dilation4').apply(im)[1]
    
    # collect lines
    hlines,vlines = find_lines(im, 150, mingap=2, maxthick=None)

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
##    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    lineimg = PIL.ImageMorph.MorphOp(op_name='dilation8').apply(lineimg)[1]
##    lineimg.show()
    hlines,vlines = find_lines(lineimg, 150, maxthick=None, move=True) #30, offset=0, move=1)

    # group lines
    ghlines,gvlines = group_lines(hlines,vlines)

    # draw grouped lines
    lineimg = PIL.Image.new('1', im.size, 0)
    draw = PIL.ImageDraw.Draw(lineimg)
    for s,e in ghlines:
        draw.line(s+e, fill=255)
    for s,e in gvlines:
        draw.line(s+e, fill=255)
    lineimg.show()

    # find corners
    # ALT1: from image corners
##    cornimg = PIL.ImageMorph.MorphOp(patterns=['1(... ... ...)->0',
##                                           '4(010 110 000)->1', #right corner
##                                           '4(000 110 000)->1',#right tip
##                                           '4(010 111 000)->1',#3way junction
##                                           '1(010 111 010)->1',#4way junction
##                                           ]).apply(lineimg)[1]
##
##    PIL.ImageMorph.MorphOp(op_name="dilation8").apply(cornimg)[1].show()
##
##    # thin each corner to one pixel
##    corners = []
##    pixels = cornimg.load()
##    for y in range(cornimg.height):
##        for x in range(cornimg.width):
##            val = pixels[x,y]
##            if val:
##                similar = any((abs(x-cx)<10 and abs(y-cy)<10
##                              for cx,cy in corners))
##                # dont add if a similar one has already been added, < 10 pixels
##                if similar:
##                    continue
##                corners.append((x,y))
##                
##    newcornimg = PIL.Image.new('1', cornimg.size, 0)
##    pixels = newcornimg.load()
##    for x,y in corners:
##        pixels[x,y] = 255
##        
##    PIL.ImageMorph.MorphOp(op_name="dilation8").apply(newcornimg)[1].show()

    # ALT2: instead, if we already have all straight connected lines, then just get the list of all their geom intersections
    isecs = []
    for hline in ghlines:
        for vline in gvlines:
            if hline[0][0] <= vline[0][0] <= hline[1][0] and vline[0][1] <= hline[0][1] <= vline[1][1]:
                x,y = vline[0][0],hline[0][1]
                isecs.append((x,y))

    corners = isecs

    # add corners of really long lines
    hlines = [l for l in ghlines if l[1][0]-l[0][0] > 1000]
    for l in hlines:
        corners.append( l[0] )
        corners.append( l[1] )

    # draw isecs
    cornimg = PIL.Image.new('1', im.size, 0)
    pixels = cornimg.load()
    for x,y in corners:
        pixels[x,y] = 255

    PIL.ImageMorph.MorphOp(op_name="dilation8").apply(cornimg)[1].show()

    # find boxes
    boxes = find_boxes(cornimg)

    # test
##    for box in boxes:
##        text = get_text(oim, box)
##        print box, text

    # find all lines that are really long
    hlines = [l for l in ghlines if l[1][0]-l[0][0] > 1000]
    print hlines

    # draw lines
    tablineimg = PIL.Image.new('1', im.size, 0)
    draw = PIL.ImageDraw.Draw(tablineimg)
    for s,e in hlines:
        draw.line(s+e, fill=255)
    tablineimg.show()

    # two top ones defines the fields region, bottom ones the column/data region
    tabfieldtop = hlines[0][0][1]
    tabfieldbottom = hlines[1][0][1]
    tabdattop = hlines[1][0][1]
    tabdatbottom = hlines[2][0][1]

    

    # loop through all topleft corners of boxes inside the fields region, left to right, ignoring ca duplicate x corners
    fieldboxes = [bbox for bbox in boxes
                  if bbox[1][1] <= tabfieldbottom + 20]
    fieldxs = sorted(set((b[0][0] for b in fieldboxes)))

    # for each corner, find ca duplicate x corners
    fields = []
    for x in fieldxs:
        print x

        g = [bbox for bbox in fieldboxes
             if bbox[0][0] <= x < bbox[1][0]]

        # loop bboxes of those duplicate corners, top to bottom
        g = sorted(g, key=lambda b: b[0][1])
        print g
        
        # define field name as their concatenated texts
        names = []
        for bbox in g:
            names.append( get_text(oim, bbox) or '' )
        print names
        name = '|'.join(names)

        # define bbox width as the bottom bbox width
        x1,x2 = g[-1][0][0],g[-1][1][0]

        # define column bbox as same width, but extending from lower fields lines to lower table line
        y1,y2 = tabdattop,tabdatbottom
        bbox = [(x1,y1),(x2,y2)]
        print bbox

        # add as field obj
        fields.append((name,bbox))

    # for first field, consider its data column bbox
    (x1,y1),(x2,y2) = fields[0][1]
    crop = oim.crop([x1,y1,x2,y2])
    crop.show()
    data = t.image_to_data(crop, lang='eng+fra') # +equ

    # loop through column text lines via image_to_data, top to bottom   
    drows = [[v for v in row.split('\t')] for row in data.split('\n')]
    dfields = drows.pop(0)
    drows = [dict(zip(dfields,row)) for row in drows]
    lines = []
    line = dict(text='')
    for row in drows:
        for k in 'left top width height'.split():
            row[k] = int(row[k])

        # REMEMBER TO TRANSLATE COLUMN COORDS TO FULL IMG COORDS
        row['top'] += y1
        row['left'] += x1
        
        # process    
        if row['word_num'] == '0' and line['text'].strip():
            lines.append(line)
            line = dict(text='')

        if line['text'] and row['text'].strip():
            # update
            bbox = row['left'], row['top'], row['left']+row['width'], row['top']+row['height']
            prevbbox = line['bbox']
            line['bbox'] = min(bbox[0], prevbbox[0]), min(bbox[1], prevbbox[1]), max(bbox[2], prevbbox[2]), max(bbox[3], prevbbox[3])
            line['text'] += ' ' + row['text']
        elif not line['text'] and row['text'].strip():
            # new line
            bbox = row['left'], row['top'], row['left']+row['width'], row['top']+row['height']
            line = dict(text=row['text'], bbox=bbox)
            
    lines.append(line)

    # for each text, consider the bottom to be the top of the next text
    rows = []
    row = dict()
    lines = sorted(lines, key=lambda l: l['bbox'][1])
    for i in range(len(lines)):
        line = lines[i]
        print line

##        rowtop = line['bbox'][1]
##        try:rowbottom = lines[i+1]['bbox'][1]
##        except:rowbottom = line['bbox'][3] # last line
##
##        try:crop.crop([0,rowtop,crop.size[0]-1,rowbottom]).show()
##        except:pass

        # process
        if not row:
            # first new
            row['rowtop'] = line['bbox'][1] - 3
            row['text'] = line['text']
            # if firstval is indented, consider a subunit
            # ...

        else:
            # continued
            row['text'] += '\n' + line['text']

        # if ends with dot ".", add row as dict
        if line['text'].endswith('.') or line['text'].endswith(u'\u2018') \
           or (len(lines) >= i+1 and lines[i+1]['bbox'][1] - line['bbox'][3] > 30): # or if large gap until next line, colon, or is mostly upper caps, add this as header/grouping

            row['rowbottom'] = line['bbox'][3]

            # loop through all fields and check for text/data within the top/bottom range of the text
            vals = []
            for fname,fbox in fields:
                bbox = [(fbox[0][0],row['rowtop']), (fbox[1][0], row['rowbottom'])] # strip away the column edges, 4 pixels
                text = get_text(oim, bbox)
                vals.append(text)
            row['vals'] = vals

            # add and reset
            print row
            rows.append(row)

            row = dict()

    for row in rows:
        # testview
        oim.crop([0,row['rowtop'],oim.size[0]-1,row['rowbottom']]).show()

    import pythongis as pg
    d=pg.VectorData(fields=[f[0].split('|')[-1] for f in fields])
    for r in rows:
        d.add_feature(row=r['vals'])
    d.browse()



