import fitz
from datetime import date,timedelta

class Page:
    def __init__(self, title="",titlex=20,titley=250,titlesize=50,basepdfname="",toclevel=0,links=[]):
        self.title = title 
        self.linksets=[]
        self.pageno=0
        self.fitzpage=""
        self.titlecol=fitz.utils.getColor("black")
        self.titlesize=titlesize
        self.titlex=titlex
        self.titley=titley
        self.basepdfname=basepdfname
        self.toclevel=toclevel
        
    
    def addLinks(self,*linksets):
        for linkset in linksets:
            self.linksets.append(linkset)
        return self


    def render(self,fitzdoc):
        self.fitzpage=fitzdoc[self.pageno]
        #render outbound links
        for linkset in self.linksets:
            linkset.render(self)
        #render title
        self.fitzpage.insert_text((self.titlex,self.titley), self.title,color=self.titlecol, overlay=True,fontsize=self.titlesize)





class Links:
    #An abstract class to represent a set of outbound links.
    #
    #Primary responsibilities are:
    #1. hold the details of a set of target pages, with text labels for each link
    #2. render these links when asked on one or more source pages
    #
    #This set of links are generally logically grouped- eg
    #you might have a set of links to pages for each day of the week.
    #This set of links can be rendered on more than one page.
    def __init__(self):
        self.pages=[];
        self.labels={}


    def addLink(self,page,label):
        self.labels[page]=label
        self.pages.append(page);
        

class LinearLinks(Links):
    # Renders a set of links left to right, or top to bottom,
    # as a set of boxes, containing centered label text.
    #
    # Expects one of left / right to be passed in constructor
    # Expects one of top/bottom to be passed in constructor
    #
    # Starting from the point defined by the two elements above,
    # boxes will be laid out either from the left (if "left" is passed)
    # or from the right (if "right" is passed).
    #
    # If right is passed, it can either be expressed as an positive number,
    # in which case it is considered as an absolute x coordinate, or as
    # a negative number, in which case it is considered as an offset from
    # the right edge of the document.
    #
    # Similarly if bottom is passed and is positive, it is considered as
    # an absolute y cooridinate, but if negative it is considered as 
    # an offset from the page bottom.
    #
    # The size of each box can be modified by the width and height args-
    # Note that is the label text is too large it will just not rendered
    #
    # Use flowdirection="right" to choose left to right, 
    # and flowdirection="down" to choose top to bottom
    # The fontsize is also controllable.
    def __init__(self,width=80,height=80,left="",top="",right="",bottom="",flowdirection="right",fontsize=30):
        super().__init__()

        self.left=left
        self.top=top
        self.right=right
        self.bottom=bottom
        self.flowdirection=flowdirection

        if (left=="" and right==""):
            raise Exception("You must set either left or right starting points")
        if (left!="" and right!=""):
            raise Exception("You cannot set both left and right starting points. Choose one")
        if (top=="" and bottom==""):
            raise Exception("You must set either top or bottom starting points")
        if (top!="" and bottom!=""):
            raise Exception("You cannot set both top and bottom starting points. Choose one")
       
        self.width=width
        self.height=height
        self.fontsize=fontsize


    # Render this set of link boxes onto the passed page
    # This method will automatically display a box as inverse color 
    # if the link points back to itself.
    def render(self,page):
        if self.flowdirection=="right":

            if (self.left!=""):
               l=self.left 
            else:
                if (self.right <= 0): #right is expressed as negative offset from right edge
                    #take the right edge, substract the passed offset, then start
                    l=page.fitzpage.rect.x1+self.right -len(self.pages)*self.width

            r=l+self.width

            if (self.top!=""):
                t=self.top  
            else:
                if (self.bottom <= 0): #bottom is expressed as negative offset from bottom edge
                    #self.bottom=page.fitzpage.rect.y1+self.bottom
                    t=page.fitzpage.rect.y1+self.bottom -self.height
            b=t+self.height
        else: #flow down from top
            if (self.left!=""):
               l=self.left 
            else:
                if (self.right <= 0): #right is expressed as negative offset from right edge
                    #take the right edge, substract the passed offset, then start
                    l=page.fitzpage.rect.x1+self.right -self.width

            r=l+self.width

            if (self.top!=""):
                t=self.top  
            else:
                if (self.bottom <= 0): #bottom is expressed as negative offset from bottom edge
                    #self.bottom=page.fitzpage.rect.y1+self.bottom
                    t=page.fitzpage.rect.y1+self.bottom -self.height*len(self.pages)
            b=t+self.height





        boxcol=fitz.utils.getColor("black")

        for target in self.pages :

            if (target.pageno==page.pageno):
                textcol=fitz.utils.getColor("white")
                backcol=fitz.utils.getColor("black")
            else:
                textcol=fitz.utils.getColor("black")
                backcol=fitz.utils.getColor("white")
            r1 = fitz.Rect(l, t, r, b)
            textrect = fitz.Rect(l, t+(self.height/2)-(self.fontsize/2*1.33), r, b)
            page.fitzpage.draw_rect(r1,color=boxcol, fill=backcol, overlay=True)

            if (self.flowdirection=="right"): 
                r=r+self.width
                l=l+self.width
            else:
                t=t+self.height
                b=b+self.height
                


            linkdict = {
                "kind": 1,
                "from": r1,
                "page": target.pageno  
            }
            page.fitzpage.insert_link(linkdict)

            # this line should use link text
            page.fitzpage.insert_textbox(textrect, f"{self.labels[target]}",color=textcol, overlay=True,align=1,fontsize=self.fontsize)



class Doc:
    # Represents the output document
    # This class exists primarily to collect the invidual pages, in the correct order.
    # As the intra pdf linking scheme relies on page number, all pages must be known
    # before links are created.
    #
    # Requires the path to a tempate pdf file when created:
    # the first page of this file will be used as the default
    # template for each page created, if the page itself does
    # not have a dedicated template.
    
    def __init__(self,basepdfname):
        self.pages=[]
        self.fitzdoc = fitz.open() 
        self.basepdfname=basepdfname
        self.toc=[]
    
    def addPage( self, title="",titlex=20,titley=250,titlesize=50,basepdfname="",toclevel=0,links=[]):
        page=Page(title=title,titlex=titlex,titley=titley,titlesize=titlesize,basepdfname=basepdfname,toclevel=toclevel,links=links)
        self.addPages(page)
        return page

    # Add one or more pages into the document.
    # This method will create fitz pages for each doc, however rendering of content
    # is done as a separate pass
    def addPages(self,*pages):
        for page in pages:
            self.pages.append(page)
            page.pageno=len(self.pages)-1
            if (page.basepdfname==""):
                page.basepdf=fitz.open(self.basepdfname)
            else:
                page.basepdf=fitz.open(page.basepdfname)
            #copy tempate into new doc
            self.fitzdoc.insert_pdf(page.basepdf, from_page=0, to_page=0,start_at=-1, rotate=-1, links=True, annots=True, show_progress=0, final=1)
            if page.toclevel!=0:
                self.toc.append([page.toclevel,page.title,page.pageno])

    
    

    # Ask each page to render their own conent- this is done once all pages are added
    # After rendering the document is saved.
    def render(self,outputfilename):
        for page in self.pages:
            page.render(self.fitzdoc);
        self.fitzdoc.set_toc(self.toc, collapse=1)
        self.fitzdoc.save(outputfilename)


