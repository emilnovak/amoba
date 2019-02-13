#!/usr/bin/env python
# coding: utf-8

import pygame

background_colour = (205,211,213)
playerColor = (154,72,208)
aiColor = (255,169,135)
lineColor = (0, 0, 0)

(window_width, window_height) = (800, 600)
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Amőba')
screen.fill(background_colour)
pygame.display.flip()

clock = pygame.time.Clock()

tileSize = 20

emptyChar = ''
playerChar = 'X'
aiChar = 'O'

gameField = [['', '', ''], ['', '', ''], ['', '', '']]
gameFieldAnchor = (window_width / 2 - tileSize, window_height / 2 - tileSize)

prevDragPosition = (0, 0)
selectedTile = (0, 0)

(offset_x, offset_y) = (0, 0)

firstMove = True


def extendField(field, anchor, charToFind):
    # Check upper border
    if charToFind in field[0]:
        border = []
        for element in field[0]:
            border.append('')
        field.insert(0, border)

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

    # Check right border
    clearRight = True
    for row in field:
        if row[-1] == charToFind:
            clearRight = False
            break
    if not clearRight:
        for i, _ in enumerate(field):
            field[i].append('')



print(gameField)
extendField(gameField, gameFieldAnchor, playerChar)
print(gameField)
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
                gameFieldAnchor = (window_width / 2 - tileSize, window_height / 2 - tileSize)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            if event.button == 1:
                if firstMove:
                    firstMove = False
                    gameFieldAnchor = (event.pos[0] // tileSize * tileSize - tileSize, event.pos[1] // tileSize * tileSize - tileSize)
                    print('event.pos:', event.pos)
                    print('gameFieldAnchor', gameFieldAnchor)
                    gameField[1][1] = playerChar


            if event.button == 3:
                prevDragPosition = event.pos


        if event.type == pygame.MOUSEMOTION:
            # print(u'pressed buttons {}, position {{}{}} and relative movement {}'.format(event.buttons, event.pos, event.rel))

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
            if tile == playerChar:
                pygame.draw.rect(screen, playerColor, [gameFieldAnchor[0] + offset_x + i * tileSize, gameFieldAnchor[1] + offset_y + i * tileSize, tileSize, tileSize])


    clock.tick(60)
    pygame.display.flip()



pygame.quit()
