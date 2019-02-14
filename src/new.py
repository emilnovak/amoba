#!/usr/bin/env python
# coding: utf-8

import pygame
import random

background_colour = (205,211,213)
playerColor = (154,72,208)
aiColor = (255,169,135)
lineColor = (0, 0, 0)

(window_width, window_height) = (800, 600)
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Amőba - Emil')
screen.fill(background_colour)
pygame.display.flip()

clock = pygame.time.Clock()

tileSize = 20

emptyChar = ''
playerChar = 'X'
aiChar = 'O'
openChar = '#'
neitherChar = 'N'
eitherChar = 'E'

gameField = [['', '', ''], ['', '', ''], ['', '', '']]
gameFieldAnchor = (window_width / 2 - tileSize, window_height / 2 - tileSize)

prevDragPosition = (0, 0)
selectedTile = (0, 0)

(offset_x, offset_y) = (0, 0)
mouse_x, mouse_y = 0, 0

firstMove = True


def extendField(field, charToFind):

    global gameFieldAnchor

    # Check upper border
    if charToFind in field[0]:
        border = []
        for element in field[0]:
            border.append('')
        field.insert(0, border)
        gameFieldAnchor = (gameFieldAnchor[0], gameFieldAnchor[1] - tileSize)

    # Check lower border
    if charToFind in field[-1]:
        border = []
        for element in field[-1]:
            border.append('')
        field.append(border)

    # Check left border
    clearLeft = True
    for row in field:
        if row[0] == charToFind:
            clearLeft = False
            break
    if not clearLeft:
        for i, _ in enumerate(field):
            field[i].insert(0, '')
        gameFieldAnchor = (gameFieldAnchor[0] - tileSize, gameFieldAnchor[1])

    # Check right border
    clearRight = True
    for row in field:
        if row[-1] == charToFind:
            clearRight = False
            break
    if not clearRight:
        for i, _ in enumerate(field):
            field[i].append('')

def whichTile(pos, inclusive = False):
    for j, row in enumerate(gameField):
        for i, tile in enumerate(row):
                if tile != '' or inclusive:
                    if pos[0] >= gameFieldAnchor[0] + offset_x + i * tileSize \
                      and pos[0] <= gameFieldAnchor[0] + offset_x + (i + 1) * tileSize \
                      and pos[1] >= gameFieldAnchor[1] + offset_y + j * tileSize \
                      and pos[1] <= gameFieldAnchor[1] + offset_y + (j + 1) * tileSize:
                        return (i, j)
    return False

def isMousePositionValid(pos):
    if whichTile(pos) is not False:
        return False
    if whichTile((pos[0], pos[1] - tileSize)) is not False \
      or whichTile((pos[0], pos[1] + tileSize )) is not False \
      or whichTile((pos[0] - tileSize, pos[1] - tileSize)) is not False \
      or whichTile((pos[0] - tileSize, pos[1] + tileSize )) is not False \
      or whichTile((pos[0] + tileSize, pos[1] - tileSize)) is not False \
      or whichTile((pos[0] + tileSize, pos[1] + tileSize )) is not False \
      or whichTile((pos[0] - tileSize, pos[1])) is not False \
      or whichTile((pos[0] + tileSize, pos[1])) is not False:

        return True

    return False

# Mirror pattern along X and Y axes
def mixPattern(pattern):

    patterns = []
    patterns.append(pattern)

    # Mirror about X axis
    tmpPattern = []
    for j, row in enumerate(pattern):
        tmpRow = []
        for i, tile in enumerate(row):
            tmpRow.append(pattern[len(pattern)  - 1 - j][i])
        tmpPattern.append(tmpRow)
    if tmpPattern not in patterns:
        patterns.append(tmpPattern)

    # Mirror about Y axis
    tmpPattern = []
    for j, row in enumerate(pattern):
        tmpRow = []
        for i, tile in enumerate(row):
            tmpRow.append(pattern[j][len(pattern[0]) - 1 - i])
        tmpPattern.append(tmpRow)
    if tmpPattern not in patterns:
        patterns.append(tmpPattern)

    #Mirror about bot X and Y axes
    tmpPattern = []
    for j, row in enumerate(pattern):
        tmpRow = []
        for i, tile in enumerate(row):
            tmpRow.append(pattern[len(pattern)  - 1 - j][len(pattern[0]) - 1 - i])
        tmpPattern.append(tmpRow)
    if tmpPattern not in patterns:
        patterns.append(tmpPattern)

    return patterns

pat1 = [['A', 'B'], ['C', 'D'], ['B', 'F']]
print(pat1)
print(mixPattern(pat1))

def findPattern(pattern, field, offset):

    playerNum, aiNum, openNum, neitherNum = 0, 0, 0, 0

    if len(pattern[0]) + offset[0] > len(field[0]):
        # print('out of bounds x')
        return (playerNum, aiNum, openNum, neitherNum)
    if len(pattern) + offset[1] > len(field):
        # print('out of bounds y')
        return (playerNum, aiNum, openNum, neitherNum)

    for j, row in enumerate(pattern):
        for i, tile in enumerate(row):
            inspectedTile = field[j + offset[1]][i + offset[0]]
            if tile == openChar and inspectedTile == emptyChar:
                openNum += 1
            elif (tile == playerChar or tile == eitherChar) and inspectedTile == playerChar:
                playerNum += 1
            elif (tile == aiChar or tile == eitherChar) and inspectedTile == aiChar:
                aiNum += 1
            if tile == neitherChar and inspectedTile == emptyChar:
                neitherNum += 1

    return (playerNum, aiNum, openNum, neitherNum)

