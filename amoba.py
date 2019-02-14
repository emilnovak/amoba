#!/usr/bin/env python3
# coding: utf-8

import pygame
import random, math, time

background_colour = (255,248,220)
playerColor = (32,178,170)
aiColor = (240,128,128)
lineColor = (169,169,169)
textColor = (123,104,238)

(window_width, window_height) = (800, 600)
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Amőba - Emil')
screen.fill(background_colour)
pygame.display.flip()

pygame.font.init()
gameFont = pygame.font.SysFont(None, 40)

clock = pygame.time.Clock()

emptyChar = ''
playerChar = 'X'
aiChar = 'O'
openChar = '#'
moveChar = '$'
neitherChar = 'N'
eitherChar = 'E'

playerWinningPatterns = [
                        [['X', 'X', 'X', 'X', 'X']],
                        [['X', '', '', '', ''], ['', 'X', '', '', ''], ['', '', 'X', '', ''], ['', '', '', 'X', ''], ['', '', '', '', 'X']],
                        [['X'], ['X'], ['X'], ['X'], ['X']]
                        ]

aiWinningPatterns = [
                    [['O', 'O', 'O', 'O', 'O']],
                    [['O', '', '', '', ''], ['', 'O', '', '', ''], ['', '', 'O', '', ''], ['', '', '', 'O', ''], ['', '', '', '', 'O']],
                    [['O'], ['O'], ['O'], ['O'], ['O']]
                    ]

obligatoryPatterns =    [
                        [[100], [['$', 'X', 'X', 'X', 'X']]],
                        [[100], [['$'], ['X'], ['X'], ['X'], ['X']]],
                        [[100], [['$', '', '', '', ''], ['', 'X', '', '', ''], ['', '', 'X', '', ''], ['', '', '', 'X', ''], ['', '', '', '', 'X']]],

                        [[110], [['$', 'O', 'O', 'O', 'O']]],
                        [[110], [['$'], ['O'], ['O'], ['O'], ['O']]],
                        [[110], [['$', '', '', '', ''], ['', 'O', '', '', ''], ['', '', 'O', '', ''], ['', '', '', 'O', ''], ['', '', '', '', 'O']]],

                        [[90], [['#', 'X', '$', 'X', 'X']]],
                        [[90], [['#'], ['X'], ['$'], ['X'], ['X']]],
                        [[90], [['#', '', '', '', ''], ['', 'X', '', '', ''], ['', '', '$', '', ''], ['', '', '', 'X', ''], ['', '', '', '', 'X']]],
                        [[90], [['#', 'X', 'X', '$', 'X']]],
                        [[90], [['#'], ['X'], ['X'], ['$'], ['X']]],
                        [[90], [['#', '', '', '', ''], ['', 'X', '', '', ''], ['', '', 'X', '', ''], ['', '', '', '$', ''], ['', '', '', '', 'X']]],

                        [[70], [['#', 'O', '$', 'O', 'O']]],
                        [[70], [['#'], ['O'], ['$'], ['O'], ['O']]],
                        [[70], [['#', '', '', '', ''], ['', 'O', '', '', ''], ['', '', '$', '', ''], ['', '', '', 'O', ''], ['', '', '', '', 'O']]],
                        [[70], [['#', 'O', 'O', '$', 'O']]],
                        [[70], [['#'], ['O'], ['O'], ['$'], ['O']]],
                        [[70], [['#', '', '', '', ''], ['', 'O', '', '', ''], ['', '', 'O', '', ''], ['', '', '', '$', ''], ['', '', '', '', 'O']]],

                        [[80], [['$', 'X', 'X', 'X', '$']]],
                        [[80], [['#'], ['X'], ['X'], ['X'], ['$']]],
                        [[80], [['$', '', '', '', ''], ['', 'X', '', '', ''], ['', '', 'X', '', ''], ['', '', '', 'X', ''], ['', '', '', '', '$']]],

                        [[70], [['$', 'O', 'O', 'O', '$']]],
                        [[70], [['$'], ['O'], ['O'], ['O'], ['$']]],
                        [[70], [['$', '', '', '', ''], ['', 'O', '', '', ''], ['', '', 'O', '', ''], ['', '', '', 'O', ''], ['', '', '', '', '$']]]

                        ]



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

def checkPattern(patternSet):
    moves = []
    # Medium ai
    for j, row in enumerate(gameField):
        for i, tile in enumerate(row):

            for basePattern in patternSet:
                patterns = mixPattern(basePattern[1])
                for pattern in patterns:

                    if len(pattern[0]) + i > len(gameField[0]) or len(pattern) + j > len(gameField):
                        continue

                    matching = True
                    anchors = []

                    # print('check for pattern: ', pattern)

                    for v, v_row in enumerate(pattern):
                        for u, u_tile in enumerate(v_row):

                            tile = gameField[j + v][i + u]
                            tilePos = (i + u, j + v)

                            if u_tile == emptyChar:
                                continue

                            elif (u_tile == playerChar and tile == playerChar) or (u_tile == aiChar and tile == aiChar):
                                # print("match found at", (tilePos[0], tilePos[1]))
                                pass

                            elif u_tile == moveChar and tile == emptyChar:
                                # print("match found at", (tilePos[0], tilePos[1]))
                                anchors.append([basePattern[0], [tilePos[0], tilePos[1]]])
                            elif u_tile == openChar and tile == emptyChar:
                                    # print("match found at", (tilePos[0], tilePos[1]))
                                    pass
                            else:
                                # print("mismatch found at", (tilePos[0], tilePos[1]))
                                matching = False

                    if matching and len(anchors) > 0:
                        moves.append(anchors)

    if moves:
        return moves[0]
    return moves

