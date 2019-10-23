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

    def __init__(self, coord, opp_coords, own_coords, col, player, moved):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col
        self.player = player
        self.moved = moved

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
    def __init__(self, coord, opp_coords, own_coords, col):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col

    def legal_moves(self):
        legals = []

        #Up
        for i in range(8):
            try:
                if [self.x, self.y - tileSize * (i+1)] in board_coords:
                    if [self.x, self.y - tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x, self.y - tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x, self.y - tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x, self.y - tileSize * (i+1)])
            except IndexError:
                pass

        #Down
        for i in range(8):
            try:
                if [self.x, self.y + tileSize * (i+1)] in board_coords:
                    if [self.x, self.y + tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x, self.y + tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x, self.y + tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x, self.y + tileSize * (i+1)])
            except IndexError:
                pass

        #Left
        for i in range(8):
            try:
                if [self.x - tileSize * (i+1), self.y] in board_coords:
                    if [self.x - tileSize * (i+1), self.y] in self.own_coords:
                        break
                    elif [self.x - tileSize * (i+1), self.y] in self.opp_coords:
                        legals.append([self.x - tileSize * (i+1), self.y])
                        break
                    else:
                        legals.append([self.x - tileSize * (i+1), self.y])
            except IndexError:
                pass

        #Right
        for i in range(8):
            try:
                if [self.x + tileSize * (i+1), self.y] in board_coords:
                    if [self.x + tileSize * (i+1), self.y] in self.own_coords:
                        break
                    elif [self.x + tileSize * (i+1), self.y] in self.opp_coords:
                        legals.append([self.x + tileSize * (i+1), self.y])
                        break
                    else:
                        legals.append([self.x + tileSize * (i+1), self.y])
            except IndexError:
                pass

        return legals

    def draw(self, win):
            if self.col == 'white':
                win.blit(rook_white, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])
            else:
                win.blit(rook_black, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])

class knight(object):
    def __init__(self, coord, opp_coords, own_coords, col):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col

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
    def __init__(self, coord, opp_coords, own_coords, col):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col

    def legal_moves(self):
        legals = []

        #Upleft
        for i in range(8):
            try:
                if [self.x - tileSize * (i+1), self.y - tileSize * (i+1)] in board_coords:
                    if [self.x - tileSize * (i+1), self.y - tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x - tileSize * (i+1), self.y - tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x - tileSize * (i+1), self.y - tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x - tileSize * (i+1), self.y - tileSize * (i+1)])
            except IndexError:
                pass

        #Upright
        for i in range(8):
            try:
                if [self.x + tileSize * (i+1), self.y - tileSize * (i+1)] in board_coords:
                    if [self.x + tileSize * (i+1), self.y - tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x + tileSize * (i+1), self.y - tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x + tileSize * (i+1), self.y - tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x + tileSize * (i+1), self.y - tileSize * (i+1)])
            except IndexError:
                pass

        #Downleft
        for i in range(8):
            try:
                if [self.x - tileSize * (i+1), self.y + tileSize * (i+1)] in board_coords:
                    if [self.x - tileSize * (i+1), self.y + tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x - tileSize * (i+1), self.y + tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x - tileSize * (i+1), self.y + tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x - tileSize * (i+1), self.y + tileSize * (i+1)])
            except IndexError:
                pass

        #Downright
        for i in range(8):
            try:
                if [self.x + tileSize * (i+1), self.y + tileSize * (i+1)] in board_coords:
                    if [self.x + tileSize * (i+1), self.y + tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x + tileSize * (i+1), self.y + tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x + tileSize * (i+1), self.y + tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x + tileSize * (i+1), self.y + tileSize * (i+1)])
            except IndexError:
                pass

        return legals

    def draw(self, win):
            if self.col == 'white':
                win.blit(bishop_white, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])
            else:
                win.blit(bishop_black, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])

