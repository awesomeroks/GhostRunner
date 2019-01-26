#PLU = PLAYER
'''
Kindly note that some variable names are used similarly as in the references used although no part of the code has been used directly without changes.


References:
https://www.youtube.com/watch?v=3UxnelT9aCo (colour scheme has been used from here. tile based game idea used. settings file idea is used)
https://www.pygame.org/docs/ (pygame documentation)
stackOverFlow for bug fixes

NOTE:
Since I was unable to submit my project files via the google form (file was too large), this folder contains the files omitting the large file.
I have sent the complete working zip file via email to neeldhara.m@iitgn.ac.in




'''
#imports
import threading
import pygame
import json
import random
import pygame.gfxdraw
import time
from settings import *


#inits
run = True #variable for running the main loop
clock = pygame.time.Clock() #maintain fps
dir = {'l':0, 'r':1, 'u':2, 'd':3, 'none':-1} #direction dictionary for character. l = Left, r = right etc..
invDir = {value: key for key, value in dir.items()}
gameOver = False #variable to run the game loop
bulletShoot = False #for shooting storing if bullet has been shot
t = 0 #keeps track of how many times tutorial has been shown
score = 0 #score of player

#spriteGroups

buttons = pygame.sprite.Group() #group for storing buttons
ghostSprites = pygame.sprite.Group() #group for all ghost sprites
wallSprites = pygame.sprite.Group() #group for all walls objects
foodSprites = pygame.sprite.Group() #group for all food objects
bulletHitSprites = pygame.sprite.Group() #group for all objects that bullet can hit

#window and sound init 
win = pygame.display.set_mode((screenWidth, screenHeight+50)) #initialize window with variables. window height = screenHeight +50 
pygame.init()# initialize pygame
pygame.display.set_caption(title) #set title of game

#sounds
pygame.mixer.init() #initialize pygame mixer (sound play)
shootmusic = pygame.mixer.Sound('shoot.wav') #sound when bullet is shot
bgmusic = pygame.mixer.Sound('8bitbgmusic.wav') #background music
electricIntro = pygame.mixer.Sound('electricintro.wav')#intro electric sound
gExplode = pygame.mixer.Sound('gexpl.wav')#sound when ghost explodes
pExplode = pygame.mixer.Sound('pacdie.wav')#sound when plu explodes
pDie = pygame.mixer.Sound('pacdiefinal.wav')#sound when plu dies


#images
#explosion animation images. Its a stop frame animation with 6 images.
exp1 = pygame.image.load('expl1.png')
exp2 = pygame.image.load('exp2.png')
exp3 = pygame.image.load('exp3.png')
exp4 = pygame.image.load('exp4.png')
exp5 = pygame.image.load('exp5.png')
exp6 = pygame.image.load('exp6.png')
explosion = [exp1,exp2,exp3,exp4,exp5] #list to scroll through the frames in the explosion animation

medal = pygame.image.load('medal.png') #medal image for highscore screen

image = pygame.Surface((tileSize, tileSize)) #image for the walls
image.fill(green)

#set mouse visibility
pygame.mouse.set_visible(False)

#fonts
adonideFont = pygame.font.Font('abandoned.ttf', 30) #intro font
smallText = pygame.font.Font('freesansbold.ttf',12)
gothicFont = pygame.font.Font('darkpix.ttf', 60) #title font
bit8font = pygame.font.Font('8bit.ttf', 20) #button and score font
bit8fontsmall = pygame.font.Font('8bit.ttf', 10)

## vars
runLoad = True #locally used variable used in multiple places
i = 0 #local counter variable
voli = 3 #volume adjust button scroll through available volumes
maps = [] #map information is stored here as 1,2,3,4,5 depending on wall or node. 1 is wall others are nodes/empty spaces
gameBegin = False #game variable for running. used in multiple places 
settingsBegin = False #is settings menu running?
quits = False #locally used in multiple places
tutorial = False #is tutorial running?
hs = [] #stores list of highscores
walls = [] #stores the wall locations
ghostPos = [] # for storing valid initialization locations of the ghosts
pluPos = [16,16] #for storing valid init locations of plu



rectArray = [] # for map design 
#initialize rectArray for map design functions
for x in range(0,screenHeight, tileSize):
    tempArray = []
    for y in range(0,screenWidth,tileSize):
        tempArray.append(pygame.Rect((y,x,tileSize,tileSize)))
    rectArray.append(tempArray)
pygame.mouse.set_visible(True)
run = True
#map design variables
startIJ = ()
mapStart = False
notErase = 1 #enables erase functionality
already1 = False #used inside the functions
d,c = 0,0

# CLASS DEFNS

#Food sprite
class food(pygame.sprite.Sprite):
    def __init__(self, pos, visible = True):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos #position
        self.x = pos[0] + 8 #redefine the center and position
        self.y = pos[1] + 8 #''
        foodSprites.add(self) #add to food group
        self.visible = True #visibility is true initially. set to false upon plu eating it
    
    def draw(self):
        if self.visible:
            pygame.gfxdraw.aacircle(win, self.x,self.y, 2, blue) #antialiased circle
            pygame.gfxdraw.filled_circle(win, self.x,self.y, 2, blue)#fill drawn circle
    
    def isEat(self):
        global score
        if self.visible and p.rect.collidepoint((self.x, self.y)): #if plu eats the food, make food invisible
            score += 1 #increase score by one if eaten on only if visible
            self.visible = False #make food invisible once eaten
            
#main player class

