import pygame
import os
import numpy as np
import neat
import itertools
pygame.init()

#Basic game info
name = "Chess"
boardWidth = 800
boardHeight = boardWidth
borderSize = 20
markingSize = 5
legalMoveRadius = 10
imageSize = 60
imageError = 1
tileSize = boardWidth // 8
marginSize = 100
board_x = list(range(borderSize, boardWidth + borderSize, tileSize))
board_y = list(range(marginSize + borderSize, boardHeight + marginSize + borderSize, tileSize))
board_coords = []

for i in board_x:
    for j in board_y:
        board_coords.append([i, j])

gameWindow = pygame.display.set_mode((boardWidth + borderSize * 2, boardHeight + borderSize*2 + marginSize*2))
pygame.display.set_caption(name)
p1Col = 'white'
p2Col = 'black'

if p1Col == 'white':
    p1Turn = True
else:
    p1Turn = False

#Load chess piece images
pawn_white = pygame.image.load('./Chess_plt60.png')
pawn_black = pygame.image.load('./Chess_pdt60.png')
rook_white = pygame.image.load('./Chess_rlt60.png')
rook_black = pygame.image.load('./Chess_rdt60.png')
knight_white = pygame.image.load('./Chess_nlt60.png')
knight_black = pygame.image.load('./Chess_ndt60.png')
bishop_white = pygame.image.load('./Chess_blt60.png')
bishop_black = pygame.image.load('./Chess_bdt60.png')
king_white = pygame.image.load('./Chess_klt60.png')
king_black = pygame.image.load('./Chess_kdt60.png')
queen_white = pygame.image.load('./Chess_qlt60.png')
queen_black = pygame.image.load('./Chess_qdt60.png')

#Define the board
class board(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def drawTiles(self, win, mouseClicked, selected_location, legal_moves):
        for i in self.x:
            if np.mod(i//tileSize, 2) == 0:
                next_col = 'white'
            else:
                next_col = 'black'

            for j in self.y:
                if next_col == 'black':
                    if [i, j] == selected_location and mouseClicked == True:
                        if legal_moves == []:
                            pygame.draw.rect(win, (225, 0, 0), (i, j, tileSize, tileSize))
                            pygame.draw.rect(win, (169, 169, 169), (i + markingSize, j + markingSize, tileSize - markingSize*2, tileSize - markingSize*2))
                        else:
                            pygame.draw.rect(win, (0, 225, 0), (i, j, tileSize, tileSize))
                            pygame.draw.rect(win, (169, 169, 169), (i + markingSize, j + markingSize, tileSize - markingSize*2, tileSize - markingSize*2))
                    else:
                        pygame.draw.rect(win, (169, 169, 169), (i, j, tileSize, tileSize))
                    next_col = 'white'

                else:
                    if [i, j] == selected_location and mouseClicked == True:
                        if legal_moves == []:
                            pygame.draw.rect(win, (225, 0, 0), (i, j, tileSize, tileSize))
                            pygame.draw.rect(win, (255, 255, 255), (i + markingSize, j + markingSize, tileSize - markingSize*2, tileSize - markingSize*2))
                        else:
                            pygame.draw.rect(win, (0, 225, 0), (i, j, tileSize, tileSize))
                            pygame.draw.rect(win, (255, 255, 255), (i + markingSize, j + markingSize, tileSize - markingSize*2, tileSize - markingSize*2))       
                    else:
                        pygame.draw.rect(win, (255, 255, 255), (i, j, tileSize, tileSize))
                    next_col = 'black'

    def drawBorder(self, win):
        win.fill((212, 175, 55))

    def drawMargin(self, win):
        #Upper margin
        pygame.draw.rect(win, (210, 105, 30), (0, 0, boardWidth+borderSize*2, marginSize))

        #Lower margin
        pygame.draw.rect(win, (210, 105, 30), (0, boardHeight + borderSize*2 + marginSize, boardWidth+borderSize*2, marginSize))

#Chess pieces
class pawn(object):

    def __init__(self, coord, opp_coords, own_coords, col, player, moved, board_coords):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col
        self.player = player
        self.moved = moved
        self.board_coords = board_coords

    def legal_moves(self):
        legals = []
        if self.moved == False:
            if self.player == 1:
                if [self.x, self.y - tileSize] not in self.opp_coords:
                    legals.append([self.x, self.y - tileSize])
                if [self.x, self.y - tileSize*2] not in self.opp_coords:
                    legals.append([self.x, self.y - tileSize*2])                    
            else:
                if [self.x, self.y + tileSize] not in self.opp_coords:
                    legals.append([self.x, self.y + tileSize])
                if [self.x, self.y + tileSize*2] not in self.opp_coords:
                    legals.append([self.x, self.y + tileSize*2])
        else:
            if self.player == 1:
                if [self.x, self.y - tileSize] not in self.opp_coords:
                    legals.append([self.x, self.y - tileSize])
            
            else:
                if [self.x, self.y + tileSize] not in self.opp_coords:
                    legals.append([self.x, self.y + tileSize])

        if self.player == 1:
            if [self.x - tileSize, self.y - tileSize] in self.opp_coords:
                legals.append([self.x - tileSize, self.y - tileSize])
            if [self.x + tileSize, self.y - tileSize] in self.opp_coords:
                legals.append([self.x + tileSize, self.y - tileSize])

        else:
            if [self.x - tileSize, self.y + tileSize] in self.opp_coords:
                legals.append([self.x - tileSize, self.y + tileSize])
            if [self.x + tileSize, self.y + tileSize] in self.opp_coords:
                legals.append([self.x + tileSize, self.y + tileSize])


        #Delete coordinate in legals if it is outside the board
        if legals != []:
            for i in range(len(legals)):
                try:
                    if legals[i] not in board_coords:
                        del legals[i]
                except IndexError:
                    pass

        #Delete coordinate in legals if it overlaps with own chess pieces
        if legals != []:
            for i in range(len(legals)):
                try:
                    if legals[i] in self.own_coords:
                        del legals[i]
                except IndexError:
                    pass

        return legals

    def draw(self, win):
        if self.col == 'white':
            win.blit(pawn_white, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])
        else:
            win.blit(pawn_black, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])

