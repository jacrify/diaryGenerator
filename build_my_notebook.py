from  notebook_builder import Doc,Page,LinearLinks
from datetime import date,timedelta
import sys

sunday=date.fromisoformat('2021-08-01')
thisweek=f"Week {sunday.strftime('%U, %Y')}"

lastSunday=sunday+timedelta(days=-7)
lastweek=f"Week {lastSunday.strftime('%U, %Y')}"



doc=Doc("pagetemplate.pdf")

# links between top level weekly pages
weeklyLinks=LinearLinks(left=10,top=110)

# links down to daily goal pages from weekly pages
dailyGoalsLinks=LinearLinks(right=-10,top=110)

# Build top level weekly pages, with templates, and give them their outbound links
# Note the daily goal pages do not exist yet, but that's ok!
weeklyRetro=doc.addPage(title=f"Retro for {lastweek}",basepdfname="weeklyRetroTemplate.pdf",toclevel=1)
weeklyRetro.addLinks(weeklyLinks,dailyGoalsLinks)

weeklyPlanner=doc.addPage(title=f"Planner for {thisweek}",basepdfname="weeklyPlannerTemplate.pdf",toclevel=1)
weeklyPlanner.addLinks(weeklyLinks,dailyGoalsLinks)

weeklyDump1=doc.addPage(title=f"Dump 1 for {thisweek}",toclevel=1)
weeklyDump1.addLinks(weeklyLinks,dailyGoalsLinks)

weeklyDump2=doc.addPage(title=f"Dump 2 for {thisweek}",toclevel=1)
weeklyDump2.addLinks(weeklyLinks,dailyGoalsLinks)

weeklyGoals=doc.addPage(title=f"Goals for {thisweek}",basepdfname="weeklyGoalsTemplate.pdf",toclevel=1)
weeklyGoals.addLinks(weeklyLinks,dailyGoalsLinks)


# Link top level pages to each other
weeklyLinks.addLink(weeklyRetro,"R");
weeklyLinks.addLink(weeklyPlanner,"P");
weeklyLinks.addLink(weeklyDump1,"D1");
weeklyLinks.addLink(weeklyDump2,"D2");
weeklyLinks.addLink(weeklyGoals,"G");

# Build one goals page and 9 notes pages for each day of the week
days=[]
for x in range(1,6):
    tempdate=sunday+timedelta(days=x)
    days.append(tempdate)


for daydate in days:
    day=daydate.strftime('%a %-d %b %Y')
    # Each set of daily notes has links to each other
    dailyNotesLinks=LinearLinks(bottom=-500,right=-5,flowdirection="down")

    # First page is a goals page. 
    # Each of the daily pages links back up to the weekly pages, to the other days in the week, and to each other on this day
    dailyGoals=doc.addPage(title=f"{day}: Daily Goals",basepdfname="dailyGoalsTemplate.pdf",toclevel=1)
    dailyGoals.addLinks(weeklyLinks,dailyGoalsLinks,dailyNotesLinks)
    
    # This gets linked "down to" from the weekly pages above
    dailyGoalsLinks.addLink(dailyGoals,f"{day[0]}")

    # It is also linked by each other page on this day
    dailyNotesLinks.addLink(dailyGoals,"G")
    

    #Add index page
    dailyNote=doc.addPage(title=f"{day}: Notes Index")
    dailyNote.addLinks(weeklyLinks,dailyGoalsLinks,dailyNotesLinks)
    
    dailyNotesLinks.addLink(dailyNote,f"I")

    for pageno in range(2,10):
        # These are the individual note pages for a given day 
        dailyNote=doc.addPage(title=f"{day}: Notes {pageno}")
        dailyNote.addLinks(weeklyLinks,dailyGoalsLinks,dailyNotesLinks)
        dailyNotesLinks.addLink(dailyNote,f"{pageno}")


peopleLinks=LinearLinks(left=10,top=110,width=300)
projectLinks=LinearLinks(left=310,top=110,width=300)



doc.render(sys.argv[1])






