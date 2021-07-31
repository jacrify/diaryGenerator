import fitz

class Page:
    def __init__(self, title="",titlex=20,titley=250,titlesize=50,basepdfname="",toclevel=0):
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
        
    
    def addLinkSet(self,*linksets):
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





class LinkSet:
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


    def addPage(self,page,label):
        self.labels[page]=label
        self.pages.append(page);
        


class HorizontalLinkSet(LinkSet):
    # Renders a set of links left to right or right to left,
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
    # The fontsize is also controllable.
    def __init__(self,width=80,height=80,left="",top="",right="",bottom="",fontsize=30):
        super().__init__()

        self.left=left
        self.top=top
        self.right=right
        self.bottom=bottom

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
    
        
        if (self.left!=""):
            l=self.left 
        else:
            if (self.right <= 0): #right is expressed as negative offset from right edge
                self.right=page.fitzpage.rect.x1+self.right
            l=self.right-len(self.pages)*self.width

        r=l+self.width

        if (self.top!=""):
            t=self.top  
        else:
            if (self.bottom <= 0): #bottom is expressed as negative offset from bottom edge
                self.bottom=page.fitzpage.rect.y1+self.bottom
            t=self.bottom-self.height
        b=t+self.height

        boxcol=fitz.utils.getColor("black")

        for target in self.pages:

            if (target.pageno==page.pageno):
                textcol=fitz.utils.getColor("white")
                backcol=fitz.utils.getColor("black")
            else:
                textcol=fitz.utils.getColor("black")
                backcol=fitz.utils.getColor("white")
            r1 = fitz.Rect(l, t, r, b)
            textrect = fitz.Rect(l, t+(self.height/2)-(self.fontsize/2*1.33), r, b)
            page.fitzpage.draw_rect(r1,color=boxcol, fill=backcol, overlay=True)
            r=r+self.width
            l=l+self.width


            linkdict = {
                "kind": 1,
                "from": r1,
                "page": target.pageno  #need right page number here from links
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
    def render(self):
        for page in self.pages:
            page.render(self.fitzdoc);
        self.fitzdoc.set_toc(self.toc, collapse=1)
        self.fitzdoc.save("/Users/john/Dropbox/Supernote/INBOX/testout.pdf")

def buildDoc():

    doc=Doc("pagetemplate.pdf")

    # links between top level weekly pages
    weeklyLinkSet=HorizontalLinkSet(left=10,top=110)

    # links down to daily goal pages from weekly pages
    dailyGoalsLinkSet=HorizontalLinkSet(right=-10,top=110)

    # Build top level weekly pages, with templates, and give them their outbound links
    # Note the daily goal pages do not exist yet, but that's ok!
    weeklyRetro=Page(title="Retro",basepdfname="weeklyRetroTemplate.pdf",toclevel=1).addLinkSet(weeklyLinkSet,dailyGoalsLinkSet)
    weeklyDump1=Page(title="Weekly Dump 1",toclevel=1).addLinkSet(weeklyLinkSet,dailyGoalsLinkSet)
    weeklyDump2=Page(title="Weekly Dump 2",toclevel=1).addLinkSet(weeklyLinkSet,dailyGoalsLinkSet)
    weeklyGoals=Page(title="Weekly Goals",basepdfname="weeklyGoalsTemplate.pdf",toclevel=1).addLinkSet(weeklyLinkSet,dailyGoalsLinkSet)

    # Add pages into the doc
    doc.addPages(weeklyRetro,weeklyDump1,weeklyDump2,weeklyGoals)

    # Link top level pages to each other
    weeklyLinkSet.addPage(weeklyRetro,"R");
    weeklyLinkSet.addPage(weeklyDump1,"D1");
    weeklyLinkSet.addPage(weeklyDump2,"D2");
    weeklyLinkSet.addPage(weeklyGoals,"G");

    # Build one goals page and 9 notes pages for each day of the week
    days=['Monday','Tuesday','Wednesday','Thursday','Friday']
    for day in days:
        # Each set of daily notes has links to each other
        dailyNotesLinkSet=HorizontalLinkSet(bottom=-5,right=-5)

        # First page is a goals page. 
        # Each of the daily pages links back up to the weekly pages, to the other days in the week, and to each other on this day
        dailyGoals=Page(title=f"{day}: Daily Goals",basepdfname="dailyGoalsTemplate.pdf",toclevel=1).addLinkSet(weeklyLinkSet,dailyGoalsLinkSet,dailyNotesLinkSet)
        
        # This gets linked "down to" from the weekly pages above
        dailyGoalsLinkSet.addPage(dailyGoals,f"{day[0]}")

        # It is also linked by each other page on this day
        dailyNotesLinkSet.addPage(dailyGoals,"G")
        
        # Add page to doc
        doc.addPages(dailyGoals)


        for pageno in range(1,10):
            # These are the individual note pages for a given day 
            dailyNote=Page(title=f"{day} Notes {pageno}").addLinkSet(weeklyLinkSet,dailyGoalsLinkSet,dailyNotesLinkSet)
            doc.addPages(dailyNote)
            dailyNotesLinkSet.addPage(dailyNote,f"{pageno}")

    doc.render() 




   

buildDoc()
