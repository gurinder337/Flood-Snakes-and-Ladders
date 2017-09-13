import pygame
import random
import os.path

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
grey = (224, 224, 224)

avCols = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255,255,0)]       #colours for the player avatars

pygame.init()
pygame.font.init()
txtFont = pygame.font.SysFont("Candara", 30)                        #fonts used throughout the game
txtFont2 = pygame.font.SysFont("Candara", 15)
cTFont = pygame.font.SysFont("Candara", 25)
cTFont.set_bold(True)
cFont = pygame.font.SysFont("Candara", 35)
cFont2 = pygame.font.SysFont("Candara", 60)
bFont = pygame.font.SysFont("Candara", 100)
quoteFont = pygame.font.SysFont("Candara", 50)
avFont = pygame.font.SysFont("Ariel", 45)

clock = pygame.time.Clock()

windWid = 800
windHei = 600
avRad = 25                  #radius of a player avatar
numTiles = 20
tilesHori = 4               #number of tiles in length
tilesVert = 5               #number of tiles in height
tWid = windWid/tilesHori    #i.e. 200
tHei = windHei/tilesVert    #i.e. 120

cWid = 240          #width of the cards
cHei = 160          #height of the cards
border = 2          #size of the border surronding cards, instructions, buttons
picGap = 5          #size of the gap between pictures and the edges of the window
txtGap = 30

minRoll = -2        #the minimum and maximum die roll
maxRoll = 5
minPosRoll = 3      #the minimum required for roll to be considered positive
newRandCard = True
cardI = 0

ground = pygame.display.set_mode((windWid, windHei))            #background surface
bgImg = pygame.transform.scale(pygame.image.load("graphics/newBG_v4.png"), (windWid, windHei))              #background image
mmImg = pygame.transform.scale(pygame.image.load("graphics/newBGNoOverlay_v4.png"), (windWid, windHei))     #main menu background image
blackImg = pygame.transform.scale(pygame.image.load("graphics/blackBg.png"), (windWid, windHei))    #loads and scales an image of the colour black
cardBackImg = pygame.transform.scale(pygame.image.load("graphics/cardBack.jpg"), (cWid, cHei))      #loads and scales the card back image

pygame.display.set_caption("Flood Snakes and Ladders")


class Component():                   #Abstract class to cover general functionality (not important)
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.body = None

    def drawSelf(self): pass    

class Avatar(Component):             #Class for player character avatars
    def __init__(self, id, x, y, tP):
        super().__init__(id, x, y)
        self.tilePos = tP            #the tile number to start on
        self.tilePlac = 1            #the placement on the tile in relation to other avatars (i.e. placement order)
        self.col = avCols[id]        #chooses colour based on id number
        self.lastPlaced = [x, y]     #stores the co-ordinates of where avatar was last placed
        self.txtSurf = avFont.render(str(id+1), False, black)
        self.txtSize = avFont.size(str(self.id))

    def drawSelf(self):
        self.body = pygame.draw.circle(ground, self.col, (int(self.x), int(self.y)), int(avRad))
        ground.blit(self.txtSurf, (self.x-(self.txtSize[0]/2), self.y-(self.txtSize[1]/2)))         #draws number in centre of self

    def changePos(self, x = None, y = None):    #default 'None' allows you to not be required to change both x AND y
        if x != None: self.x = x
        if y != None: self.y = y

class Button(Component):            #Class for buttons that appear on the main menu
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.txtSurf = txtFont.render("<None>", False, black)
        #print("button: " + str(id) + " alive")

    def drawSelf(self):
        pygame.draw.rect(ground, black,(int(self.x-border), int(self.y-border), cWid+(border*2), cHei+(border*2))) #Draws a rect slighter bigger first (the border)
        self.body = pygame.draw.rect(ground, avCols[self.id+1],(int(self.x), int(self.y), cWid, cHei))
        ground.blit(self.txtSurf, (self.x+100, self.y+25))

    def changeTxt(self, t):
        self.txtSurf = bFont.render(t, False, black)