patternForPlacig =   [
                    [['E'], ['N']],
                    [['E', 'N']],
                    [['E', ''], ['', 'N']]
                    ]


def aiTurn():
    global gameField

    validMoves = []

    for j, row in enumerate(gameField):
        for i, tile in enumerate(row):

            if tile != emptyChar:
                continue

            try:
                if gameField[j][i + 1] != emptyChar:
                    validMoves.append((i, j))
            except IndexError:
                pass
            try:
                if gameField[j][i - 1] != emptyChar:
                    validMoves.append((i, j))
            except IndexError:
                pass
            try:
                if gameField[j + 1][i + 1] != emptyChar:
                    validMoves.append((i, j))
            except IndexError:
                pass
            try:
                if gameField[j + 1][i - 1] != emptyChar:
                    validMoves.append((i, j))
            except IndexError:
                pass
            try:
                if gameField[j - 1][i + 1] != emptyChar:
                    validMoves.append((i, j))
            except IndexError:
                pass
            try:
                if gameField[j - 1][i - 1] != emptyChar:
                    validMoves.append((i, j))
            except IndexError:
                pass
            try:
                if gameField[j + 1][i] != emptyChar:
                    validMoves.append((i, j))
            except IndexError:
                pass
            try:
                if gameField[j - 1][i] != emptyChar:
                    validMoves.append((i, j))
            except IndexError:
                pass

    print(validMoves)


    if len(validMoves) > 0:
        print(validMoves)
        x, y = random.choice(validMoves)
        gameField[y][x] = aiChar
    else:
        print("Error with validMoves being 0!")

    extendField(gameField, aiChar)

# Debug code
extendField(gameField, playerChar)

# Game Loop

running = True
while running:

    # EVENTS

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
            if event.key == pygame.K_SPACE:
                gameFieldAnchor = (window_width / 2 - len(gameField[0]) // 2 * tileSize, window_height / 2 - len(gameField) // 2 * tileSize)
                offset_x, offset_y = 0, 0
            if event.key == pygame.K_q:
                print("valid tile:", whichTile((mouse_x, mouse_y), True))

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if firstMove:
                    firstMove = False
                    gameFieldAnchor = (event.pos[0] // tileSize * tileSize - tileSize, event.pos[1] // tileSize * tileSize - tileSize)
                    # print('event.pos:', event.pos)
                    # print('gameFieldAnchor', gameFieldAnchor)
                    gameField[1][1] = playerChar
                    aiTurn()
                    extendField(gameField, aiChar)

                if isMousePositionValid(event.pos):
                    print("valid tile:", whichTile(event.pos, True))
                    (x, y) = whichTile(event.pos, True)
                    gameField[y][x] = playerChar
                    extendField(gameField, playerChar)
                    aiTurn()
                    extendField(gameField, aiChar)



            if event.button == 3:
                prevDragPosition = event.pos


        if event.type == pygame.MOUSEMOTION:
            # print(u'pressed buttons {}, position {{}{}} and relative movement {}'.format(event.buttons, event.pos, event.rel))

            mouse_x, mouse_y = event.pos

            if event.buttons[2] == 1:
                (tmp_x, tmp_y) = event.pos

                offset_x += tmp_x - prevDragPosition[0]
                offset_y += tmp_y - prevDragPosition[1]

                prevDragPosition = event.pos


        if event.type == pygame.MOUSEBUTTONUP:
            1


    # RENDER
    screen.fill(background_colour)

    # Render grid
    for i in range(0, window_height // tileSize):
        pygame.draw.line(screen, lineColor, (0, i * tileSize + offset_y % tileSize), (window_width - 1, i * tileSize + offset_y % tileSize))
    for i in range(0, window_width // tileSize):
        pygame.draw.line(screen, lineColor, (i * tileSize + offset_x % tileSize, 0), (i * tileSize + offset_x % tileSize, window_height - 1))

    # Test code
    # pygame.draw.rect(screen, (0, 255, 0), [window_width / 2 + offset_x, window_height / 2 + offset_y, tileSize, tileSize])

    # Render gameField
    for j, row in enumerate(gameField):
        for i, tile in enumerate(row):
            if tile == emptyChar:
                continue

            tileColor = (0, 0, 0)
            if tile == playerChar:
                tileColor = playerColor
            if tile == aiChar:
                tileColor == aiColor
            pygame.draw.rect(screen, tileColor, [gameFieldAnchor[0] + offset_x + i * tileSize, gameFieldAnchor[1] + offset_y + j * tileSize, tileSize, tileSize])


    pygame.draw.circle(screen, (255, 0, 0), (int(gameFieldAnchor[0] + offset_x), int(gameFieldAnchor[1]) + offset_y), 5)

    clock.tick(60)
    pygame.display.flip()



pygame.quit()
