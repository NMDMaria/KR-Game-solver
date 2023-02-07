import sys
import time
from copy import deepcopy
from queue import Queue

import pygame
import pygame_menu
import random


class Button:
    def __init__(self, display=None, text="", left=0, top=0, w=0, h=0, backgroundColor=(20, 20, 20),
                 backgroundColorSelected=(90, 90, 90), font="arial",
                 fontSize=16, textColor=(255, 255, 255),
                 value=""):
        # Init basic values
        self.display = display
        self.backgroundColor = backgroundColor
        self.backgroundColorSelected = backgroundColorSelected
        self.text = text
        self.font = font
        self.w = w
        self.h = h
        self.selected = False
        self.fontSize = fontSize
        self.textColor = textColor
        self.value = value
        fontObj = pygame.font.SysFont(self.font, self.fontSize)
        self.text = fontObj.render(self.text, True, self.textColor)
        self.rect = pygame.Rect(left, top, w, h)

        # Centre text
        self.textRect = self.text.get_rect(center=self.rect.center)

    def setSelect(self, selected: bool):
        self.selected = selected
        self.draw()

    def select(self, coord: tuple):
        if self.rect.collidepoint(coord) and self.selected == False:
            self.setSelect(True)
            return True
        return False

    def update(self):
        self.rect.left = self.left
        self.rect.top = self.top
        self.textRect = self.text.get_rect(center=self.rect.center)

    def draw(self):
        pygame.draw.rect(self.display, self.backgroundColorSelected if self.selected else self.backgroundColor,
                         self.rect)
        self.display.blit(self.text, self.textRect)


class ButtonsGroup:
    def __init__(self, buttons=[], left=0, top=0, indexSelected=None, spaceBetween=10):
        self.buttons = buttons
        self.indexSelected = indexSelected
        if indexSelected is not None:
            self.buttons[self.indexSelected].selected = True
        self.top = top
        self.left = left
        self.spaceBetween = spaceBetween

        leftCurrent = self.left
        for button in self.buttons:
            button.top = self.top
            button.left = leftCurrent
            button.update()
            leftCurrent += (spaceBetween + button.w)

    def select(self, coord: tuple):
        for index, button in enumerate(self.buttons):
            if button.select(coord):
                if self.indexSelected is not None:
                    self.buttons[self.indexSelected].setSelect(False)
                self.indexSelected = index
                return True
        return False

    def draw(self):
        for button in self.buttons:
            button.draw()

    def value(self):
        if self.indexSelected is not None:
            return self.buttons[self.indexSelected].value
        return None

    def reset(self):
        if self.indexSelected is not None:
            self.buttons[self.indexSelected].setSelect(False)
        self.indexSelected = None