class Instructions(Component):
    def __init__(self, x, y):   
        super().__init__(1, x, y)                           #id just set to 1 because isn't necessary
        self.mainSurf = txtFont.render("", False, black)    #the first, bigger line of text
        self.subSurf = txtFont2.render("", False, black)    #the second, smaller line of text
        self.show = True                                    #whether or not to show instructions

    def drawSelf(self):
        if self.show:   #checks if instructions should be shown first
            pygame.draw.rect(ground, black, (self.x-5-border, self.y-border, (border*2)+max(self.mainSurf.get_rect().width, self.subSurf.get_rect().width)+10, (border*2)+self.subSurf.get_rect().height+45))
            self.body = pygame.draw.rect(ground, white, (self.x-5, self.y, max(self.mainSurf.get_rect().width, self.subSurf.get_rect().width)+10, self.subSurf.get_rect().height+45))
            ground.blit(self.mainSurf, (self.x, self.y))
            ground.blit(self.subSurf, (self.x, self.y+40))

    def changeText(self, main = None, sub = ""):
        if main != None: self.mainSurf = txtFont.render(main, False, black)
        if sub != None: self.subSurf = txtFont2.render(sub, False, black)

    def changePos(self, x = None, y = None):
        if x != None: self.x = x
        if y != None: self.y = y

class Card(Component):            #Class for cards which determine player movement
    def __init__(self, id, x, y):
        super().__init__(id, x, y)
        self.reveal = False

    def drawSelf(self, roll = None):
        global cardI
        global newRandCard
        txtGap = 10               #gap between text on cards and card edge
        #print(str(plyrs[turn].tilePos) +" = tile Pos" + str(tileCat()) +" = cat")
        if self.reveal:
            fctr = 2              #the factor by which the card should grow when clicked on (i.e. fctr 2 -> wid and hei x2)
            lrgX = self.enlargeCoords(fctr)[0]
            lrgY = self.enlargeCoords(fctr)[1]
            pygame.draw.rect(ground, black, (lrgX, lrgY, cWid*fctr, cHei*fctr)) #border
            self.body = pygame.draw.rect(ground, grey, (lrgX+border*fctr, lrgY+border*fctr, (cWid-(border*2))*fctr, (cHei-(border*2))*fctr))

            preface = "Go forward "          #assumes roll > 0 initially
            if roll < 0:
                if newRandCard: cardI = random.randint(0, len(negTxts[tileCat()])-1)
                txt = negTxts[tileCat()][cardI]
                roll = -roll
                preface = "Go back "
                col = red
            elif roll > 0 and roll < minPosRoll:
                if newRandCard: cardI = random.randint(0, len(neuTxts[tileCat()])-1)
                txt = neuTxts[tileCat()][cardI]
                col = grey
            else:
                if newRandCard: cardI = random.randint(0, len(posTxts[tileCat()])-1)
                txt = posTxts[tileCat()][cardI]
                col = green
                
            newRandCard = False
            
            self.body = pygame.draw.rect(ground, col, (lrgX+border*fctr, lrgY+border*fctr, (cWid-(border*2))*fctr, (cHei-(border*2))*fctr))
            titleY = showParagr(catTitles[tileCat()], (lrgX+20, lrgY+20), cTFont, (cWid*fctr)-40)
            #print(lrgY)
            showParagr(txt, (lrgX+20, titleY+10), cFont, (cWid*fctr)-40)
            size = cFont2.size(preface + str(roll))
            ground.blit(cFont2.render(preface + str(roll), False, black), (lrgX+(cWid*fctr)-size[0]-txtGap, lrgY+(cHei*fctr)-size[1]-txtGap))
        else:
            self.body = pygame.draw.rect(ground, grey, (self.x+border, self.y+border, cWid-(border*2), cHei-(border*2)))
            ground.blit(cardBackImg, (self.x, self.y))
        
    def enlargeCoords(self, f = 1):
        if self.y < windHei/2:
            lrgY = 10
            instructs.changePos(y = windHei-instructs.body.height-40)
        else: lrgY = windHei-(cHei*f)-10

        if self.x < windWid/2:
            if self.x < windWid/4: lrgX = 10
            else: lrgX = windWid/2-((cWid*f)/2)
        else: lrgX = windWid-(cWid*f)-10
        
        return (lrgX, lrgY)