class plu(pygame.sprite.Sprite):
    
    def __init__(self, img, pos = [0,0], vel = 1 ):
        pygame.sprite.Sprite.__init__(self)
        self.vel = vel  #velocity of plu
        self.image = img #attribute its image to itself.
        self.image.fill(yellow) #fill image with yellow: player color
        self.rect = img.get_rect() #bounding box of the character
        self.life = 4 #life of plu
        self.pos = pos[0], pos[1] #position of plu
        self.rect.x = pos[0] #set initial position of the rectangle
        self.rect.y = pos[1] #''
        self.x = 150 #used for drawing the life
        self.velx = 0 #for movement in x direction
        self.vely = 0 #for movement in y direction
        self.dir = dir['none'] #direction of plu
    
    def adjustRect(self):
        #function is used for checking collision. Adjust rectangle in direction of movement and then check for collision
        #did this because character gets stuck if the rectangle isnt adjusted before checking
        if self.dir == dir['l']:
            self.rect.x -= self.vel #adjust rectangle coordinates
        elif self.dir == dir['r']:
            self.rect.x += self.vel
        elif self.dir == dir['u']:
            self.rect.y -= self.vel
        elif self.dir == dir['d']:
            self.rect.y += self.vel
    
    def pacDie(self):
        #function for checking and updating if the pacman is dead or is dying(hit)
        global gameOver
        self.life -= 1 #decrease life upon dying
        if self.life <= 0: # if gameover, play exploding sound and gameOver
            pygame.mixer.Channel(1).play(pExplode, 0)
            gameOver = True
        else:
            pygame.mixer.Channel(1).play(pDie, 0) #pacman die sound
        for i in explosion: # exploding animation
            clock.tick(24)
            pygame.display.update(win.blit(i,(self.rect.x-7,self.rect.y-7)))
        x = random.randint(0,int(len(ghostPos)/2))
        self.pos = (posFind())[0] #find init location of the pacman based on current map
        self.rect.x = self.pos[0] #set position of pacman
        self.rect.y = self.pos[1]
        clock.tick(1) #delay for UX
    
    def isDie(self):
        #check if the player dies if collision with ghost occurs
        if pygame.sprite.spritecollideany(self, ghostSprites):
            self.pacDie()
    
    def isCollide(self):
        #collision checking function. Adjust rectangle in direction of motion and check for collision 
        #returns True if collision detected
        self.pos = (self.rect.x, self.rect.y)
        self.adjustRect()       
        ret = pygame.sprite.spritecollideany(self, wallSprites)
        self.rect.x, self.rect.y = self.pos       
        return ret
    
    def shootBullet(self, o):
        o.dir = self.dir
        #set direction of bullet if shot
    
    def draw(self):
        
        win.blit(self.image, self.rect)#draw plu
        for f in foodSprites: #check if food has been eaten
            f.isEat()
        self.isDie() #check if plu dies
        drawText(textRender("LIVES:", bit8font, fireColor),75,500)
        if self.life == 4: #draw life tiles (no of lives remaining)
            win.blit(self.image, pygame.Rect(self.x,485,15,15))
            win.blit(self.image, pygame.Rect(self.x+16,485,15,15))
            win.blit(self.image, pygame.Rect(self.x,501,15,15))
            win.blit(self.image, pygame.Rect(self.x+16,501,15,15))
        elif self.life == 3:
            win.blit(self.image, pygame.Rect(self.x,485,15,15))
            win.blit(self.image, pygame.Rect(self.x,501,15,15))
            win.blit(self.image, pygame.Rect(self.x+16,501,15,15))
        elif self.life == 2:
            win.blit(self.image, pygame.Rect(self.x,485,15,15))
            win.blit(self.image, pygame.Rect(self.x+16,501,15,15))
        elif self.life == 1:
            win.blit(self.image, pygame.Rect(self.x,485,15,15))

def intlists(l1,l2):
    return list(set(l1) & set(l2))
#ghost enemies class
class ghost(pygame.sprite.Sprite):
    def __init__(self, img,color,  pos = [0,0], vel = 1, life = 4):
        pygame.sprite.Sprite.__init__(self)
        self.vel = vel
        ghostSprites.add(self)
        bulletHitSprites.add(self)
        #load all variables passed to self
        self.image1 = img
        
        self.image = img
        self.color = color
        self.image.fill(self.color)
        self.image1.fill(self.color)
        self.life = life
        self.pos = pos

        self.timelimit = 100
        self.times = 0
        self.ghostlim = random.randint(50,500)
        
        self.rect = img.get_rect()
        self.rect.x = pos[0]
        self.steps = 1
        self.rect.y = pos[1]
        self.wantChangeDir = False # wantchangedir is a function. functionality explained in function
        if self.color == red: #x is for displaying the life tiles
            self.x = 90
        elif self.color == orange:
            self.x = 150
        elif self.color == pink:
            self.x = 210
        elif self.color == cyan:
            self.x = 270
        self.die = False #is ghost dead?
        self.dir = dir['r']
    
    def adjustRect(self):
        #same functionality as plu
        if self.dir == dir['l']:
            self.rect.x -= self.vel
        elif self.dir == dir['r']:
            self.rect.x += self.vel
        elif self.dir == dir['u']:
            self.rect.y -= self.vel
        elif self.dir == dir['d']:
            self.rect.y += self.vel
    
    def isCollide(self, fromMain = False, x = None, y = None):
        #same functionality as plu
        pos = (self.rect.x, self.rect.y)
        self.adjustRect()       
        ret = pygame.sprite.spritecollideany(self, wallSprites)
        self.rect.x, self.rect.y = pos
        return ret
    
    def explode(self):
        #explosion animation
        pygame.mixer.Channel(3).play(gExplode)
        for i in explosion:
            clock.tick(24)
            pygame.display.update(win.blit(i,(self.rect.x-7,self.rect.y-7)))
    
    def isHit(self, bulletHit = False):
        #if bullet hits the ghost,  reduce life by 1 and explode. find init position and send ghost back.
        if bulletHit:
            self.life -=1
            self.explode()
            x = random.randint(int(len(ghostPos)/2), len(ghostPos))
            self.pos = (posFind())[1][x]
            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]
            return True
        return False
    
    def perpDirs(self, curDir, preferredDirs):
        #function sets direction perpendicular to current direction
        #preferredDirs is just a helper variable. Its always initialized with all 4 directions
        #preferredDirs gets converted into a list of dirs which are allowed depending on surroundings
        if curDir == dir['l'] or curDir == dir['r']:
            preferredDirs = [dir['u'], dir['d']]
        else:
            preferredDirs = [dir['r'], dir['l']]
        # print([invDir[x] for x in preferredDirs])
        return preferredDirs

    def isNode(self):
        #checksif current tile in which ghost is is a node. i.e., can change its dir or not
        global maps
        i = self.rect.x//tileSize
        p, k = self.rect.x%tileSize, self.rect.y%tileSize
        j = self.rect.y//tileSize
        global maps
        lim = 0
        ret = 0
        if maps[j][i] != 1 and maps[j][i] != 2 and p <= lim and k <= lim:
            ret = maps[j][i]
        return ret
    
    def move(self, x, y):
        
        node = self.isNode() #assigning isNode to var since it might be called many times.

        if self.isCollide() or node:
            self.setwantChangeDir()

        if self.dir == dir['l']:
            self.rect.x -= self.vel
        if self.dir == dir['u']:
            self.rect.y -= self.vel
        if self.dir == dir['r']:
            self.rect.x += self.vel
        if self.dir == dir['d']:
            self.rect.y += self.vel

        self.steps += 1
    
    def setwantChangeDir(self):
        dirs = []
        l = p.rect.x - self.rect.x
        b = p.rect.y - self.rect.y
        modl =abs(l) 
        modb = abs(b)
        if(self.color == orange):
            rad =pow(pow((p.rect.x-self.rect.x),2)+pow((p.rect.y-self.rect.y),2),0.5)
            if rad <=120:
                l = 16 - self.rect.x
                b = 400- self.rect.y
        elif(self.color == pink):
            l+=60
        elif(self.color == cyan):
            l = 2*p.rect.x - ghostRed.rect.x - self.rect.x
            b = 2*p.rect.y - ghostRed.rect.y - self.rect.y

        if l>0:
            dirs.append(dir['r'])
        else:
            dirs.append(dir['l'])

        if b>0:
            dirs.append(dir['d'])
        else:
            dirs.append(dir['u'])

        if self.dir not in dirs:
            self.wantChangeDir = True

        else:
            self.wantChangeDir = False
        perpdirs = self.perpDirs(self.dir, [0,1,2,3])
        tempdirs = intlists(perpdirs, dirs)
        dirs.remove(tempdirs[0])
        tempdirs.extend(dirs)
        for i in dir.values():
            if i not in tempdirs:
                tempdirs.append(i)
        for i in tempdirs:
            self.dir = i
            if not self.isCollide():
                return

    def draw(self,x,y):
        #draws plu and also number of lives
        self.steps%=self.ghostlim
        if self.steps== 0 :
            self.times = self.timelimit
        if self.times == self.timelimit:
            self.image = greenimage
            self.vel = 0 
            self.ghostlim = random.randint(200,1000)
        elif self.times <=0:
            self.image = self.image1
            self.vel = 1
            
        self.times -= 1
        # print(self.steps,self.times)
        if not self.die:
            self.move(x,y)#move b4 drawing
            self.isHit()#check if its hit
            win.blit(self.image, self.rect)