class Game:
    JMIN = None
    JMAX = None
    cellDim = 150
    player1 = 1
    player2 = 2
    emptyCell = '.'
    poisonedCell = 0
    maxScore = 0

    def displayText(self, text, top, height, font="arial", fontSize=15, textColor=(255, 250, 226)):
        fontObj = pygame.font.SysFont(font, fontSize)
        textRender = fontObj.render(text, True, textColor)
        rect = pygame.Rect(0, top, self.display.get_width(), height - 1)
        textRect = textRender.get_rect(center=rect.center)
        self.display.blit(textRender, textRect)

    def __init__(self, display, dimensions, poisoned, matrix=None):
        self.lastMove = None
        self.marked = []
        if matrix is None:
            self.init(display, dimensions, poisoned)
        else:  # while in game
            self.cellTable = matrix

    @classmethod
    def init(cls, display, dimensions, poisoned):
        cls.display = display
        cls.mode = 1  # player vs computer
        cls.cellTable = [cls.emptyCell] * dimensions[0] * dimensions[1]
        cls.cellGrid = []
        cls.dimensions = dimensions
        cls.poisoned = poisoned
        cls.cellDim = min((display.get_width()) / dimensions[1], display.get_height() / dimensions[0] - 40)
        cls.poisonImage = pygame.transform.scale(pygame.image.load("./images/poison.png"), (cls.cellDim, cls.cellDim))

        # Up and bottom padding:
        cls.topPadding = (display.get_height() - 30 - (cls.cellDim + 1) * dimensions[0]) / 2
        cls.leftPadding = (display.get_width() - (cls.cellDim + 1) * dimensions[1]) / 2

        for i in range(dimensions[0]):
            for j in range(dimensions[1]):
                cell = pygame.Rect(j * (cls.cellDim + 1) + cls.leftPadding,
                                   i * (cls.cellDim + 1) + cls.topPadding,
                                   cls.cellDim, cls.cellDim)
                cls.cellGrid.append(cell)

        while poisoned:
            position = random.randint(0, dimensions[0] * dimensions[1] - 1)
            if cls.cellTable[position] == cls.emptyCell:
                cls.cellTable[position] = cls.poisonedCell
                poisoned -= 1

        cls.currentPlayer = 1

    @classmethod
    def setMode(cls, mode):
        cls.mode = mode

    @classmethod
    def setAlgorithm(cls, algorithm):
        cls.algorithm = algorithm

    @classmethod
    def setPlayer(cls, player):
        cls.JMIN = player
        cls.JMAX = cls.player1 if cls.JMIN == cls.player2 else cls.player2

    def drawBoard(self):
        self.displayText(f"{'Red' if self.currentPlayer == 1 else 'Blue'} has to move",
                         0, self.__class__.topPadding, fontSize=int(self.__class__.topPadding // 2))

        for i in range(len(self.cellGrid)):
            if i in self.marked:
                pygame.draw.rect(self.__class__.display, (100, 100, 100), self.cellGrid[i])
            elif self.cellTable[i] == self.poisonedCell:
                pygame.draw.rect(self.__class__.display, (255, 255, 255), self.cellGrid[i])
                self.__class__.display.blit(self.__class__.poisonImage, (
                    i % self.__class__.dimensions[1] * (self.__class__.cellDim + 1) + self.__class__.leftPadding,
                    i // self.__class__.dimensions[1] * (self.__class__.cellDim + 1) + self.__class__.topPadding))
            elif self.cellTable[i] == self.player1:
                pygame.draw.rect(self.__class__.display, (192, 50, 33), self.cellGrid[i])
            elif self.cellTable[i] == self.player2:
                pygame.draw.rect(self.__class__.display, (48, 102, 190), self.cellGrid[i])
            else:
                pygame.draw.rect(self.__class__.display, (255, 255, 255), self.cellGrid[i])

        if self.__class__.mode == 3:
            self.displayText("Press any key to continue", self.display.get_height() - self.__class__.topPadding,
                             self.__class__.topPadding, fontSize=int(self.__class__.topPadding // 2))

        pygame.display.flip()

    def finalScreen(self):
        self.display.fill((20, 20, 20))
        self.displayText(f"{'Red' if self.currentPlayer == 1 else 'Blue'} has won !!!!",
                         0, self.display.get_height(),
                         fontSize=int(self.display.get_height() // 6))
        pygame.display.flip()

    @classmethod
    def otherPlayer(cls, player):
        if player == 1:
            return 2
        else:
            return 1

    def markCell(self, index):
        if index in self.marked:
            self.marked.remove(index)
            return True
        elif self.cellTable[index] == self.poisonedCell:
            return "Patratica otravita"
        elif self.cellTable[index] != self.emptyCell:
            return "Patratica nu este goala"

        self.marked.append(index)
        return True

    def makeSelection(self, left, right):
        verify = self.verifyMove(left, right)

        if not verify:
            return "Mutare invalida"

        indexLeft = (left[1] // self.dimensions[1], left[1] % self.dimensions[1])
        indexRight = (right[1] // self.dimensions[1], right[1] % self.dimensions[1])

        for lin in range(min(indexLeft[0], indexRight[0]), max(indexLeft[0], indexRight[0]) + 1):
            for col in range(min(indexLeft[1], indexRight[1]), max(indexLeft[1], indexRight[1]) + 1):
                if self.cellGrid[lin * self.dimensions[1] + col] != left[0]:
                    self.markCell(lin * self.dimensions[1] + col)
        return True

    def colorSelection(self):
        for index in self.marked:
            self.cellTable[index] = self.currentPlayer
        self.marked = []

    def verifyMove(self, left, right):
        indexLeft = (left[1] // self.dimensions[1], left[1] % self.dimensions[1])
        indexRight = (right[1] // self.dimensions[1], right[1] % self.dimensions[1])

        nextTo = False
        border = False
        # Parcurgere matrice
        for lin in range(min(indexLeft[0], indexRight[0]), max(indexLeft[0], indexRight[0]) + 1):
            if lin == 0 or lin == self.dimensions[0] - 1:
                border = True
            for col in range(min(indexLeft[1], indexRight[1]), max(indexLeft[1], indexRight[1]) + 1):
                if col == 0 or col == self.dimensions[1] - 1:
                    border = True
                if self.cellTable[lin * self.dimensions[1] + col] != self.emptyCell:
                    return False
                neighbours = self.neighbours(lin * self.dimensions[1] + col)
                for neighbour in neighbours:
                    if self.cellTable[neighbour] == self.currentPlayer:
                        nextTo = True
        return nextTo or border

    def countEmpty(self, index, sense="row"):
        if sense == "row":
            empty = 0
            while index % self.dimensions[1] != 0:
                if self.cellTable[index] == self.emptyCell:
                    empty += 1
                index += 1
            return empty
        elif sense == "col":
            empty = 0
            while index < self.dimensions[0] * self.dimensions[1]:
                if self.cellTable[index] == self.emptyCell:
                    empty += 1
                index = index + self.dimensions[1]
            return empty
        return 0

    def countEmpty(self):
        return len([index for index in range(len(self.cellTable)) if self.cellTable[index] == self.emptyCell])

    def countPoisioned(self, index, sense="row"):
        if sense == "row":
            empty = 0
            while index % self.dimensions[1] != 0:
                if self.cellTable[index] == self.poisonedCell:
                    empty += 1
                index += 1
            return empty
        elif sense == "col":
            empty = 0
            while index < self.dimensions[0] * self.dimensions[1]:
                if self.cellTable[index] == self.poisonedCell:
                    empty += 1
                index = index + self.dimensions[1]
            return empty
        return 0

    def getPoisonedIdx(self):
        return [i for i in range(len(self.cellTable)) if self.cellTable[i] == self.poisonedCell]

    def isFinal(self):
        if not self.path(self.getPoisonedIdx()):
            return self.currentPlayer
        elif self.countEmpty() == 0:
            return self.otherPlayer(self.currentPlayer)
        else:
            return False

    def neighbours(self, index):
        result = []
        r, c = index // self.dimensions[1], index % self.dimensions[1]

        if r + 1 < self.dimensions[0]:
            result.append((r + 1) * self.dimensions[1] + c)
        if r - 1 >= 0:
            result.append((r - 1) * self.dimensions[1] + c)
        if c + 1 < self.dimensions[1]:
            result.append(r * self.dimensions[1] + c + 1)
        if c - 1 >= 0:
            result.append(r * self.dimensions[1] + c - 1)
        return result

    def bfs(self, start):
        q = Queue()
        q.put(start)
        visited = set([start])

        while not q.empty():
            last_node = q.get()
            nodes = self.neighbours(last_node)
            for node in nodes:
                if node not in visited and\
                        self.cellTable[node] == self.emptyCell or self.cellTable[node] == self.poisonedCell:
                    visited.add(node)
                    q.put(node)
        return len(visited)

    def estScore(self, depth):
        finalPlayer = self.isFinal()

        if finalPlayer == self.JMAX:
            return self.maxScore + depth
        elif finalPlayer == self.JMIN:
            return -self.maxScore - depth
        else:
            return self.calcScore(self.JMAX) - self.calcScore(self.JMIN)

    def getMostX(self, player, index, direction='up'):
        r, c = index // self.dimensions[1], index % self.dimensions[1]

        if direction == "up":
            while r + 1 < self.dimensions[0] and self.cellTable[(r + 1) * self.dimensions[1] + c] == player:
                r = r + 1

            if r == self.dimensions[0]:
                return None
            return r * self.dimensions[1] + c
        elif direction == "down":
            while r - 1 >= 0 and self.cellTable[(r - 1) * self.dimensions[1] + c] == player:
                r = r - 1

            if r == 0:
                return None
            return r * self.dimensions[1] + c
        elif direction == "left":
            while c - 1 >= 0 and self.cellTable[r * self.dimensions[1] + c - 1] == player:
                c = c - 1

            if c == 0:
                return None
            return r * self.dimensions[1] + c
        elif direction == "right":
            while c + 1 < self.dimensions[1] and self.cellTable[r * self.dimensions[1] + c + 1] == player:
                c = c + 1

            if c == self.dimensions[1] - 1:
                return None
            return r * self.dimensions[1] + c

    def calcScore(self, player):
        borderEmpty = 0
        aux = [0, self.dimensions[0] - 1]
        for lin in aux:
            for col in range(self.dimensions[1] - 1):
                if self.cellTable[lin * self.dimensions[1] + col] == self.emptyCell:
                    borderEmpty += 1
        used = []
        for index in range(self.cellTable):
            if self.cellTable[index] == player and index not in used:
                directions = ['up', 'down', 'left', 'right']
                for dir in directions:
                    m = self.getMostX(player, index, dir)
                    if m and m not in used:
                        used.append(m)
        return borderEmpty + len(used)

    def rec(self, start, rest, explored, path):
        min = []
        if not rest:
            return path

        for val in rest:
            p = self.BFS_SP(start, val, deepcopy(explored))
            if not p:
                return []
            cp = deepcopy(rest)
            cp.remove(val)
            dr = self.rec(val, cp, explored + [start], path[:-1] + p)
            if min == [] or len(dr) < len(min):
                min = dr

        return min

    def path(self, l):
        minPath = []

        for index in range(len(l)):
            p = self.rec(l[index], l[:index] + l[(index + 1):], [], [])
            if minPath == [] or len(minPath) > len(p):
                minPath = p

        return minPath

    def BFS_SP(self, start, goal, explored = []):
        q = Queue()
        q.put([start])
        if start == goal:
            return []

        while not q.empty():
            path = q.get()
            node = path[-1]

            if node not in explored:
                n = self.neighbours(node)

                for neighbour in n:
                    if self.cellTable[neighbour] == self.player1 or self.cellTable[neighbour] == self.player2:
                        continue
                    if neighbour in explored:
                        continue
                    new_path = list(path)
                    new_path.append(neighbour)
                    q.put(new_path)

                    if neighbour == goal:
                        return new_path

                explored.append(node)

        return []

    def generateAllMoves(self, leftTop):
        # always go right down
        l_moves = []



    def move(self, player):
        l_moves = []
        for lin in range(self.dimensions[0]):
            for col in range(self.dimensions[1]):
                if self.cellTable[lin * self.dimensions[1] + col] == self.emptyCell:
                    if lin == 0 or col == 0 or lin == self.dimensions[0] - 1 or col == self.dimensions[1] - 1:



    def __str__(self):
        s = ""
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                s += "|" + str(self.cellTable[i * self.dimensions[1] + j])
            s += "|\n"
        return s

    def __repr__(self):
        return self.__str__()


class State:
    def __init__(self, game, currentPlayer, depth, parent=None, score=None):
        self.game = game
        self.currentPlayer = currentPlayer
        self.depth = depth
        self.parent = parent
        self.score = score

        self.possibleMoves = []
        self.move = None

    def moves(self):
        possibleMoves = self.game.moves(self.currentPlayer)
        otherPlayer = self.game.otherPlayer(self.currentPlayer)
        possibleStates = [State(move, otherPlayer, self.depth - 1, parent=self) for move in possibleMoves]
        return possibleStates

    def __str__(self):
        return self.game.__str__() + f"(Current player: {self.currentPlayer})"

    def __repr__(self):
        return self.__str__()


def min_max(state):
    if state.depth == 0 or state.game.isFinal():
        state.score = state.game.estimScore(state.depth)
        return state
    state.possibleMoves = state.moves()
    moveScore = [min_max(move) for move in state.possibleMoves]

    if state.currentPlayer == Game.JMAX:
        state.move = max(moveScore, key=lambda x: x.score)
    else:
        state.move = min(moveScore, key=lambda x: x.score)
    state.score = state.move.score
    return state


def alpha_beta(alpha, beta, state):
    if state.depth == 0 or state.game.isFinal():
        state.score = state.game.estimScore(state.depth)
        return state

    if alpha > beta:
        return state

    state.possibleMoves = state.moves()
    if state.currentPlayer == Game.JMAX:
        currentScore = float("-inf")

        for move in state.possibleMoves:
            newState = alpha_beta(alpha, beta, move)
            if currentScore < newState.score:
                state.move = newState
                currentScore = newState.score
            if alpha < newState.score:
                alpha = newState.score
                if alpha >= beta:
                    break
    elif state.currentPlayer == Game.JMIN:
        currentScore = float("-inf")

        for move in state.possibleMoves:
            newState = alpha_beta(alpha, beta, move)
            if currentScore > newState.score:
                state.move = newState
                currentScore = newState.score
            if beta > newState.score:
                beta = newState.score
                if alpha >= beta:
                    break

    state.score = state.move.score
    return state


MAX_DEPTH = 5


class Menu:
    def __init__(self, settingsPath=""):
        if settingsPath == "":
            self.dimensions = (800, 600)
            self.boardDimensions = (4, 5)
            self.boardPoisoned = 2
        else:
            self.dimensions = (800, 600)
            readSettings = open(settingsPath)
            line = readSettings.readline()
            if line.find("N=") == -1:
                self.boardDimensions = (4, 5)
            else:
                self.boardDimensions = (int(line.split("N=")[1].strip()), 5)
                line = readSettings.readline()
                if line.find("M=") != -1:
                    self.boardDimensions = (int(self.boardDimensions[0]),
                                            int(line.split("M=")[1].strip()))

            line = readSettings.readline()
            if line.find("O=") != -1:
                self.boardPoisoned = int(line.split("O=")[1].strip())
            else:
                self.boardPoisoned = 2

        pygame.init()
        pygame.display.set_caption("Negrut Maria-Daniela - Hap")
        chocoIcon = pygame.image.load("images/icon.png")
        pygame.display.set_icon(chocoIcon)
        self.screen = pygame.display.set_mode(self.dimensions)
        self.screen.fill((20, 20, 20))
        self.game = Game(self.screen, self.boardDimensions, self.boardPoisoned)

        self.typeGame()

    def typeGame(self):
        fontObj = pygame.font.SysFont("Arial", 16)
        text = fontObj.render("Tipul jocului:  ", True, (255, 255, 255))
        rect = pygame.Rect(40, 30, 60, 30)
        textRect = text.get_rect(center=rect.center)
        self.screen.blit(text, textRect)

        btn = ButtonsGroup(
            top=30,
            left=170,
            buttons=[
                Button(display=self.screen, w=150, h=30, text="Calculator VS Jucator", value=1),
                Button(display=self.screen, w=150, h=30, text="Jucator VS Jucator", value=2),
                Button(display=self.screen, w=150, h=30, text="Calculator VS Calculator", value=3)
            ],
            indexSelected=0
        )

        ok = Button(display=self.screen, top=100, left=30, w=40, h=30, text="ok",
                    backgroundColor=(155, 0, 55))
        btn.draw()
        ok.draw()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if not btn.select(pos):
                        if ok.select(pos):
                            self.screen.fill((20, 20, 20))  # stergere ecran
                            self.game.setMode(btn.value())
                            if btn.value() == 1:
                                self.menuCvP()
                            elif btn.value() == 3:
                                self.menuCvC()
                            else:
                                self.play()

            pygame.display.update()

    def menuCvC(self):
        fontObj = pygame.font.SysFont("Arial", 16)
        text = fontObj.render("Algoritmul folosit: ", True, (255, 255, 255))
        rect = pygame.Rect(40, 30, 85, 30)
        textRect = text.get_rect(center=rect.center)
        self.screen.blit(text, textRect)

        btn_alg = ButtonsGroup(
            top=30,
            left=170,
            buttons=[
                Button(display=self.screen, w=80, h=30, text="Min-Max", value="minmax"),
                Button(display=self.screen, w=80, h=30, text="Alpha-Beta", value="alphabeta")
            ],
            indexSelected=0
        )

        ok = Button(display=self.screen, top=100, left=30, w=40, h=30, text="ok",
                    backgroundColor=(155, 0, 55))
        btn_alg.draw()
        ok.draw()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if not btn_alg.select(pos):
                        if ok.select(pos):
                            self.screen.fill((20, 20, 20))  # stergere ecran
                            self.game.setAlgorithm(btn_alg.value())
                            self.play()
                            return
            pygame.display.update()

    def menuCvP(self):
        fontObj = pygame.font.SysFont("Arial", 16)
        text = fontObj.render("Algoritmul folosit: ", True, (255, 255, 255))
        rect = pygame.Rect(40, 30, 85, 30)
        textRect = text.get_rect(center=rect.center)
        self.screen.blit(text, textRect)

        btn_alg = ButtonsGroup(
            top=30,
            left=170,
            buttons=[
                Button(display=self.screen, w=80, h=30, text="Min-Max", value="minmax"),
                Button(display=self.screen, w=80, h=30, text="Alpha-Beta", value="alphabeta")
            ],
            indexSelected=0
        )

        fontObj = pygame.font.SysFont("Arial", 16)
        text = fontObj.render("Culoarea jucatorului: ", True, (255, 255, 255))
        rect = pygame.Rect(40, 100, 100, 30)
        textRect = text.get_rect(center=rect.center)
        self.screen.blit(text, textRect)

        btn_juc = ButtonsGroup(
            top=100,
            left=170,
            buttons=[
                Button(display=self.screen, w=35, h=30, text="Red",
                       backgroundColorSelected=(192, 50, 33), value=1),
                Button(display=self.screen, w=35, h=30, text="Blue",
                       backgroundColorSelected=(48, 102, 190), value=2)
            ],
            indexSelected=0
        )

        fontObj = pygame.font.SysFont("Arial", 16)
        text = fontObj.render("Dificultate: ", True, (255, 255, 255))
        rect = pygame.Rect(40, 170, 50, 30)
        textRect = text.get_rect(center=rect.center)
        self.screen.blit(text, textRect)

        btn_dif = ButtonsGroup(
            top=170,
            left=170,
            buttons=[
                Button(display=self.screen, w=80, h=30, text="Incepator", value=1),
                Button(display=self.screen, w=80, h=30, text="Mediu", value=2),
                Button(display=self.screen, w=80, h=30, text="Avansat", value=3)
            ],
            indexSelected=0
        )

        ok = Button(display=self.screen, top=240, left=30, w=40, h=30, text="ok",
                    backgroundColor=(155, 0, 55))
        btn_alg.draw()
        btn_juc.draw()
        btn_dif.draw()
        ok.draw()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if not btn_alg.select(pos):
                        if not btn_juc.select(pos):
                            if not btn_dif.select(pos):
                                if ok.select(pos):
                                    self.screen.fill((20, 20, 20))  # stergere ecran
                                    self.game.setAlgorithm(btn_alg.value())
                                    self.game.setPlayer(btn_juc.value())
                                    self.play()
                                    return
            pygame.display.update()

    def play(self):
        state = State(self.game, 1, MAX_DEPTH)
        state.game.drawBoard()

        isMoving = None
        while True:
            if Game.mode == 1 or Game.mode == 2:  # cvp
                btn = ButtonsGroup(
                    top=self.screen.get_height() - Game.topPadding - 20,
                    left=Game.leftPadding,
                    buttons=[
                        Button(display=self.screen, w=80, h=30, text="Muta", value="muta"
                               , backgroundColor=(100, 100, 100)),
                        Button(display=self.screen, w=80, h=30, text="Reincearca", value="r"
                               , backgroundColor=(100, 100, 100))
                    ]
                )

                btn.draw()
                pygame.display.flip()

                breakFlag = False
                while not breakFlag:
                    if (state.currentPlayer == Game.JMIN and Game.mode == 1)\
                            or Game.mode == 2: # pvp muta mereu player nu calc
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif ev.type == pygame.MOUSEBUTTONDOWN:
                                pos = pygame.mouse.get_pos()

                                if btn.select(pos):
                                    if btn.value() == "r":
                                        state.game.marked = []
                                        state.game.drawBoard()
                                        btn.reset()
                                        isMoving = None
                                        breakFlag = True
                                    else:
                                        state.game.colorSelection()
                                        state.currentPlayer = Game.otherPlayer(state.currentPlayer)
                                        state.game.currentPlayer = Game.otherPlayer(state.game.currentPlayer)
                                        self.screen.fill((20, 20, 20))
                                        state.game.drawBoard()
                                        btn.reset()
                                        isMoving = None

                                        if state.game.isFinal():
                                            state.game.finalScreen()
                                            return
                                        breakFlag = True
                                else:
                                    if isMoving is None:
                                        for np in range(len(state.game.cellGrid)):
                                            if state.game.cellGrid[np].collidepoint(pos):
                                                aux = state.game.markCell(np)
                                                if aux == True:
                                                    state.game.drawBoard()
                                                    isMoving = (state.game.cellGrid[np], np)
                                                else:
                                                    print(aux)
                                                break
                                    elif isMoving != "finished":
                                        for np in range(len(state.game.cellGrid)):
                                            if state.game.cellGrid[np].collidepoint(pos):
                                                aux = state.game.makeSelection(isMoving,
                                                                               (state.game.cellGrid[np], np))
                                                if aux == True:
                                                    state.game.drawBoard()
                                                    isMoving = "finished"
                                                else:
                                                    print(aux)
                                                    state.game.marked = []
                                                    state.game.drawBoard()
                                                    isMoving = None
                                                breakFlag = True
                                                break
                    elif state.currentPlayer == Game.JMAX and Game.mode == 1:
                        tBefore = int(round(time.time() * 1000))
                        if state.game.algorithm == "minmax":
                            newState = min_max(state)
                        else:
                            newState = alpha_beta(-500, 500, state)
                        state.game = newState.game

                        print("Mutare calculator:\n" + str(state))
                        tAfter = int(round(time.time() * 1000))
                        print("Calculatorul a \"gandit\" timp de " + str(tAfter - tBefore) + " milisecunde.")
                        state.game.drawBoard()
                        if state.game.isFinal():
                            state.game.finalScreen()
                            break

                        state.currentPlayer = Game.otherPlayer(state.currentPlayer)
                        state.game.currentPlayer = Game.otherPlayer(state.currentPlayer)
                    pygame.display.update()

                pygame.display.update()


if __name__ == '__main__':
    Menu()
