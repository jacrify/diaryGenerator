# A Hyperlinked PDF Notebook Generator for EInk Tablets

## Introduction and Functionality
This is a simple python library that allows you to generate  custom hyperlinked pdf notebook for use on eink tablets such as the Supernote A5X, Remarkable 1/2, Boox Note Air, etc. You will need some level of python to be able to use, but you should be able to get away with hacking the example.

**For a sample of the kinds of documents this allows you to generate, see the bottom of this page, or look at the sample [here](https://github.com/jacrify/diaryGenerator/raw/main/assets/sample.pdf).**

Currently it supports the following functionality:
- Define a background PDF page used for all pages. You can make these on the Supernote itself if you wish, including with handwriting, and/or edit using a pdf editor (I used PDFPen)
- Override this PDF for specific pages if you wish
- Print a title on each page, if you wish (or embed it in the template PDF)
- Define a set of links to appear on one of more pages, linking to other pages
- Link labels are configurable
- Link sets are currently linear, and can be vertical or horizontal
- Link sets can be positioned relative to any edge of the page (top bottom left right)
- A linkset will indicate if the current page is selected by using inverse colors
- Pages can be added to PDF table of content
- Font size and size of link boxes is configurable
- For the Supernote, setting the output directory to Dropbox allow you to automatically push the resulting file to your Supernote. Your Supernote handwriting will not be impacted and will appear on top of the template, as long as you don't change the order of the pages. (This is awesome)

## Installing
If you want to use this code, you will need to do the following:

- Install Python3 for your platform
- Clone the git repository
- You'll need the pymupdf library to do the heavy lifting (details (here)[https://pymupdf.readthedocs.io/en/latest/]. To install this run the shell command:
`pip3 install fitz`
- Then cd to the directory where the code is, and run
 `python3 build_my_notebook.py "testout.pdf"`
 This should generate the default testout.pdf file.
 
 Now you can edit "build_my_notebook.py" and make it do what you want. This contains the code for stiching together the notebook pages.
 
 The file notebook_builder.py, on the other hand, contains the core classes and documentation on how to use them.
 
 
 ## Key Concepts
 Doc represents that output document.  
 - When created, pass the default template name.
 
 Page represents one page in the output doc. 
 - Add pages one by one by calling doc.addPage. Order matters: the doc will be built from start to finish in the order the pages are added
 - When adding a page you can set title, specific template name, and toclevel. 
 - Set toclevel to 1 to show top level of TOC, 2 to show next level, etc. Leave out to not show page in TOC

Links represents a set of links to be rendered on one or more pages, linking those pages to other pages.
- A single linkset can be dropped onto multiple pages to save time
- The only (current) implementation of links is LinearLinks, which draw links as a line of boxes with text inside them
- LinearLinks can be vertical (created with `flowdirecton=down`) or horizontal (created with `flowdirection=right`)
- Links can be offset from the left, right, top, and bottom edges. One offset for horizontal and vertical axes must be specified so the code knows where to draw. 
- Right and bottom offsets are expressed as negative numbers - `right=-10` draws boxes finishing 10px from right edge of page. `bottom=-10` draws them finishing 10px from bottom
- `left=10` and `top=10` draw boxes 10 px from left and top edges, respectively
- Boxes have a sensible default width, which can be overridden with `width=80` 
- Fontsize also has a sensible default, which can be overridden with `fontsize=20`
- Target pages can be added to the Links object, along with the label for the outbound link, using `addLink(dailyGoals,"G")`
- When rendering a set of links, if the current page is in the link set the link box will be reverse colour. This is useful for navigation.

Links and Pages can be put together in any order. Ie you can create a page, create a Links object, add it to the page, then add some pages to the Links object. 

When you have finished creating all your pages and links, call `doc.render(outputFilename)` to create the output doc.


## Why does this exist?
I recently purchased a Supernote A5x. This is one of a (relatively) new class of eink notebook devices, like a kindle but with a stylus pen for writing notes on. I love it- there are kinds of work that are best done on paper, with pen in hand, but actual paper has never really worked for me. I love the simplicity of erasing, of being able to lasso text and move it. I also love a couple of special features of the A5X: the ability to draw a star anywhere in any doc and then search for all stars, the ability to build dynamic tables of contents, and the ability to take take handwritten notes on book highlights.

However once I'd been using the device for a week I knew there were more things I wanted to make it do. Specifically I wanted some basic template notes to guide me through my weeks and days, and I wanted to be able to easily navigate between various portions of my notebooks. Supernote allows you to follow local links within PDF documents, so I looked into how difficult it would be to generate a my own hyperlinked pdf planner.

The general structure I wanted was as follows:
- At the start of each week I do a simple retro of the previous week. 3 things that went well, 3 things to improve. I want a page for that with a simple template. ![](https://github.com/jacrify/diaryGenerator/raw/main/assets/20210804223640.png)
- Then I look at my calendar and pull out significant events on each day that I need to prepare for. I want a page for that also, with a section for each weekday to take notes in. ![](https://github.com/jacrify/diaryGenerator/raw/main/assets/20210804223702.png)
- I then do a brain dump of everything that is going on in my world. This is pretty freeform but normally takes a couple of pages. ![](https://github.com/jacrify/diaryGenerator/raw/main/assets/20210804223724.png)
- Swapping back and forth between the events and the dump pages, I then try and sketch out 3 significant outcomes I want to achieve in the week. I want a template page for this. ![](https://github.com/jacrify/diaryGenerator/raw/main/assets/20210804223751.png)

Then I get on with my week. For each day of the week:
- I start setting goals for the day with a single templated page. I may refer back to the dumps and weekly goals when doing this.![](https://github.com/jacrify/diaryGenerator/raw/main/assets/20210804223820.png)
- As my day progresses I write notes on my meetings and tasks, in a fairly linear fashion. So I need around 9 pages of space each day just for these, with an index page ![](https://github.com/jacrify/diaryGenerator/raw/main/assets/20210804223908.png)
![](https://github.com/jacrify/diaryGenerator/raw/main/assets/20210804223934.png)
The key things I wanted were:
- I wanted to be able to jump around within the notes very easily, especially between weekly and daily goals, and the various weekly planning pages.
- If I decided the change the system, I wanted to be able to do this with a minimum of effort. Ideally I wanted to be able to make minor changes to the templates mid week without breaking the whole notebook. Changes from week to week I wasn't so worried about, as I will generate a new doc each week.
- I wanted room for future growth. There are a few pdf planners kicking around with hyperlinked monthly and yearly planners. If I decide not to generate a doc each week, I wanted to be able to add functionality as required.


The full doc I generate is available [here](https://github.com/jacrify/diaryGenerator/raw/main/assets/sample.pdf).

Caveats: I'm not a seasoned Pythonista and the code is not especially good idiomatic pythhon. There are no automated tests. Your computer might catch fire. The earth will one day be torched to a cinder as it slowly spirals down into the heart of the sun, followed eons later by the terrible gloom of the stars themselves winking out one by one, and if that happens because of this code it's on you dude not me.