#button class             
class button(pygame.sprite.Sprite):
    def __init__(self, pos, text,textcolor,bgColour,font = bit8font,  visible = True):
        pygame.sprite.Sprite.__init__(self)
        buttons.add(self) #add to button grp
        #set variables to self
        self.pos = pos
        self.text = text
        self.textSurface = font.render(self.text, True, textcolor) #renders font
        self.textRect = self.textSurface.get_rect() #gets bounding box of text
        self.bgColour = bgColour #not hover, not pressed bgColour. setting as transparent( same as bgColour)
        self.textRect.x = pos[0] +5 #setting location of buttton
        self.textRect.y = pos[1] +5
        self.drawRect = self.textRect
        self.drawRect.x -= 5
        self.drawRect.y -= 5
        self.drawRect.width += 5
        self.drawRect.height += 5
        self.font = font
        self.pressed = False ##true  if its pressed
        self.textcolor = textcolor
        self.hover = False #true if mouse hovers over btn
        self.visible = visible #true if btn is to be drawn
    
    def overButton(self, mousePos):
        if self.textRect.collidepoint(mousePos) and not self.pressed:
            self.hover = True
        else:
            self.hover = False
        #sets hover variable to true or false depending on if mouse is hovering over the button

    def draw(self):
        #draws the button according to whether its pressed, not pressed or hovering.
        if self.visible:
            if self.hover and not self.pressed:
                pygame.draw.rect(win, buttonOnHoverColor, self.drawRect)
            elif self.pressed:
                pygame.draw.rect(win, buttonOnPressedColor, self.drawRect)
            else:
                pygame.draw.rect(win, self.bgColour, self.drawRect)            
            self.textSurface = self.font.render(self.text, True, self.textcolor)
            self.textRect = self.textSurface.get_rect()
            self.textRect.x = self.pos[0] + 5
            self.textRect.y = self.pos[1] + 5
            
            #here, rerendering of the text object of the button takes place because its needed in cases like the volume change button
            win.blit(self.textSurface,self.textRect)
hits = []
#bullet class
class bullet(pygame.sprite.Sprite):
    def __init__(self, pos,img = pygame.Surface((2, 2), pygame.SRCALPHA),vel = 2):
        pygame.sprite.Sprite.__init__(self)
        self.vel = vel
        self.image = img
        self.rect = self.image.get_rect()
        self.dir = dir['none']
        self.pos = pos
        self.rect.x = pos[0]
        self.rect.y = pos[1]    
    def draw(self):
        pygame.gfxdraw.aacircle(win, self.rect.x, self.rect.y, 4, bulletColor)
        pygame.gfxdraw.filled_circle(win, self.rect.x, self.rect.y, 4, bulletColor)
        
    def isCollide(self):
        hitObj = pygame.sprite.spritecollideany(self, bulletHitSprites)
        if hitObj in ghostSprites:
            hitObj.isHit(bulletHit = True)
        elif hitObj:
            for w in wallSprites:
                if w.pos == hitObj.pos:
                    w.times = w.timelimit
                    break
  #ghost can disguise itself occasionally . change colour of ghost to wall colour and speed to 0         
        if hitObj:
            global bulletShoot
            bulletShoot = False
            self.rect.x = -110
            self.rect.y = -110
            self.vel = 0 
        return hitObj
    def moveBullet(self):
        global bulletShoot
        # print(self.rect.x,self.rect.y,self.vel, bulletShoot)
        if bulletShoot:
            self.isCollide()
            self.vel = 2
            if self.dir == dir['l']:
                self.rect.x -= self.vel
            if self.dir == dir['u']:
                self.rect.y -= self.vel
            if self.dir == dir['r']:
                self.rect.x += self.vel
            if self.dir == dir['d']:
                self.rect.y += self.vel
            if self.dir == dir['none']:
                self.rect.x = -110
                bulletShoot = False
            
        else:

            self.rect.x = -110
            self.rect.y = -110
            self.vel = 0

wallhitImage = pygame.Surface((tileSize,tileSize))
wallhitImage.fill(wallhitColour)
#walls class  
greenimage = pygame.Surface((tileSize, tileSize))
greenimage.fill(wallColour)
class wall(pygame.sprite.Sprite):
    #wall sprite for walls
    
    def __init__(self, pos, img = pygame.Surface((tileSize,tileSize))):
        pygame.sprite.Sprite.__init__(self)
        wallSprites.add(self)
        bulletHitSprites.add(self) #bullet can hit
        self.timelimit = 10
        self.image = img
        self.times = 0
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.pos = pos
        self.image = greenimage
    
    def draw(self,start = False):
        if self.times == self.timelimit:
            self.image = wallhitImage
            # print('red')
        elif self.times <=0:
            self.image = greenimage
        self.times-= 1
        win.blit(self.image, (self.pos[0], self.pos[1])) #draw wall
        
        

#characters
#Btns
settingsbackBtn = button([450,470], "BACK", white, bgColour,bit8font, False) #back button of options menu
startBtn = button([60,450], "START", white, bgColour, bit8font) #start button of main menu
hsBtn = button([startBtn.textRect.width + 10 + startBtn.textRect.x, 450], "HIGHSCORE", white, bgColour, bit8font)   #highscore button of mainmenu
settingsBtn = button([hsBtn.textRect.width + hsBtn.textRect.x + 10,450], "OPTIONS", white, bgColour, bit8font) #option button of main menu
exitBtn = button([settingsBtn.textRect.width + 10+ settingsBtn.textRect.x,450], "EXIT", white, bgColour, bit8font) #exit button of main menu