class queen(object):
    def __init__(self, coord, opp_coords, own_coords, col):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col

    def legal_moves(self):
        legals = []

        #Up
        for i in range(8):
            try:
                if [self.x, self.y - tileSize * (i+1)] in board_coords:
                    if [self.x, self.y - tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x, self.y - tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x, self.y - tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x, self.y - tileSize * (i+1)])
            except IndexError:
                pass

        #Down
        for i in range(8):
            try:
                if [self.x, self.y + tileSize * (i+1)] in board_coords:
                    if [self.x, self.y + tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x, self.y + tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x, self.y + tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x, self.y + tileSize * (i+1)])
            except IndexError:
                pass

        #Left
        for i in range(8):
            try:
                if [self.x - tileSize * (i+1), self.y] in board_coords:
                    if [self.x - tileSize * (i+1), self.y] in self.own_coords:
                        break
                    elif [self.x - tileSize * (i+1), self.y] in self.opp_coords:
                        legals.append([self.x - tileSize * (i+1), self.y])
                        break
                    else:
                        legals.append([self.x - tileSize * (i+1), self.y])
            except IndexError:
                pass

        #Right
        for i in range(8):
            try:
                if [self.x + tileSize * (i+1), self.y] in board_coords:
                    if [self.x + tileSize * (i+1), self.y] in self.own_coords:
                        break
                    elif [self.x + tileSize * (i+1), self.y] in self.opp_coords:
                        legals.append([self.x + tileSize * (i+1), self.y])
                        break
                    else:
                        legals.append([self.x + tileSize * (i+1), self.y])
            except IndexError:
                pass

        #Upleft
        for i in range(8):
            try:
                if [self.x - tileSize * (i+1), self.y - tileSize * (i+1)] in board_coords:
                    if [self.x - tileSize * (i+1), self.y - tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x - tileSize * (i+1), self.y - tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x - tileSize * (i+1), self.y - tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x - tileSize * (i+1), self.y - tileSize * (i+1)])
            except IndexError:
                pass

        #Upright
        for i in range(8):
            try:
                if [self.x + tileSize * (i+1), self.y - tileSize * (i+1)] in board_coords:
                    if [self.x + tileSize * (i+1), self.y - tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x + tileSize * (i+1), self.y - tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x + tileSize * (i+1), self.y - tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x + tileSize * (i+1), self.y - tileSize * (i+1)])
            except IndexError:
                pass

        #Downleft
        for i in range(8):
            try:
                if [self.x - tileSize * (i+1), self.y + tileSize * (i+1)] in board_coords:
                    if [self.x - tileSize * (i+1), self.y + tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x - tileSize * (i+1), self.y + tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x - tileSize * (i+1), self.y + tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x - tileSize * (i+1), self.y + tileSize * (i+1)])
            except IndexError:
                pass

        #Downright
        for i in range(8):
            try:
                if [self.x + tileSize * (i+1), self.y + tileSize * (i+1)] in board_coords:
                    if [self.x + tileSize * (i+1), self.y + tileSize * (i+1)] in self.own_coords:
                        break
                    elif [self.x + tileSize * (i+1), self.y + tileSize * (i+1)] in self.opp_coords:
                        legals.append([self.x + tileSize * (i+1), self.y + tileSize * (i+1)])
                        break
                    else:
                        legals.append([self.x + tileSize * (i+1), self.y + tileSize * (i+1)])
            except IndexError:
                pass

        return legals

    def draw(self, win):
            if self.col == 'white':
                win.blit(queen_white, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])
            else:
                win.blit(queen_black, [self.x + ((tileSize - imageSize)//2) - imageError, self.y + ((tileSize - imageSize)//2)])

class king(object):
    def __init__(self, coord, opp_coords, own_coords, col, player, moved):
        self.x = coord[0]
        self.y = coord[1]
        self.opp_coords = opp_coords
        self.own_coords = own_coords
        self.col = col
        self.player = player
        self.moved = moved

    def legal_moves(self):
        legals = []
        #Up
        try:
            if [self.x, self.y - tileSize] in board_coords:
                if [self.x, self.y - tileSize] not in self.own_coords:
                    legals.append([self.x, self.y - tileSize])
        except IndexError:
            pass

        #Down
        try:
            if [self.x, self.y + tileSize] in board_coords:
                if [self.x, self.y + tileSize] not in self.own_coords:
                    legals.append([self.x, self.y + tileSize])
        except IndexError:
            pass

        #Left
        try:
            if [self.x - tileSize, self.y] in board_coords:
                if [self.x - tileSize, self.y] not in self.own_coords:
                    legals.append([self.x - tileSize, self.y])
        except IndexError:
            pass

        #Right
        try:
            if [self.x + tileSize, self.y] in board_coords:
                if [self.x + tileSize, self.y] not in self.own_coords:
                    legals.append([self.x + tileSize, self.y])
        except IndexError:
            pass

        #Upleft
        try:
            if [self.x - tileSize, self.y - tileSize] in board_coords:
                if [self.x - tileSize, self.y - tileSize] not in self.own_coords:
                    legals.append([self.x - tileSize, self.y - tileSize])
        except IndexError:
            pass

        #Upright
        try:
            if [self.x + tileSize, self.y - tileSize] in board_coords:
                if [self.x + tileSize, self.y - tileSize] not in self.own_coords:
                    legals.append([self.x + tileSize, self.y - tileSize])
        except IndexError:
            pass

        #Downleft
        try:
            if [self.x - tileSize, self.y + tileSize] in board_coords:
                if [self.x - tileSize, self.y + tileSize] not in self.own_coords:
                    legals.append([self.x - tileSize, self.y + tileSize])
        except IndexError:
            pass

        #Downright
        try:
            if [self.x + tileSize, self.y + tileSize] in board_coords:
                if [self.x + tileSize, self.y + tileSize] not in self.own_coords:
                    legals.append([self.x + tileSize, self.y + tileSize])
        except IndexError:
            pass

        return legals

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
    p1Pieces.append(pawn(p1Pos[i], p2Pos, p1Pos, player = 1, col = p1Col, moved = False))
    p2Pieces.append(pawn(p2Pos[i], p1Pos, p2Pos, player = 2, col = p2Col, moved = False))

#Chess pieces
for i in range (8, 16):
    if i in [8, 15]:
        p1Pieces.append(rook(p1Pos[i], p2Pos, p1Pos, col = p1Col))
        p2Pieces.append(rook(p2Pos[i], p1Pos, p2Pos, col = p2Col))

    elif i in [9, 14]:
        p1Pieces.append(knight(p1Pos[i], p2Pos, p1Pos, col = p1Col))
        p2Pieces.append(knight(p2Pos[i], p1Pos, p2Pos, col = p2Col))

    elif i in [10, 13]:
        p1Pieces.append(bishop(p1Pos[i], p2Pos, p1Pos, col = p1Col))
        p2Pieces.append(bishop(p2Pos[i], p1Pos, p2Pos, col = p2Col))

    elif i == 11:
        p1Pieces.append(queen(p1Pos[i], p2Pos, p1Pos, col = p1Col))
        p2Pieces.append(queen(p2Pos[i], p1Pos, p2Pos, col = p2Col))

    elif i == 12:
        p1Pieces.append(king(p1Pos[i], p2Pos, p1Pos, col = p1Col, player = 1, moved = False))
        p2Pieces.append(king(p2Pos[i], p1Pos, p2Pos, col = p2Col, player = 2, moved = False))

#Main program
run = True
selected_location = 0
noMove = False
p1PieceTypes = ['p','p','p','p','p','p','p','p','r','n','b','q', 'k', 'b', 'n', 'r']
p2PieceTypes = ['p','p','p','p','p','p','p','p','r','n','b','q', 'k', 'b', 'n', 'r']
p1PawnMoved = [False]*8
p2PawnMoved = [False]*8
p1KingMoved = False
p2KingMoved = False

while run:
    #Initiate gameboard
    gameBoard = board(board_x, board_y)

    #Reset dominant positions
    p1Dom = []
    p2Dom = []

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


            #Player 1
            if p1Turn == True:
                #Store current state

                p1PosTemp = p1Pos.copy()
                p1PiecesTemp = p1Pieces.copy()
                # #Create array to store otherwise legal moves to remove
                legals_remove = []
                for k in range(len(p1Pos)):
                    legals_active = p1Pieces[k].legal_moves()

                    for h in legals_active:
                        #Player 2 piece positions
                        p1Pos[k] = h
                        if p1PieceTypes[k] == 'r':
                            p1Pieces[k] = rook(p1Pos[k], p2Pos, p1Pos, col = p1Col)

                        elif p1PieceTypes[k] == 'n':
                            p1Pieces[k] = knight(p1Pos[k], p2Pos, p1Pos, col = p1Col)

                        elif p1PieceTypes[k] == 'b':
                            p1Pieces[k] = bishop(p1Pos[k], p2Pos, p1Pos, col = p1Col)

                        elif p1PieceTypes[k] == 'q':
                            p1Pieces[k] = queen(p1Pos[k], p2Pos, p1Pos, col = p1Col)

                        elif p1PieceTypes[k] == 'k':
                            p1Pieces[k] = king(p1Pos[k], p2Pos, p1Pos, player = 1, col = p1Col, moved = True)

                        else:
                            p1Pieces[k] = pawn(p1Pos[k], p2Pos, p1Pos, player = 1, col = p1Col, moved = True)

                        for i in range(len(p2Pos)):
                            #Update p2Pieces for legal_moves function
                            if p2PieceTypes[i] == 'r':
                                p2Pieces[i] = rook(p2Pos[i], p1Pos, p2Pos, col = p2Col)
                            elif p2PieceTypes[i] == 'n':
                                p2Pieces[i] = knight(p2Pos[i], p1Pos, p2Pos, col = p2Col)
                            elif p2PieceTypes[i] == 'b':
                                p2Pieces[i] = bishop(p2Pos[i], p1Pos, p2Pos, col = p2Col)
                            elif p2PieceTypes[i] == 'q':
                                p2Pieces[i] = queen(p2Pos[i], p1Pos, p2Pos, col = p2Col)
                            elif p2PieceTypes[i] == 'k':
                                p2Pieces[i] = king(p2Pos[i], p1Pos, p2Pos, player = 2, col = p2Col, moved = p2KingMoved)
                            else:
                                p2Pieces[i] = pawn(p2Pos[i], p1Pos, p2Pos, player = 2, col = p2Col, moved = p2PawnMoved[i])

                            opp_legals = p2Pieces[i].legal_moves()
                            for j in range(len(opp_legals)):
                                if p1Pos[12] == opp_legals[j]:
                                    legals_remove.append([k, opp_legals[j]])

                            #Reset P2 legal moves
                            for x in range(len(p2Pos)):
                                if p2PieceTypes[x] == 'r':
                                    p2Pieces[x] = rook(p2Pos[x], p1Pos, p2Pos, col = p2Col)
                                elif p2PieceTypes[x] == 'n':
                                    p2Pieces[x] = knight(p2Pos[x], p1Pos, p2Pos, col = p2Col)
                                elif p2PieceTypes[x] == 'b':
                                    p2Pieces[x] = bishop(p2Pos[x], p1Pos, p2Pos, col = p2Col)
                                elif p2PieceTypes[x] == 'q':
                                    p2Pieces[x] = queen(p2Pos[x], p1Pos, p2Pos, col = p2Col)
                                elif p2PieceTypes[x] == 'k':
                                    p2Pieces[x] = king(p2Pos[x], p1Pos, p2Pos, player = 2, col = p2Col, moved = p2KingMoved)
                                else:
                                    p2Pieces[x] = pawn(p2Pos[x], p1Pos, p2Pos, player = 2, col = p2Col, moved = p2PawnMoved[x])

                        p1Pos = p1PosTemp.copy()
                        p1Pieces = p1PiecesTemp.copy()

                        #Reset P1 legal moves
                        for x in range(len(p1Pos)):
                            if p1PieceTypes[x] == 'r':
                                p1Pieces[x] = rook(p1Pos[x], p2Pos, p1Pos, col = p1Col)
                            elif p1PieceTypes[x] == 'n':
                                p1Pieces[x] = knight(p1Pos[x], p2Pos, p1Pos, col = p1Col)
                            elif p1PieceTypes[x] == 'b':
                                p1Pieces[x] = bishop(p1Pos[x], p2Pos, p1Pos, col = p1Col)
                            elif p1PieceTypes[x] == 'q':
                                p1Pieces[x] = queen(p1Pos[x], p2Pos, p1Pos, col = p1Col)
                            elif p1PieceTypes[x] == 'k':
                                p1Pieces[x] = king(p1Pos[x], p2Pos, p1Pos, player = 1, col = p1Col, moved = p1KingMoved)
                            else:
                                p1Pieces[x] = pawn(p1Pos[x], p2Pos, p1Pos, player = 1, col = p1Col, moved = p1PawnMoved[x])



                print(legals_remove)


                #Check is piece is selected already
                if mouseClicked == False:
                    #Log location
                    for i in p1Pos:
                        if i != '':
                            if mousePos[0] >= i[0] and mousePos[0] <= i[0] + tileSize and mousePos[1] >= i[1] and mousePos[1] <= i[1] + tileSize:
                                selected_location = i
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
                            if p1PieceTypes[i] == 'r':
                                p1Pieces[i] = rook(p1Pos[i], p2Pos, p1Pos, col = p1Col)

                            elif p1PieceTypes[i] == 'n':
                                p1Pieces[i] = knight(p1Pos[i], p2Pos, p1Pos, col = p1Col)

                            elif p1PieceTypes[i] == 'b':
                                p1Pieces[i] = bishop(p1Pos[i], p2Pos, p1Pos, col = p1Col)

                            elif p1PieceTypes[i] == 'q':
                                p1Pieces[i] = queen(p1Pos[i], p2Pos, p1Pos, col = p1Col)

                            elif p1PieceTypes[i] == 'k':
                                p1KingMoved = True
                                p1Pieces[i] = king(p1Pos[i], p2Pos, p1Pos, player = 1, col = p1Col, moved = p1KingMoved)

                            elif p1PieceTypes[i] == 'p':
                                p1PawnMoved[i] = True
                                p1Pieces[i] = pawn(p1Pos[i], p2Pos, p1Pos, player = 1, col = p1Col, moved = p1PawnMoved[i])

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

                #Store current state
                p2PosTemp = p2Pos.copy()
                p2PiecesTemp = p2Pieces.copy()
                # #Create array to store otherwise legal moves to remove
                legals_remove = []
                for k in range(len(p2Pos)):
                    legals_active = p2Pieces[k].legal_moves()

                    for h in legals_active:
                        #Player 2 piece positions
                        p2Pos[k] = h
                        if p2PieceTypes[k] == 'r':
                            p2Pieces[k] = rook(p2Pos[k], p1Pos, p2Pos, col = p2Col)

                        elif p2PieceTypes[k] == 'n':
                            p2Pieces[k] = knight(p2Pos[k], p1Pos, p2Pos, col = p2Col)

                        elif p2PieceTypes[k] == 'b':
                            p2Pieces[k] = bishop(p2Pos[k], p1Pos, p2Pos, col = p2Col)

                        elif p2PieceTypes[k] == 'q':
                            p2Pieces[k] = queen(p2Pos[k], p1Pos, p2Pos, col = p2Col)

                        elif p2PieceTypes[k] == 'k':
                            p2Pieces[k] = king(p2Pos[k], p1Pos, p2Pos, player = 2, col = p2Col, moved = True)

                        else:
                            p2Pieces[k] = pawn(p2Pos[k], p1Pos, p2Pos, player = 2, col = p2Col, moved = True)


                        for i in range(len(p1Pos)):

                            #Update p1Pieces for legal_moves function
                            if p1PieceTypes[i] == 'r':
                                p1Pieces[i] = rook(p1Pos[i], p2Pos, p1Pos, col = p1Col)
                            elif p1PieceTypes[i] == 'n':
                                p1Pieces[i] = knight(p1Pos[i], p2Pos, p1Pos, col = p1Col)
                            elif p1PieceTypes[i] == 'b':
                                p1Pieces[i] = bishop(p1Pos[i], p2Pos, p1Pos, col = p1Col)
                            elif p1PieceTypes[i] == 'q':
                                p1Pieces[i] = queen(p1Pos[i], p2Pos, p1Pos, col = p1Col)
                            elif p1PieceTypes[i] == 'k':
                                p1Pieces[i] = king(p1Pos[i], p2Pos, p1Pos, player = 1, col = p1Col, moved = p1KingMoved)
                            else:
                                p1Pieces[i] = pawn(p1Pos[i], p2Pos, p1Pos, player = 1, col = p1Col, moved = p1PawnMoved[i])

                            opp_legals = p1Pieces[i].legal_moves()
                            for j in range(len(opp_legals)):
                                if p2Pos[12] == opp_legals[j]:
                                    legals_remove.append([k, h])

                            for x in range(len(p1Pos)):
                                #Reset P1 legal moves
                                if p1PieceTypes[x] == 'r':
                                    p1Pieces[x] = rook(p1Pos[x], p2Pos, p1Pos, col = p1Col)
                                elif p1PieceTypes[x] == 'n':
                                    p1Pieces[x] = knight(p1Pos[x], p2Pos, p1Pos, col = p1Col)
                                elif p1PieceTypes[x] == 'b':
                                    p1Pieces[x] = bishop(p1Pos[x], p2Pos, p1Pos, col = p1Col)
                                elif p1PieceTypes[x] == 'q':
                                    p1Pieces[x] = queen(p1Pos[x], p2Pos, p1Pos, col = p1Col)
                                elif p1PieceTypes[x] == 'k':
                                    p1Pieces[x] = king(p1Pos[x], p2Pos, p1Pos, player = 1, col = p1Col, moved = p1KingMoved)
                                else:
                                    p1Pieces[x] = pawn(p1Pos[x], p2Pos, p1Pos, player = 1, col = p1Col, moved = p1PawnMoved[x])


                        p2Pos = p2PosTemp.copy()
                        p2Pieces = p2PiecesTemp.copy()

                        #Reset P2 legal moves
                        for x in range(len(p2Pos)):
                            if p2PieceTypes[x] == 'r':
                                p2Pieces[x] = rook(p2Pos[x], p1Pos, p2Pos, col = p2Col)
                            elif p2PieceTypes[x] == 'n':
                                p2Pieces[x] = knight(p2Pos[x], p1Pos, p2Pos, col = p2Col)
                            elif p2PieceTypes[x] == 'b':
                                p2Pieces[x] = bishop(p2Pos[x], p1Pos, p2Pos, col = p2Col)
                            elif p2PieceTypes[x] == 'q':
                                p2Pieces[x] = queen(p2Pos[x], p1Pos, p2Pos, col = p2Col)
                            elif p2PieceTypes[x] == 'k':
                                p2Pieces[x] = king(p2Pos[x], p1Pos, p2Pos, player = 2, col = p2Col, moved = p2KingMoved)
                            else:
                                p2Pieces[x] = pawn(p2Pos[x], p1Pos, p2Pos, player = 2, col = p2Col, moved = p2PawnMoved[x])

                print(legals_remove)

                #Check if piece is selected already
                if mouseClicked == False:
                    #Log location
                    for i in p2Pos:
                        if i != '':
                            if mousePos[0] >= i[0] and mousePos[0] <= i[0] + tileSize and mousePos[1] >= i[1] and mousePos[1] <= i[1] + tileSize:
                                selected_location = i
                                legal_moves = p2Pieces[p2Pos.index(i)].legal_moves()

                                #Store mouseclick
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
                            if p2PieceTypes[i] == 'r':
                                p2Pieces[i] = rook(p2Pos[i], p1Pos, p2Pos, col = p2Col)

                            elif p2PieceTypes[i] == 'n':
                                p2Pieces[i] = knight(p2Pos[i], p1Pos, p2Pos, col = p2Col)

                            elif p2PieceTypes[i] == 'b':
                                p2Pieces[i] = bishop(p2Pos[i], p1Pos, p2Pos, col = p2Col)

                            elif p2PieceTypes[i] == 'q':
                                p2Pieces[i] = queen(p2Pos[i], p1Pos, p2Pos, col = p2Col)

                            elif p2PieceTypes[i] == 'k':
                                p2KingMoved = True
                                p2Pieces[i] = king(p2Pos[i], p1Pos, p2Pos, player = 2, col = p2Col, moved = p2KingMoved)

                            else:
                                p2PawnMoved[i] = True
                                p2Pieces[i] = pawn(p2Pos[i], p1Pos, p2Pos, player = 2, col = p2Col, moved = p2PawnMoved[i])

                            if j in p1Pos:
                                p1Pos[p1Pos.index(j)] = ''

                            noMove = False
                            mouseClicked = False
                            break

                    if noMove == False:
                        p1Turn = True

    if run == True:
        redrawGameWindow(gameWindow, gameBoard, p1Pos, p2Pos, p1Pieces, p2Pieces, mouseClicked, selected_location, legal_moves)