class rook(object):
    def __init__(self, coord, opp_coords, own_coords, col, board_coords):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col
        self.board_coords = board_coords

    def draw(self, win):
            if self.col == 'white':
                win.blit(rook_white, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])
            else:
                win.blit(rook_black, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])

class knight(object):
    def __init__(self, coord, opp_coords, own_coords, col, board_coords):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col
        self.board_coords = board_coords

    def legal_moves(self):
        legals = []
        legals.append([self.x + tileSize * 2, self.y + tileSize])
        legals.append([self.x + tileSize * 2, self.y - tileSize])
        legals.append([self.x - tileSize * 2, self.y + tileSize])
        legals.append([self.x - tileSize * 2, self.y - tileSize])
        legals.append([self.x + tileSize, self.y + tileSize * 2])
        legals.append([self.x + tileSize, self.y - tileSize * 2])
        legals.append([self.x - tileSize, self.y + tileSize * 2])
        legals.append([self.x - tileSize, self.y - tileSize * 2])

        if legals != []:
            for i in range(len(legals)):
                try:
                    if legals[i] not in board_coords:
                        del legals[i]
                except IndexError:
                    pass

        if legals != []:
            for i in range(len(legals)):
                try:
                    if legals[i] in self.own_coords:
                        del legals[i]
                except IndexError:
                    pass

        return legals

    def draw(self, win):
            if self.col == 'white':
                win.blit(knight_white, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])
            else:
                win.blit(knight_black, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])

class bishop(object):
    def __init__(self, coord, opp_coords, own_coords, col, board_coords):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col
        self.board_coords = board_coords

    def draw(self, win):
            if self.col == 'white':
                win.blit(bishop_white, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])
            else:
                win.blit(bishop_black, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])

class queen(object):
    def __init__(self, coord, opp_coords, own_coords, col, board_coords):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col
        self.board_coords = board_coords

    def draw(self, win):
            if self.col == 'white':
                win.blit(queen_white, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])
            else:
                win.blit(queen_black, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])

class king(object):
    def __init__(self, coord, opp_coords, own_coords, col, player, moved, board_coords):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col
        self.player = player
        self.moved = moved
        self.board_coords = board_coords

    def draw(self, win):
            if self.col == 'white':
                win.blit(king_white, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])
            else:
                win.blit(king_black, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])