def nextLevel():
    #resets vars for next level upon game completion
    mapLoad(True) #load new map after generation
    ghostRed.life = 4 #reset ghost life and alive status
    ghostCyan.life = 4
    ghostPink.life = 4
    ghostOrange.life = 4
    ghostRed.die = False
    ghostCyan.die = False
    ghostPink.die = False
    ghostOrange.die = False
    win.fill(bgColour)
    drawText(textRender("NEXT LEVEL",gothicFont,white),320,250) #display next level
    pygame.display.update()
    clock.tick(0.5) # wait for 2 seconds before starting

def findNodes(tempmaps):
    #finds nodes ( modifies the map with non 1 and non 0 values at locations of nodes)or locations in the tilemap where the ghost can change its direction.
    # i.e., corners, t-shapes, open on all 4 directions etc..
    #returns the modified version of the map.
    # 4 is T shape
    # 5 is L shape
    # 3 is + shape

    for i in range(1,gridHeight-1):
            for j in range(1,gridWidth-1):
                if tempmaps[i][j]!= 1:
                    if  tempmaps[i+1][j] != 1 and tempmaps[i-1][j] != 1 and tempmaps[i][j-1] != 1 and tempmaps[i][j+1]!=1 :
                        tempmaps[i][j] = 3
                    elif tempmaps[i+1][j] != 1 and tempmaps[i-1][j] != 1 and (tempmaps[i][j-1] != 1 or tempmaps[i][j+1] !=1):
                        tempmaps[i][j] = 3
                    elif tempmaps[i][j+1] != 1 and tempmaps[i][j-1] != 1 and (tempmaps[i-1][j] != 1 or tempmaps[i+1][j] !=1):
                        tempmaps[i][j] = 3
                    elif tempmaps[i+1][j] != 1 and tempmaps[i-1][j] != 1 and (tempmaps[i][j-1] != 1 or tempmaps[i][j+1] !=1):
                        tempmaps[i][j] = 3
                    elif tempmaps[i][j+1] == 1 and tempmaps[i][j-1] == 1 and (tempmaps[i-1][j] == 1 or tempmaps[i+1][j] ==1):
                        tempmaps[i][j] = 4
                    elif tempmaps[i+1][j] == 1 and tempmaps[i-1][j] == 1 and (tempmaps[i][j-1] == 1 or tempmaps[i][j+1] ==1):
                        tempmaps[i][j] = 4
                    elif tempmaps[i+1][j] == 1 and tempmaps[i][j+1] == 1:
                        tempmaps[i][j] = 5
                    elif tempmaps[i+1][j] == 1 and tempmaps[i][j+1] == 1:
                        tempmaps[i][j] = 5
                    elif tempmaps[i-1][j] == 1 and tempmaps[i][j-1] == 1:
                        tempmaps[i][j] = 5
                    elif tempmaps[i-1][j] == 1 and tempmaps[i][j-1] == 1:
                        tempmaps[i][j] = 5
                    elif tempmaps[i-1][j] == 1 and tempmaps[i][j+1] == 1:
                        tempmaps[i][j] = 5
                    elif tempmaps[i+1][j] == 1 and tempmaps[i][j-1] == 1:
                        tempmaps[i][j] = 5
    return tempmaps

def viewMaps():
    runLoad = True #local variable for view map menu loop
    for b in buttons: #set all buttons to invisible
        b.visible = False
    n = button([450,485], "BACK", white, bgColour,bit8font, True) #new back button for the view map menu
    mapLoad(nxtLvl = False) #load map from file. dont generate(False)
    while runLoad:
        clock.tick(fps)
        win.fill(bgColour)
        mousePos = pygame.mouse.get_pos() #get mouse position
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quits = True #assign vars to quit through everything
                run = False
                runLoad = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseCheck(mousePos,click = True) # mousecheck checks and assigns vars to buttons if theyre pressed or not
            if event.type == pygame.MOUSEBUTTONUP:
                for q in buttons:
                    q.pressed = False #if the button is not pressed, its pressed value shld be false
        if n.pressed:
            runLoad = False
            clock.tick(5)
            n.pressed = False
        for w in wallSprites:
            w.draw() #draw walls
        drawButtons(mousePos) #draw the buttons 
        pygame.display.update()
    n.visible = False #set back button to invisible

def posFind():
    #finds valid init location of ghost and plu positions
    global pluPos,ghostPos, maps
    for i in range(gridHeight):
        for j in range(gridWidth):
            if maps[i][j] !=1:
                pluPos = [j*tileSize,i*tileSize]
                break
    for i in range(gridHeight-1,-1,-1):
        for j in range(gridWidth-1,-1,-1):
            if maps[i][j] !=1:
                ghostPos.append([j*tileSize,i*tileSize])
    
    return pluPos, ghostPos

def mapLoad(nxtLvl = False):
    #loads the map from file or random generator depending on next level or not
    global maps,walls, wallSprites, foodSprites, ghostPos, pluPos
    walls = []
    wallSprites = pygame.sprite.Group() #redefine wall and food sprite groups to empty as they are going to be new.
    foodSprites = pygame.sprite.Group()
    if nxtLvl == False:
        f = open('map.txt','r') #map stored in map.txt
        a = f.read()
        maps = json.loads(a) #json.loads converts the read text from string to list and assigns it to maps
        f.close()
    else:
        maps = generateMap(200,6,10) #if not going to the next level, generate new map and find its nodes
    maps = findNodes(maps) #find nodes in the map

    #populate the walls using wall sprites after getting info from maps (loaded from file or generated)
    for i in range(int(gridHeight)):
        for j in range(int(gridWidth)):
            if maps[i][j] == 1:
                walls.append(wall([j*tileSize, i*tileSize])) 
            else:
                food([j*tileSize, i*tileSize])
                
    #find valid init positions of plu and ghost and assign them
    global ghostPos
    ghostPos = []
    posFind()
    p.rect.x = pluPos[0]
    p.rect.y = pluPos[1]
    x = random.randint(int(len(ghostPos)/2), len(ghostPos)-1)
    
   
    ghostRed.rect.x = ghostPos[x][0]
    ghostRed.rect.y = ghostPos[x][1]
    x = random.randint(int(len(ghostPos)/2), len(ghostPos)-1)

    ghostCyan.rect.x = ghostPos[x][0]
    ghostCyan.rect.y = ghostPos[x][1]
    x = random.randint(int(len(ghostPos)/2), len(ghostPos)-1)

    ghostPink.rect.x = ghostPos[x][0]
    ghostPink.rect.y = ghostPos[x][1]
    x = random.randint(int(len(ghostPos)/2), len(ghostPos)-1)

    ghostOrange.rect.x = ghostPos[x][0]
    ghostOrange.rect.y = ghostPos[x][1]


