
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import RectangleObject

with open('pdfs/SYB5.pdf', 'rb') as fobj:
    reader = PdfFileReader(fobj)
    length = reader.getNumPages()
    print length

    for i in range(21-1, length):
        print '-----'
        print i
        page = reader.getPage(i)

        print page.trimBox.lowerLeft, page.trimBox.upperRight

        ll = (0,400)
        ur = (600,600)
        w = abs(ll[0] - ur[0])
        h = abs(ll[1] - ur[1])

        page.mediaBox.lowerLeft = ll
        page.mediaBox.upperRight = ur

        page.cropBox.lowerLeft = ll
        page.cropBox.upperRight = ur

        page.trimBox.lowerLeft = ll
        page.trimBox.upperRight = ur

        page.bleedBox.lowerLeft = ll
        page.bleedBox.upperRight = ur

        page.artBox.lowerLeft = ll
        page.artBox.upperRight = ur

        print page.trimBox.lowerLeft, page.trimBox.upperRight

        outdoc = PdfFileWriter()
        outpage = outdoc.addBlankPage(w,h)
        outpage.trimBox.lowerLeft = ll
        outpage.trimBox.upperRight = ur
        print outpage.trimBox.lowerLeft, outpage.trimBox.upperRight
        
        outpage.mergePage(page)
        print outpage.trimBox.lowerLeft, outpage.trimBox.upperRight

        with open('cropped.pdf', 'wb') as wfobj:
            outdoc.write(wfobj)

        # read from cropped file

        with open('cropped.pdf', 'rb') as rfobj:
            creader = PdfFileReader(rfobj)

##            list(creader.pages)
##            print creader.resolvedObjects
##            print creader.resolvedObjects[(0,3)]['/Contents']
##            print creader.resolvedObjects[(0,3)]['/Resources']
##            print creader.resolvedObjects[(0,3)]['/Resources']['/XObject']
##            print creader.resolvedObjects[(0,3)]['/Resources']['/Font']['/C0_0']
##            print type(creader.resolvedObjects[(0,3)]['/Resources']['/Font']['/C0_0'])
##            fsdf
            
            cpage = creader.getPage(0)
            print cpage.trimBox.lowerLeft, cpage.trimBox.upperRight

            text = cpage.extractText()
            print text

        # test img
        im = page['/Resources']['/XObject']['/Im0']
        print bool(im.getData())

        kjlkj