def initGraphics(path, highest = 1):  #'highest' = the highest graphics-number (e.g. if num = 30, will look up to qImg30.png)
    gs = []
    for i in range(highest):
        if (os.path.isfile(path + "Picture" + str(i+1) + ".png")):   #if checks if there is an image with given index number
            gs.append(pygame.image.load((path + "Picture" + str(i+1) + ".png")).convert())
            if (gs[i].get_width() > windWid-(picGap)): gs[i] = pygame.transform.scale(gs[i], (windWid-picGap, int(gs[i].get_height()*((windWid-picGap)/gs[i].get_width()))))
            if (gs[i].get_height() > windHei-(picGap)): gs[i] = pygame.transform.scale(gs[i], (int(gs[i].get_width()*((windHei-picGap)/gs[i].get_height())), windHei-picGap))
    print("length of graphics: " + str(len(gs)))
    if len(gs) == 1: return gs[0]               #if there's only 1 picture, just return that
    else: return gs                              #else, return the array

def tileCat():
    pTile = plyrs[turn].tilePos
    if pTile >= 1 and pTile <= 4: return 0
    if pTile >= 5 and pTile <= 8: return 1
    if pTile >= 9 and pTile <= 12: return 2
    if pTile >= 13 and pTile <= 16: return 3
    if pTile >= 17 and pTile <= 20: return 4
    return -1

def showParagr(txt, pos, font, widLimit, color=black, alpha=None):  #method for handling and printing multi-line text to the screen
    words = [word.split(" ") for word in txt.splitlines()]
    space = font.size(" ")[0]
    x, y = pos
    maxWid = pos[0] + widLimit
    for line in words:
        for word in line:
            wordSurf = font.render(word, 0, color)
            wordSurf.set_alpha(alpha)
            wordWid, wordHei = wordSurf.get_size()
            if x + wordWid >= maxWid:
                x = pos[0]
                y += wordHei
            ground.blit(wordSurf, (x, y))
            x += wordWid + space
        x = pos[0]
        y += wordHei
    return y                                                #returns height of paragraph

def swapTiles(array, i1, i2):   #swaps the index of 2 tiles in a given array
    temp = array[i1]
    array[i1] = array[i2]
    array[i2] = temp
    return array

def initTiles():
    ts = []
    tsNum = 0
    for y in (4, 3, 2, 1, 0):   #ranges are backwards to cause tiles to begin from bottom right, upwards and left-wards
        for x in (3, 2, 1, 0):
            ts.append(pygame.Rect(x*tWid, y*tHei, tWid, tHei))
    #below accounts for inverted rows on board       
    ts = swapTiles(ts, 4, 7)
    ts = swapTiles(ts, 5, 6)
    ts = swapTiles(ts, 12, 15)
    ts = swapTiles(ts, 13, 14)
    return ts

def initTxt(path):              #loads text files into String array and returns it
    file = open(path, "r")
    txt = []
    for line in file:
        txt.append(line)
    #print(len(txt))
    if len(txt) == 1: return txt[0]
    else: return txt

def initCards():                #initialises cards, places evenly spaced-apart
    cs = []
    cNum = 0
    width = cWid*3
    widRemain = windWid - width
    widGaps = widRemain/4
    for y in range(2):
        for x in range(3):
            cs.append(Card(cNum, widGaps+(x*(widGaps+cWid)), 125+(y*(30+cHei))))
            cNum += 1
    return cs    

def instructsPos():         #method to determine where instruction position should be based on which player's turn is it, and their location
    if plyrs[turn].x < windWid/2: x = plyrs[turn].x + (avRad)
    else: x = plyrs[turn].x - (max(instructs.mainSurf.get_rect().width, instructs.subSurf.get_rect().width)+10) - (avRad)

    if plyrs[turn].y < windHei/4: y =  plyrs[turn].y + (avRad)
    else: y = plyrs[turn].y - (instructs.subSurf.get_rect().height+45) - (avRad)
    
    return (x, y)       