p = plu(pygame.Surface((tileSize-1, tileSize-1)), pluPos) #defining instance of plu
b = bullet([-110,-110]) #defining instance of the bullet
   
#defining ghost instances
ghostRed = ghost(pygame.Surface((tileSize, tileSize)),red, pluPos)
ghostPink = ghost(pygame.Surface((tileSize, tileSize)),pink, pluPos)
ghostCyan = ghost(pygame.Surface((tileSize, tileSize)),cyan, pluPos)
ghostOrange = ghost(pygame.Surface((tileSize, tileSize)),orange, pluPos)


#FN DEFNS

def pauseScrn():
    
    q = True
    while q:
        clock.tick(fps)
        drawText(textRender("Paused",gothicFont,white),320,200)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                q = False
    drawWindow()
    for r in range(4500):

        if r <1500:
            drawText(textRender("3",gothicFont,white),320,250)
        elif r <3000:
            drawText(textRender("2",gothicFont,white),320,300)
        else:
            drawText(textRender("1",gothicFont,white),320,350)
        r += 1
        pygame.display.update()
            
def moveSpriteOnPress(o):

    global bulletShoot
    keysPressed = pygame.key.get_pressed() #gets all keys that are pressed as a dictionary with keys = key name and values as boolean
    o.velx = 0 #velx and vely are 0. changed on keypress
    o.vely = 0
    #the following ifs allow for checking of the movement in a particular direction and assigning movement if there is no collision between plu and the walls
    if keysPressed[pygame.K_ESCAPE]:
        pauseScrn()
    if keysPressed[pygame.K_LEFT] :
        o.dir = dir['l']
        if not o.isCollide():
            o.velx = -1*o.vel
        else:
            o.dir = dir['none']
    if keysPressed[pygame.K_RIGHT] :
        o.dir = dir['r']
        
        if not o.isCollide():
            o.velx = o.vel
        else:
            o.dir = dir['none']
    if keysPressed[pygame.K_UP] :
        o.dir = dir['u']
        
        if not o.isCollide():
            o.vely = -1*o.vel
        else:
            o.dir = dir['none']
    if keysPressed[pygame.K_DOWN]:
        o.dir = dir['d']
        
        if not o.isCollide():
            o.vely = 1*o.vel
        else:
            o.dir = dir['none']
    #shoot bullet if space is pressed and play corresponding sound
    if keysPressed[pygame.K_SPACE]:
        if bulletShoot == False:
            bulletShoot = True
            pygame.mixer.Channel(1).play(shootmusic)
            b.rect.x = p.rect.x +8
            b.rect.y = p.rect.y + 8
            b.moveBullet()
            o.shootBullet(b)    

    o.rect.x += o.velx #move plu (in this function plu is passed as o)
    o.rect.y += o.vely

def drawGrid():
    #draws gridlines for mapdesigning
    for x in range(0,screenWidth, tileSize):
        pygame.draw.line(win, gridColour, (x, 0), (x, screenHeight))
    for y in range(0,screenHeight, tileSize):
        pygame.draw.line(win, gridColour, (0, y), (screenWidth, y))

def drawWindow():
    #draws window in mainLoop
    win.fill(bgColour)
    for w in wallSprites:
        w.draw()
    for f in foodSprites:
        if f.visible:
            f.draw()
    b.draw()
    for sprite in ghostSprites:
        sprite.draw(p.rect.x, p.rect.y)
    p.draw()
    drawScore() #draws score of the player
    pygame.display.update()

def drawText(text,xc,yc):
    #draws text on the screen
    x = text.get_rect()
    x.center = (xc,yc)
    win.blit(text, x) 

def textRender(text,font, color):
    #returns rendered textSurface
    return font.render(text, True, color)

ghostRunnerText = textRender("GHOSTRUNNER", gothicFont, fireColor) #often called text

def intro():
    loadingScrn()
    global runLoad,i
    #PRAVEEEN PRESENTS intro
    adonideFont1 = pygame.font.Font('abandoned.ttf', 50) #font with different size
    while runLoad:
        if i == 2300:
            pygame.mixer.Channel(0).play(electricIntro) #electric shock sound
        if i > 2500: #electric shock effect
            if i%2 == 0:
                win.fill(black)
            else:
                win.fill(white)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
        drawText(textRender("Praveen",adonideFont1,white), 300,150)
        drawText(textRender("Presents",adonideFont1,white), 360,200)
        pygame.display.update()
        if i >=3000:
            runLoad = False
            win.fill(white)
            pygame.display.update()
        i+=1
    pygame.time.delay(2000)
    pygame.mixer.Channel(0).play(bgmusic, -1) #play background music
    pygame.time.delay(600)

    runLoad = True
    i = 0

    ##GHOSTRNNER intro
    text = textRender("GHOSTRUNNER",gothicFont, white)
    
    while runLoad:
        clock.tick(fps)
        win.fill(white)
        pygame.draw.circle(win, bgColour, (int(screenWidth/2), int(screenHeight/2)),2*i) #outward going circle
        drawText(text, 320,240)
        pygame.display.update()
        i+=1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
        if 2*i>=screenWidth:
            runLoad = False
    
    runLoad = True
    i = 0

    #erase GhostRunner intro
    while runLoad:
        clock.tick(fps)
        win.fill(bgColour)
        drawText(text, 320,240)
        pygame.draw.rect(win, bgColour,pygame.Rect(140, 200, i, 100))
        i += 1
        pygame.display.update()
        if i>=text.get_rect().width:
            runLoad = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

    runLoad = True
    i = 640
    #ghostRunner load mainScreen
    while runLoad:
        clock.tick(fps)
        win.fill(bgColour)
        drawText(ghostRunnerText, 320,30)
        pygame.draw.rect(win, bgColour,pygame.Rect(140, 0, 6*i, 100))
        pygame.display.update()
        i-=3
        if i<=0:
            runLoad = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

def waitForSpace():
    #function waits for keyboard press and upon keyboard press, quits the function
    ret = True
    while ret:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                ret = False
            if event.type == pygame.QUIT:
                exit(0)

def mouseCheck(mousePos,click = True, hover= False, exclude = []):
    #function checks if the buttons are hovered or pressed and sets  button vars accordingly
    for b in buttons:
        if b.visible and b.textRect.collidepoint(mousePos) :
            if b not in exclude:
                if click:
                    b.pressed = not b.pressed
                elif hover:
                    b.hover = True
        else:
            b.hover = False