def aiTurn():
    render()
    time.sleep(0.6)

    global gameField
    global winningTiles

    extendField(gameField, playerChar)

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

    obligatoryMoves = checkPattern(obligatoryPatterns)

    if obligatoryMoves:
        print(obligatoryMoves)
        x, y = obligatoryMoves[obligatoryMoves[0][0].index(max(obligatoryMoves[0][:][0]))][1]
        gameField[y][x] = aiChar
    elif validMoves:
        x, y = random.choice(validMoves)
        gameField[y][x] = aiChar
    else:
        print("Error with validMoves being 0!")

    extendField(gameField, aiChar)
    checkIfAiHasWon()


def checkIfPlayerHasWon():
    if aiHasWon:
        return False
    global playerHasWon
    global winningTiles

    for basePattern in playerWinningPatterns:
        for pattern in mixPattern(basePattern):
            for j, row in enumerate(gameField):
                for i, tile in enumerate(row):
                    playerNum, _, _, _ = findPattern(pattern, gameField, (i, j))
                    if playerNum >= 5:
                        print('player has won')
                        playerHasWon = True
                        winningTiles = []
                        for v, v_row in enumerate(pattern):
                            for u, u_tile in enumerate(v_row):
                                if u_tile == playerChar:
                                    winningTiles.append((u + i, j + v))
                        print(winningTiles)
                        return

def checkIfAiHasWon():
    if playerHasWon:
        return False
    global aiHasWon
    global winningTiles

    for basePattern in aiWinningPatterns:
        for pattern in mixPattern(basePattern):
            for j, row in enumerate(gameField):
                for i, tile in enumerate(row):
                    _, aiNum, _, _ = findPattern(pattern, gameField, (i, j))
                    if aiNum >= 5:
                        print('ai has won')
                        aiHasWon = True
                        winningTiles = []
                        for v, v_row in enumerate(pattern):
                            for u, u_tile in enumerate(v_row):
                                if u_tile == aiChar:
                                    winningTiles.append((u + i, j + v))
                        print(winningTiles)
                        return


def render():
    global screen

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
            elif tile == aiChar:
                tileColor = aiColor
            if (i, j) in winningTiles:
                if playerHasWon:
                    playerWonColor = (127 + 127 * math.sin(time.time()*10), 255, 127 + 127 * math.cos(time.time()* 100))
                    tileColor = playerWonColor
                if aiHasWon:
                    aiWonColor = (255, 127 + 127 * math.sin(time.time()*10), 127 + 127 * math.cos(time.time()* 100))
                    tileColor = aiWonColor
            pygame.draw.rect(screen, tileColor, [gameFieldAnchor[0] + offset_x + i * tileSize + 1, gameFieldAnchor[1] + offset_y + j * tileSize + 1, tileSize - 1, tileSize - 1])

    message = ""
    if playerHasWon:
        message = "You won! Press 'R' to reset!"
    elif aiHasWon:
        message = "AI won! Press 'R' to reset!"
    if playerHasWon or aiHasWon:
        textsurface = gameFont.render(message, False, (123,104,238))
        textRect = textsurface.get_rect(center = (window_width / 2, window_height / 8))
        screen.blit(textsurface, textRect)

    # Debug gameFieldAnchor
    # pygame.draw.circle(screen, (255, 0, 0), (int(gameFieldAnchor[0] + offset_x), int(gameFieldAnchor[1]) + offset_y), 5)

    clock.tick(60)
    pygame.display.flip()

def setup():
    global gameField
    global gameFieldAnchor
    global winningTiles
    global prevDragPosition
    global selectedTile
    global offset_x
    global offset_y
    global mouse_x
    global mouse_y
    global playerHasWon
    global aiHasWon
    global firstMove
    global tileSize

    tileSize = 20


    gameField = [['', '', ''], ['', '', ''], ['', '', '']]
    gameFieldAnchor = (window_width / 2 - tileSize, window_height / 2 - tileSize)
    winningTiles = []
    winningTiles = []

    prevDragPosition = (0, 0)
    selectedTile = (0, 0)

    (offset_x, offset_y) = (0, 0)
    mouse_x, mouse_y = 0, 0

    firstMove = True

    playerHasWon = False
    aiHasWon = False

def loop():
    global gameField
    global gameFieldAnchor
    global winningTiles
    global prevDragPosition
    global selectedTile
    global offset_x
    global offset_y
    global mouse_x
    global mouse_y
    global playerHasWon
    global aiHasWon
    global firstMove
    global tileSize

    running = True
    while running:

        # EVENTS

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                if event.key == pygame.K_r:
                    setup()
                if event.key == pygame.K_SPACE:
                    gameFieldAnchor = (window_width / 2 - len(gameField[0]) // 2 * tileSize, window_height / 2 - len(gameField) // 2 * tileSize)
                    offset_x, offset_y = 0, 0
                if event.key == pygame.K_q:
                    print("valid tile:", whichTile((mouse_x, mouse_y), True))

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1 and not (playerHasWon or aiHasWon):

                    if firstMove:
                        firstMove = False
                        gameFieldAnchor = ((event.pos[0] - offset_x) // tileSize * tileSize - tileSize, (event.pos[1] - offset_y) // tileSize * tileSize - tileSize)
                        # print('event.pos:', event.pos)
                        # print('gameFieldAnchor', gameFieldAnchor)
                        gameField[1][1] = playerChar
                        aiTurn()
                        extendField(gameField, aiChar)

                    if isMousePositionValid(event.pos):
                        (x, y) = whichTile(event.pos, True)
                        gameField[y][x] = playerChar
                        extendField(gameField, playerChar)

                        checkIfPlayerHasWon()

                        aiTurn()




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

        render()

    pygame.quit()

def main():
    setup()
    loop()


if __name__ == "__main__":
    main()