def rollDie():              #method to handle metaphorical 'die roll' i.e. card selection process
    global dieRoll
    global instructs
    global choosing    

    dieRoll = random.randint(minRoll, maxRoll)
    while dieRoll == 0 or plyrs[turn].tilePos + dieRoll > 20 or plyrs[turn].tilePos + dieRoll <= 0:   #continues dice roll until valid number given
        dieRoll = random.randint(minRoll, maxRoll)
            
    instructs.changeText("Player " + str(turn+1) + ", please pick a card:", "This will determine spaces moved")
    instructs.changePos(40, 40)
    choosing = True
    revealed = False
    for c in range(len(cards)): cards[c].reveal = False #resets cards to 'unrevealed' prior to next roll
    while choosing:    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:               #allows quitting out of application
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if revealed: choosing = False           #if player clicks after card already revealed, break
                for c in range(len(cards)):
                    if cards[c].body.collidepoint(pygame.mouse.get_pos()):
                        cards[c].reveal = True
                        revealed = True
                        instructs.changeText("Player " + str(turn+1) + ", tap to continue", "When you are ready")
        gameLoopUpdate()
        
    if dieRoll == 1 or dieRoll == -1: txtStr = "Player " + str(turn+1) + ", move " + str(dieRoll) + " space"    #for grammar
    else: txtStr = "Player " + str(turn+1) + ", move " + str(dieRoll) + " spaces"
    instructs.changeText(txtStr, "Hold to move")
    instructs.changePos(instructsPos()[0], instructsPos()[1])

def evalPlyrMove(plyr):   #evaluates whether the player has moved their avatar to the correct location  
    global nextTurn
    if plyr.body.colliderect(tiles[(plyr.tilePos-1) + dieRoll]):       #checks player moved to correct tile | -1 to normalise array index to tileNum
        plyr.x = tiles[(plyr.tilePos-1) + dieRoll].x + (avRad*2-10)    #moves piece to central tile location
        plyr.y = tiles[(plyr.tilePos-1) + dieRoll].y + avRad*2
        plyr.tilePos += dieRoll
        ammendCollisions(plyr)
        nextTurn = True                                                 #allows next turn
    else:
        plyr.x = plyr.lastPlaced[0]
        plyr.y = plyr.lastPlaced[1]
        instructs.changeText(sub = "Try again!")

def ammendCollisions(plyr):     #moves player avatars if 2+ are on the same tile
    global plyrs
    plyr.tilePlac = 1   #reset as they would have just landed therefore Plac = 1
    for p in plyrs:
        while p.id != plyr.id and p.tilePos == plyr.tilePos and p.tilePlac == plyr.tilePlac:
            if numPlyrs == 4: plyr.x += (avRad*2) - 8   #squashes avatars together more if 4 players (to fit on 1 tile)
            else: plyr.x += (avRad*2) + 5
            plyr.tilePlac += 1
        print(str(p.id+1) + " tile: " + str(p.tilePos) + " place: " + str(p.tilePlac))

def initPlyrs(num = 1):         #initialises player avatars
    ps = []
    pX = tiles[0].x + avRad*2 - 10
    pY = tiles[0].y + avRad*2
    for p in range(num):
        ps.append(Avatar(p, pX, pY, 1))         #tilePos taken as param is tile[index] +1
        if numPlyrs == 4: pX += (avRad*2) - 8   #squashes avatars together more if 4 players (to fit on 1 tile)
        else: pX += (avRad*2) + 5
    return ps

def initPlyrNumOpts():          #initialises player number options
    opts = []
    width = cWid*3
    widRemain = windWid - width
    widGaps = widRemain/4
    for o in range(3):
        opts.append(Button(o, widGaps+(o*(widGaps+cWid)), 150))
        opts[o].changeTxt(str(o+2))
    return opts

def gameLoopUpdate():           #called every iteration while the game is running
    ground.blit(bgImg,(0,0))

    for p in range(len(plyrs)):
        plyrs[p].drawSelf()
    if choosing:
        toRedraw = None         #variable to determine whether or not to redraw a card to be ontop of the rest (because it was revealed)
        for c in range(len(cards)):
            cards[c].drawSelf(dieRoll)
            if cards[c].reveal: toRedraw = c
        if toRedraw != None: cards[toRedraw].drawSelf(dieRoll)
    instructs.drawSelf()
    pygame.display.update()
    clock.tick(30)
    
