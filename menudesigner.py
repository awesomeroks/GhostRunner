import pygame
import json
from settings import *
run = True #variable for running the main loop
clock = pygame.time.Clock() #maintain fps
win = pygame.display.set_mode((screenWidth, screenHeight+50+100)) #initialize window with variables. window height = screenHeight +50 
pygame.init()# initialize pygame
pygame.display.set_caption(title) #set title of game
pygame.mixer.init() #initialize pygame mixer (sound play)
pygame.mouse.set_visible(True)
run = True

#groups
allElements = pygame.sprite.Group()
textElements = pygame.sprite.Group()
buttons = pygame.sprite.Group()

class Button(pygame.sprite.Sprite):
    def __init__(self, pos, text,textcolor,bgColour,font = bit8font,  visible = True):
        pygame.sprite.Sprite.__init__(self)
        buttons.add(self) #add to button grp
        allElements.add(self)
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

class Text(pygame.sprite.Sprite):
    def __init__(self, pos, text, colour, font):
        allElements.add(self)
        textElements.add(self)
        self.pos = pos
        self.text = text
        self.colour = colour
        self.font = font
        self.textSurface = font.render(self.text, True, color) #renders font
        self.textRect = self.textSurface.get_rect() #gets bounding box of text
    def draw(self):
        win.blit(self.textSurface,self.textRect)
    
while run:
    mousePos = pygame.mouse.get_pos()
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    win.fill(bgColour)
    pygame.draw.line(win,white,(0,screenHeight+50),(screenWidth, screenHeight+50))
    pygame.draw.line(win,white,(0,0),(screenWidth, 0))
    pygame.draw.line(win,white,(screenWidth-1,0),(screenWidth-1, screenHeight+50))
    pygame.draw.line(win,white,(0,0),(0, screenHeight+50))
    pygame.display.update()

pygame.quit()