#vars for intro anim are global since introAnim is called many times
i = 0
j = -100
k = -250
l = -300
m = -350

def isNextLvl():
    #checks if its the next level or not. Next level if all the foodSprites are eaten (not visible)
    for f in foodSprites:
        if f.visible == True:
            return False
    return True

def introAnim():
    #animation in the main screen
    global i,j,k,l,m
    #moving sprites animation
    pygame.draw.rect(win, yellow,pygame.Rect(i,240,50,50))
    pygame.draw.rect(win, cyan, pygame.Rect(k, 180,50,50))
    pygame.draw.rect(win, pink, pygame.Rect(l, 300,50,50))
    pygame.draw.rect(win, red, pygame.Rect(m, 180,50,50))
    pygame.draw.rect(win, orange, pygame.Rect(j, 300,50,50))
    #reset location if it goes outside the screen
    if i>screenWidth+50:
        i = -50
    if j>screenWidth+50:
        j = -150
    if k>screenWidth+50:
        k = -250
    if l>screenWidth+50:
        l = -300
    if m>screenWidth+50:
        m = -350
    i+=1
    j+=1
    k+=1
    l+=1
    m+=1

def tutorialscreen():
    #displays the tutorial
    #screen 1
    win.fill(bgColour)
    pygame.draw.rect(win, yellow, pygame.Rect(250,240,100,100))
    drawText(textRender("THIS IS YOUR CHARACTER", bit8font, white),320,500)
    drawText(textRender("Press any key to continue", smallText, white), 320,50)
    pygame.display.update()
    waitForSpace()
    #screen2
    win.fill(bgColour)
    pygame.draw.rect(win, red, pygame.Rect(430,240,100,100))
    pygame.draw.rect(win, orange, pygame.Rect(310,240,100,100))
    pygame.draw.rect(win, pink, pygame.Rect(190,240,100,100))
    pygame.draw.rect(win, cyan, pygame.Rect(70,240,100,100))
    drawText(textRender("THESE ARE YOUR ENEMIES", bit8font, white),320,500)
    drawText(textRender("Press any key to continue", smallText, white), 320,50)
    pygame.display.update()
    waitForSpace()
    win.fill(bgColour)
    #screen3
    drawText(textRender("Press any key to continue", smallText, white), 320,50)
    drawText(textRender("USE ARROW KEYS TO MOVE", bit8font, white), 320,100)
    drawText(textRender("USE SPACE TO SHOOT", bit8font, white), 320,150)
    drawText(textRender("AVOID ENEMIES", bit8font, white), 320,200)
    drawText(textRender("EAT FOOD", bit8font, white), 320,250)
    drawText(textRender("NAVIGATE THE WALLS", bit8font, white), 320,300)
    drawText(textRender("YOU HAVE 4 LIVES", bit8font, white), 320,350)
    drawText(textRender("All the best!", gothicFont, green), 320,480)
    drawText(textRender("You lose 1 point for each second spent", adonideFont, white), 320,400)
    pygame.display.update()
    waitForSpace()   
    #end of tut

def gameOverScrn(): 
    #screen to show when game is over
    global gameOver,score,bulletShoot
    bulletShoot = False
    b.rect.x = -110
    b.vel = 0
    runLoad = True
    pygame.mouse.set_visible(True) #use of mouse is needed
    menuBtn = button([450,470], "MENU", white,bgColour) #back to menu button
    exitBtn.visible = False #exitbtn shld not be visible

    hs.append(score) #add score to list of highscores
    hs.sort(reverse = True) #sort highscores in descending order
    
    while runLoad:
        clock.tick(fps) #tick fps times
        win.fill(bgColour) #fill with bgColour
        mousePos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quits = True
                run = False
                runLoad = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseCheck(mousePos,click = True) #check for mouse activity
            if event.type == pygame.MOUSEBUTTONUP:
                for q in buttons:
                    q.pressed = False
        if menuBtn.pressed:
            runLoad = False
            gameBegin = False
            clock.tick(5)
        drawButtons(mousePos) #draw Buttons 
        drawText(textRender("Game Over",gothicFont,fireColor), 320,250) #draw gameover text
        drawText(textRender("YOUR SCORE:",bit8font,white), 300,290)
        drawText(textRender("HIGHSCORE:",bit8font,white), 300,320)
        drawText(textRender(str(hs[0]),bit8font,yellow), 440,320)
        drawText(textRender(str(score),bit8font,yellow), 440,290)
        pygame.display.update() #update the display
    
    startBtn.visible = True
    menuBtn.visible = False
    settingsBtn.visible = True
    hsBtn.visible = True
    exitBtn.visible = True
    gameOver = False
    #reset
    
    p.life = 4
    ghostRed.life = 4
    ghostCyan.life = 4
    ghostPink.life = 4
    ghostOrange.life = 4
    score = 0

def hsScrn():
    #function shows highscore
    runLoad = True
    pygame.mouse.set_visible(True)
    menuBtn = button([450,470], "MENU", white,bgColour)
    exitBtn.visible = False
    startBtn.visible = False
    a = medal.get_rect()
    a.x = 130
    a.y = 150
    hs.sort(reverse = True)
    settingsBtn.visible = False
    hsBtn.visible = False
    while runLoad:
        clock.tick(fps)
        win.fill(bgColour)
        mousePos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quits = True
                run = False
                runLoad = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseCheck(mousePos,click = True)
            if event.type == pygame.MOUSEBUTTONUP:
                for q in buttons:
                    q.pressed = False
        if menuBtn.pressed:
            runLoad = False
            clock.tick(5)
        drawText(textRender("Highscores",gothicFont,fireColor), 320,30)
        win.blit(medal,a)
        drawText(textRender( str(hs[0]),bit8font,yellow), 323,130)
        drawText(textRender(str(hs[1]),bit8font,white), 207,170)
        drawText(textRender( str(hs[2]),bit8font,fireColor), 436,95 + 100*1)
        drawButtons(mousePos)
        pygame.display.update()

    startBtn.visible = True
    menuBtn.visible = False
    settingsBtn.visible = True
    hsBtn.visible = True
    exitBtn.visible = True

def loadingScrn():
    tipsfile = open("tips.txt",'r')
    tipslist = tipsfile.readlines()
    tipsfile.close()
    for i in range(len(tipslist)):
        tipslist[i] = tipslist[i].strip()
    print(tipslist)
    randinteger = random.randint(0,len(tipslist)-1)

    for i in range(500):
        clock.tick(fps)
        win.fill(bgColour)
        drawText(textRender("LOADING", gothicFont, white),320,260)
        pygame.draw.rect(win, fireColor,pygame.Rect(188,300,i*0.55,50))
        drawText(textRender("Tip:" + tipslist[randinteger], bit8fontsmall, green), 320,400)
        pygame.display.update()
    for i in range(100):
        clock.tick(fps)
    win.fill(bgColour)
    pygame.display.update()
        