def showQuote(tileNum):
    print(tileNum)
    global firstQuote
    cat = tileCat()
    print(cat)
    if firstQuote:
        slide = "first"
        firstQuote = False
    elif tileNum == 20: slide = endSlide
    else:
        print("length: " + str(len(quoteSlides[cat])-1))
        slide = quoteSlides[cat][random.randint(1, len(quoteSlides[cat])-1)]
    viewQuote = True
    sTime = pygame.time.get_ticks()     #takes a start time to work out how long quote has been shown for
    alpha = 0
    while (viewQuote):        
        if (alpha < 240):
            blackImg.set_alpha(alpha)
            if (slide != "first"): slide.set_alpha(alpha)
            alpha = alpha+10
            
        ground.blit(bgImg,(0,0))                            #draws background and avatars in background for underlay
        for p in range(len(plyrs)): plyrs[p].drawSelf()
        ground.blit(blackImg,(0,0))
        if (slide != "first"): ground.blit(slide, ((windWid/2)-(slide.get_width()/2), (windHei/2)-(slide.get_height()/2)))
        else: showParagr(fQTxt, (txtGap, txtGap), quoteFont, windWid-(txtGap), color=white, alpha=alpha)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       #allows user to quit the game
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (alpha == 240):
                    viewQuote = False         #only allows user to close quote once it's fully opaque (not while fading in)
        pygame.display.update()
        clock.tick(30)
        #if (pygame.time.get_ticks() - sTime > 10000): viewQuote = False    #timeout for display of quote

    #quoteSlides[cat][qNum].set_alpha(None) #reset image to fully opaque afterwards

tiles = initTiles()
cards = initCards()
instructs = Instructions(50, 50)
plyrNumOpts = initPlyrNumOpts()

catTitles = initTxt("txts/catTitles.txt")
negTxts = []
for i in range(5):
    negTxts.append(initTxt("txts/negatives/negatives" + str(i+1) + ".txt"))

posTxts = []
for i in range(5):
    posTxts.append(initTxt("txts/positives/positives" + str(i+1) + ".txt"))

neuTxts = []
for i in range(5):
    neuTxts.append(initTxt("txts/neutrals/neutrals" + str(i+1) + ".txt"))
    
quoteSlides = []
for i in range(5):
    quoteSlides.append(initGraphics("graphics/slides/category" + str(i+1) + "/", 20))

fQTxt = initTxt("txts/firstQuote.txt")
endSlide = initGraphics("graphics/slides/end/")

run = True
choosing = False
while run:           #runs code from top everytime a new game begins (after a player wins)
    mainMenu = True
    gameLoop = True
    winner = None
    plyrs = None
    avSelected = False
    turn = -1
    nextTurn = True
    firstQuote = True
    pygame.event.clear()
    while mainMenu:

        instructs.changeText("Welcome to Flood Snakes and Ladders!", "Selected number of players:")
        ground.blit(mmImg,(0,0))
        instructs.drawSelf()
        for o in range(len(plyrNumOpts)):
            plyrNumOpts[o].drawSelf()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   #allows user to quit the game
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for o in range(len(plyrNumOpts)):
                    if plyrNumOpts[o].body.collidepoint(pygame.mouse.get_pos()):
                        numPlyrs = o+2
                        plyrs = initPlyrs(numPlyrs)
                if plyrs != None:
                    mainMenu = False    #quit main menu if user has chosen number of players

        pygame.display.update()
        clock.tick(30)

    while gameLoop:

        if nextTurn:
            showQuote(plyrs[turn].tilePos)
            if turn > -1: plyrs[turn].lastPlaced = [plyrs[turn].x, plyrs[turn].y]   #pre-turn maintenance only run if NOT very first turn (-1)
            turn += 1
            if turn >= len(plyrs): turn = 0 #resets turn counter, allows loops around plyrs
            newRandCard = True
            rollDie()
            nextTurn = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:   #allows user to quit the game
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if plyrs[turn].body.collidepoint(pygame.mouse.get_pos()):
                    avSelected = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if avSelected: evalPlyrMove(plyrs[turn])    #if plyr lets go, evaluate their move
                avSelected = False
                if plyrs[turn].tilePos == 20:
                    showQuote(plyrs[turn].tilePos)
                    winner = turn+1
                    gameLoop = False
                    endScreenStart = pygame.time.get_ticks()

        if avSelected:
            instructs.show = False
            plyrs[turn].changePos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

        gameLoopUpdate()
        if not avSelected: instructs.show = True

    instructs.changeText("Player " + str(winner) + " wins!", "Congradulations") #end game
    instructs.changePos(40, 40)
    while pygame.time.get_ticks() - endScreenStart < 3000:
        gameLoopUpdate()

pygame.quit()
quit()
    