#Drawing game window
def redrawGameWindow(win, board, p1Pos, p2Pos, p1Pieces, p2Pieces, mouseClicked, selected_location, legal_moves = []):
    #Draw board
    board.drawBorder(win)
    board.drawTiles(win, mouseClicked, selected_location, legal_moves)
    board.drawMargin(win)

    #Draw pieces
    for i in range(16):
        if p1Pos[i] != '':
            p1Pieces[i].draw(win)
        if p2Pos[i] != '':
            p2Pieces[i].draw(win)

    #Draw legal moves
    if legal_moves != []:
        for i in legal_moves:
            pygame.draw.circle(win, (0, 225, 0), (i[0] + tileSize//2, i[1] + tileSize//2), legalMoveRadius)

    pygame.display.update()

#Initiate values and positions
mousePos = (0, 0)
mouseClicked = False

p1Pos = []
p2Pos = []
p1Pieces = []
p2Pieces = []

#Pawn positions
for i in board_x:
    p1Pos.append([i, marginSize + borderSize + tileSize * 6])
    p2Pos.append([i, marginSize + borderSize + tileSize])

#Chess piece positions
for i in board_x:
    p1Pos.append([i, marginSize + borderSize + tileSize * 7])
    p2Pos.append([i, marginSize + borderSize])

#Pawns
for i in range(8):
    p1Pieces.append(pawn(p1Pos[i], p2Pos, p1Pos, player = 1, col = p1Col, moved = False, board_coords = board_coords))
    p2Pieces.append(pawn(p2Pos[i], p1Pos, p2Pos, player = 2, col = p2Col, moved = False, board_coords = board_coords))

#Chess pieces
for i in range (8, 16):
    if i in [8, 15]:
        p1Pieces.append(rook(p1Pos[i], p2Pos, p1Pos, col = p1Col, board_coords = board_coords))
        p2Pieces.append(rook(p2Pos[i], p1Pos, p2Pos, col = p2Col, board_coords = board_coords))

    elif i in [9, 14]:
        p1Pieces.append(knight(p1Pos[i], p2Pos, p1Pos, col = p1Col, board_coords = board_coords))
        p2Pieces.append(knight(p2Pos[i], p1Pos, p2Pos, col = p2Col, board_coords = board_coords))

    elif i in [10, 13]:
        p1Pieces.append(bishop(p1Pos[i], p2Pos, p1Pos, col = p1Col, board_coords = board_coords))
        p2Pieces.append(bishop(p2Pos[i], p1Pos, p2Pos, col = p2Col, board_coords = board_coords))

    elif i == 11:
        p1Pieces.append(queen(p1Pos[i], p2Pos, p1Pos, col = p1Col, board_coords = board_coords))
        p2Pieces.append(queen(p2Pos[i], p1Pos, p2Pos, col = p2Col, board_coords = board_coords))

    elif i == 12:
        p1Pieces.append(king(p1Pos[i], p2Pos, p1Pos, col = p1Col, player = 1, moved = False, board_coords = board_coords))
        p2Pieces.append(king(p2Pos[i], p1Pos, p2Pos, col = p2Col, player = 2, moved = False, board_coords = board_coords))

#Main program
run = True
selected_location = 0
noMove = False

while run:
    #Initiate gameboard
    gameBoard = board(board_x, board_y)

    #Set legal_moves to an empty list if mouse is not clicked
    if mouseClicked == False:
        legal_moves = []

    #Get events
    for event in pygame.event.get():

        #Quit game if event type is quit
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()

        #Check if mouse button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN:

            mousePos = list(pygame.mouse.get_pos())

            if p1Turn == True:

                #Check is piece is selected already
                if mouseClicked == False:
                    #Log location
                    for i in p1Pos:
                        if i != '':
                            if mousePos[0] >= i[0] and mousePos[0] <= i[0] + tileSize and mousePos[1] >= i[1] and mousePos[1] <= i[1] + tileSize:
                                selected_location = i
                                if p1Pos.index(i) in range(8) or p1Pos.index(i) in [9, 14]:
                                    legal_moves = p1Pieces[p1Pos.index(i)].legal_moves()

                                #Store mouseclick
                                mouseClicked = True
                                break

                else:
                    #Move location if selected
                    for j in board_coords:
                        if mousePos[0] >= j[0] and mousePos[0] <= j[0] + tileSize and mousePos[1] >= j[1] and mousePos[1] <= j[1] + tileSize:
                            
                            #Reset move if location is not in legal_moves
                            if j not in legal_moves:
                                noMove = True
                                mouseClicked = False
                                break
                            i = p1Pos.index(selected_location)
                            p1Pos[i] = j
                            
                            #Reposition chess pieces
                            if i in [8, 15]:
                                p1Pieces[i] = rook(p1Pos[i], p2Pos, p1Pos, col = p1Col, board_coords = board_coords)

                            elif i in [9, 14]:
                                p1Pieces[i] = knight(p1Pos[i], p2Pos, p1Pos, col = p1Col, board_coords = board_coords)

                            elif i in [10, 13]:
                                p1Pieces[i] = bishop(p1Pos[i], p2Pos, p1Pos, col = p1Col, board_coords = board_coords)

                            elif i == 11:
                                p1Pieces[i] = queen(p1Pos[i], p2Pos, p1Pos, col = p1Col, board_coords = board_coords)

                            elif i == 12:
                                p1Pieces[i] = king(p1Pos[i], p2Pos, p1Pos, player = 1, col = p1Col, moved = True, board_coords = board_coords)

                            elif j in legal_moves:
                                p1Pieces[i] = pawn(p1Pos[i], p2Pos, p1Pos, player = 1, col = p1Col, moved = True, board_coords = board_coords)

                            #Remove opponent's piece if taken
                            if j in p2Pos and j in legal_moves:
                                p2Pos[p2Pos.index(j)] = ''

                            #Register move and reset mouseclick
                            noMove = False
                            mouseClicked = False
                            break

                    #Switch turn
                    if noMove == False:
                        p1Turn = False

            #Player 2
            else:

                #Check if piece is selected already
                if mouseClicked == False:
                    #Log location
                    for i in p2Pos:
                        if i != '':
                            if mousePos[0] >= i[0] and mousePos[0] <= i[0] + tileSize and mousePos[1] >= i[1] and mousePos[1] <= i[1] + tileSize:
                                selected_location = i
                                if p2Pos.index(i) in range(8) or p2Pos.index(i) in [9, 14]:
                                    legal_moves = p2Pieces[p2Pos.index(i)].legal_moves()
                                mouseClicked = True
                                break

                else:
                    #Move location if selected
                    for j in board_coords:
                        if mousePos[0] >= j[0] and mousePos[0] <= j[0] + tileSize and mousePos[1] >= j[1] and mousePos[1] <= j[1] + tileSize:
                            if j not in legal_moves:
                                noMove = True
                                mouseClicked = False
                                break
                            i = p2Pos.index(selected_location)

                            p2Pos[i] = j
                            if i in [8, 15]:
                                p2Pieces[i] = rook(p2Pos[i], p1Pos, p2Pos, col = p2Col, board_coords = board_coords)

                            elif i in [9, 14]:
                                p2Pieces[i] = knight(p2Pos[i], p1Pos, p2Pos, col = p2Col, board_coords = board_coords)

                            elif i in [10, 13]:
                                p2Pieces[i] = bishop(p2Pos[i], p1Pos, p2Pos, col = p2Col, board_coords = board_coords)

                            elif i == 11:
                                p2Pieces[i] = queen(p2Pos[i], p1Pos, p2Pos, col = p2Col, board_coords = board_coords)

                            elif i == 12:
                                p2Pieces[i] = king(p2Pos[i], p1Pos, p2Pos, player = 2, col = p2Col, moved = True, board_coords = board_coords)

                            else:
                                p2Pieces[i] = pawn(p2Pos[i], p1Pos, p2Pos, player = 2, col = p2Col, moved = True, board_coords = board_coords)

                            if j in p1Pos:
                                p1Pos[p1Pos.index(j)] = ''

                            noMove = False
                            mouseClicked = False
                            break

                    if noMove == False:
                        p1Turn = True

    if run == True:
        redrawGameWindow(gameWindow, gameBoard, p1Pos, p2Pos, p1Pieces, p2Pieces, mouseClicked, selected_location, legal_moves)