def mainGameLoop():
    #the loop where the main game runs
    global tutorial, run, gameBegin, quits,t,gameOver,score
    pygame.mouse.set_visible(False)
    if t == 0: #run tut screen iff first run in game
        tutorialscreen()
        t = 1
    mapLoad() #load map for playing
    m = 0 #counter for score reduction
    
    

    while gameBegin and not gameOver:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quits = True      
                exitScrn()
                pygame.quit()
                exit(0)
            if event.type == pygame.K_ESCAPE:
                gameBegin = False
                break
        m+=1
        moveSpriteOnPress(p)
        if isNextLvl():
            nextLevel()
        if m%fps == 0: #reduce score by 1 as each second passes
            score -= 1
        b.moveBullet()
        drawWindow()
        
        if gameOver:
            gameBegin = False
            break
        if quits:
            run = False
            gameBegin = False
        
def drawScore():
    #draw the score of the game
    drawText(textRender("SCORE:" + str(score), bit8font, white),500,500)

def settingsLoop():
    #settings menu loop
    global quits, settingsBegin, voli
    pygame.mouse.set_visible(True)

    startBtn.visible = False
    settingsBtn.visible = False
    hsBtn.visible = False
    exitBtn.visible = False
    #set menu buttons visibility to false

    volPos = ['MUTE','LOW', 'MEDIUM', 'HIGH'] #volume states

    #initialize local buttons
    volumeBtn = button([200,130], volPos[voli], yellow,bgColour,bit8font)
    mapGenBtn = button([50,230], "CREATE MAPS", yellow, bgColour, bit8font)
    viewMapBtn = button([50,330], "VIEW MAPS", yellow, bgColour, bit8font)
    mapLoad()
    while settingsBegin:
        mousePos = pygame.mouse.get_pos()
        clock.tick(fps)
        settingsbackBtn.visible = True
        mouseCheck(mousePos,click = False, hover = True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quits = True
                run = False
                settingsBegin = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseCheck(mousePos,click = True)
            if event.type == pygame.MOUSEBUTTONUP:
                for q in buttons:
                    q.pressed = False
        if volumeBtn.pressed: #volume adjustment
            volumeBtn.text = volPos[(voli+1)%4]
            voli += 1
            voli %= 4 #loop back to index 0 upon completion
            if voli == 3:
                pygame.mixer.Channel(0).set_volume(1)
                pygame.mixer.Channel(1).set_volume(1)
            elif voli == 2:
                pygame.mixer.Channel(0).set_volume(0.66)
                pygame.mixer.Channel(1).set_volume(0.66)
            elif voli == 1:
                pygame.mixer.Channel(0).set_volume(0.33)
                pygame.mixer.Channel(1).set_volume(0.33)
            elif voli == 0:
                pygame.mixer.Channel(0).set_volume(0)
                pygame.mixer.Channel(1).set_volume(0)
            clock.tick(5)
        if mapGenBtn.pressed: #open map designer on clicking that button
            viewMapBtn.visible = False
            mapGenBtn.visible = False
            settingsbackBtn.visible = False
            volumeBtn.visible = False
            mapDesign()
        else:
            viewMapBtn.visible = True
            startBtn.visible = False
            settingsBtn.visible = False
            mapGenBtn.visible = True
            hsBtn.visible = False
            exitBtn.visible = False
            settingsbackBtn.visible = True
            volumeBtn.visible = True
        if viewMapBtn.pressed: #view map if that button is clicked
            viewMaps()
            clock.tick(5)
        win.fill(bgColour)
        drawText(textRender("OPTIONS", gothicFont,fireColor),320,30) #draw text for the screen
        drawText(textRender("VOLUME: ",bit8font,white),130,140)
        if settingsbackBtn.pressed:
            settingsBegin = False 
        for btn in buttons: #draw buttons for that screen
            btn.draw()
        pygame.display.update()
    viewMapBtn.visible = False
    startBtn.visible = True
    settingsBtn.visible = True
    mapGenBtn.visible = False
    hsBtn.visible = True
    exitBtn.visible = True
    settingsbackBtn.visible = False
    volumeBtn.visible = False
    
def exitScrn():
    pygame.mixer.fadeout(2400) #fadeout music
    i = 0
    runLoad = True
    t = textRender("Thank You", gothicFont,bgColour)
    a = t.get_rect()
    a.center = (int(screenWidth/2)), (int(screenHeight/2))  #center the thank you text
    p, q = a.center
    while runLoad: #closing screen animation
        clock.tick(fps)
        pygame.draw.circle(win, bgColour, (int(screenWidth/2), int(screenHeight/2)), 100+6*i)
        pygame.draw.circle(win, white, (int(screenWidth/2), int(screenHeight/2)),2*i)
        drawText(t,p,q)
        pygame.display.update()
        i+=1
        if 2*i>=screenWidth:
            runLoad = False
   
def drawButtons(mousePos):
    #draws all buttons and checks for hovering
    for i in buttons:
        i.overButton(mousePos)
        i.draw()
    
def mapfn(mousePos):
    #map designer
    global  startIJ,d,c, already1, mapStart, notErase
    d,c = mousePos #store current x and y
    if not ( d< screenWidth and c < screenHeight): #dont proceed if the click isnt within the grid area
        return
    if d <= screenWidth and c <=screenHeight:
        if mapStart == False: #see if the first click has happened yet
            mapStart = True
            already1 = False
            for i in range(gridHeight):
                for j in range(gridWidth):
                    if rectArray[i][j].collidepoint(mousePos):
                        startIJ = (i,j)
                        if(maps[int(rectArray[i][j].y/tileSize)][int(rectArray[i][j].x/tileSize)] == int(notErase)):
                            already1 = True
                        maps[int(rectArray[i][j].y/tileSize)][int(rectArray[i][j].x/tileSize)] = int(notErase) #assign the start position with value 1 in the map
                        break
        else:
            mapStart = False #reset this variable to show one iteration is over
            a,b = startIJ
            c = int(c/tileSize)
            d = int(d/tileSize)

            #fill all tiles with appropriate number
            if b == d:#top down filling
                if(a>c):
                    for i in range(c,a+1):
                        maps[int(rectArray[i][d].y/tileSize)][d] = int(notErase) 
                else:
                    for i in range(a,c+1):
                        
                        maps[int(rectArray[i][d].y/tileSize)][d] = int(notErase)
            elif a==c:#left right filling
                if(b>d):
                    for i in range(d,b+1):
                        maps[a][int(rectArray[a][i].x/tileSize)] = int(notErase)
                else:
                    for i in range(b,d+1):
                        maps[a][int(rectArray[a][i].x/tileSize)] = int(notErase)
            else:
                if(already1 == False):
                    maps[int(rectArray[a][b].y/tileSize)][int(rectArray[a][b].x/tileSize)] = int(not notErase) # if the second click is not in lines parallel to axes, unfill the start

            startIJ = ()
            findNodes(maps) # find nodes in the designed map
    else:
        c = d = 0 #reset vars

def generateMap(limit,mindist,maxdist, l = 1):
    #generates random map using drunken walk algorithm
    I = 0
    J = 0
    tempmaps = [[1 for x in range(gridWidth)] for y in range(gridHeight)] #fill all tiles with walls
    write = 2
    prevdirection = -1 # previous direction of walking in loop
    prevlim = -1 #previous steps walked 
    direction = random.randint(0,4) #direction of walking
    for j in range(l):
        J = random.randint(1,gridWidth-1) #start random position
        I = random.randint(1,gridHeight-1) #start random position
        tempmaps[I][J] = 0 #assign start position as non wall
        for i in range(limit):
            lim = (random.randint(mindist,maxdist+1))
            while lim%2 != 0:
                lim = (random.randint(mindist,maxdist+1)) #get an even distance to be walked since only then you will get self intersecting loops

            if prevdirection == 0 or prevdirection == 1: #walk in a perpendicular direction to current direction
                direction = random.randint(2,4)
            else:
                direction = random.randint(0,2)
            
            #fill limit number of tiles with tunnels in specified direction not considering the boundaries
            if direction == 0 and I!=gridHeight-1:
                for i in range(lim):
                    if I>=gridHeight-lim:
                        break
                    I+=1
                    tempmaps[I][J] = write
                    
            elif direction == 1 and I!=0:
                for i in range(lim):
                    if I<=lim:
                        break
                    I-=1
                    tempmaps[I][J] = write
            elif direction == 2 and J!=gridWidth-1:
                for i in range(lim):
                    if J>=gridWidth-lim:
                        break
                    J+=1
                    tempmaps[I][J] = write
            elif direction == 3 and J!=0:
                for i in range(lim):
                    if J<=lim:
                        break
                    J-=1
                    tempmaps[I][J] = write

            prevdirection = direction
            prevlim = lim
        
        tempmaps = findNodes(tempmaps) #find nodes of generated map
    return tempmaps

redImage = pygame.Surface((tileSize, tileSize))
redImage.fill(red)
whiteImage = pygame.Surface((tileSize, tileSize))
whiteImage.fill(white)
pinkImage = pygame.Surface((tileSize, tileSize))
pinkImage.fill(pink)
def mapDesign():
    #main loop/screen for mapDesigning function

    #init local buttons
    finishbtn = button([490,480], "FINISH", white, buttonBG)  
    b = button([10,480], "ERASE",white, buttonBG)
    generateButton = button([290,480], "GENERATE", white, buttonBG)
    clearButton = button([140,480], "CLEAR", white, buttonBG)    
    
    global maps,mapStart, notErase
    runLoad = True
    while runLoad:
        clock.tick(fps)
        win.fill(bgColour)
        mousePos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseCheck(mousePos)
                notErase = int(not b.pressed)
                mapfn(mousePos)
            if event.type == pygame.MOUSEBUTTONUP:
                for i in buttons:
                    if i is not b:
                        i.pressed = False
        if finishbtn.pressed:
            f = open("map.txt", 'w')
            
            f.write(json.dumps(maps))      #json dumps allows to store var in file as string. load with json.loads
            f.close()
            runLoad = False
        if generateButton.pressed: #generate map if that button is presssed
            maps = generateMap(200,6,10)
            maps = findNodes(maps)
            clock.tick(5)
        if clearButton.pressed: #clear map if that button is pressed
            maps = [[0 for x in range(gridWidth)] for y in range(gridHeight)]

        drawGrid()
        for i in range(gridHeight): #draw filled tiles (walls)
            for j in range(gridWidth):
                if maps[i][j] == 1:
                    win.blit(image, rectArray[i][j])
                elif maps[i][j] == 3:
                    win.blit(redImage, rectArray[i][j])
                elif maps[i][j] == 4:
                    win.blit(whiteImage, rectArray[i][j])
                elif maps[i][j] == 5:
                    win.blit(pinkImage, rectArray[i][j])
        if mapStart == True:
            if d< screenWidth and c < screenHeight: #draw guiding lines if map designing has begun
                x = (int(d/tileSize)*tileSize)+int(tileSize/2)
                y = (int(c/tileSize)*tileSize)+int(tileSize/2)
                pygame.draw.line(win, white, (x,0), (x, screenHeight))
                pygame.draw.line(win, white, (0,y), (screenWidth, y))
        drawButtons(mousePos)
        pygame.display.update()
    b.visible = False
    clearButton.visible = False
    generateButton.visible = False
    finishbtn.visible = False

# /////// GAME LOOP//////////

mapLoad() #load the map from file upon first run
intro() #run intro screen

pygame.mouse.set_visible(True)
hsfile = open('hs.txt', 'r')
hs = json.loads(hsfile.read()) #read highscores from file
hsfile.close()
while run:
    bulletShoot = False
    b.rect.x = -110
    b.rect.y = -110
    b.vel = 0
    hits = []
    clock.tick(fps)
    mousePos = pygame.mouse.get_pos()
    mouseCheck(mousePos,click = False, hover = True)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            mouseCheck(mousePos,click = True)
        if event.type == pygame.MOUSEBUTTONUP:
            
            for q in buttons:
                q.pressed = False
    
    #main game running
    #DRAW
    win.fill(bgColour)
    drawText(ghostRunnerText, 320,30)
    for btn in buttons:
        btn.draw()
    introAnim() #draw the moving character animation
    pygame.display.update()
    if exitBtn.pressed: #exit if that button is pressed
        run = False
    if gameBegin: #start game
        mainGameLoop()
        gameOverScrn()
        gameBegin = False
        startBtn.pressed = False
    if settingsBegin: #start settingsmenu 
        settingsLoop()
    if startBtn.pressed: #start game if that button is pressed
        gameBegin = True
        gameOver = False
        score = 0
        mapLoad()
        startBtn.visible = False
        settingsBtn.visible = False
        hsBtn.visible = False
    if settingsBtn.pressed: #start options menu if that button is pressed
        settingsBegin = True
    if hsBtn.pressed: #start highscore menu if that button is pressed
        hsScrn()    

#end of game
exitScrn() #show exit screen
hs.sort(reverse = True)
hsfile = open('hs.txt', 'w')
hsfile.write(json.dumps(hs)) #write highscsores to file
hsfile.close()

pygame.quit()
