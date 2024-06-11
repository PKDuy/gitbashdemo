import pygame
import copy
import math
from Board import originalGameBoard
from random import randrange

gameBoard = copy.deepcopy(originalGameBoard)
ElementPath = "Assets/ElementImages/"
square = 25
spriteRatio = 3/2
spriteOffset = square * (1 - spriteRatio) * (1/2)
screen = pygame.display.set_mode((700, 900))

ghostsafeArea = [15, 13] # The location the ghosts escape to when attacked
ghostGate = [[15, 13], [15, 14]]

class Ghost:
    def __init__(self, row, col, color, changeFeetCount):
        self.row = row
        self.col = col
        self.attacked = False
        self.color = color
        self.dir = randrange(4)
        self.dead = False
        self.changeFeetCount = changeFeetCount
        self.changeFeetDelay = 5
        self.target = [-1, -1]
        self.ghostSpeed = 1/4
        self.lastLoc = [-1, -1]
        self.attackedTimer = 240
        self.attackedCount = 0
        self.deathTimer = 120
        self.deathCount = 0

    def update(self):
        # print(self.row, self.col)
        if self.target == [-1, -1] or (self.row == self.target[0] and self.col == self.target[1]) or gameBoard[int(self.row)][int(self.col)] == 4 or self.dead:
            self.setTarget()
        self.setDir()
        self.move()

        if self.attacked:
            self.attackedCount += 1

        if self.attacked and not self.dead:
            self.ghostSpeed = 1/8

        if self.attackedCount == self.attackedTimer and self.attacked:
            if not self.dead:
                self.ghostSpeed = 1/4
                self.row = math.floor(self.row)
                self.col = math.floor(self.col)

            self.attackedCount = 0
            self.attacked = False
            self.setTarget()

        if self.dead and gameBoard[self.row][self.col] == 4:
            self.deathCount += 1
            self.attacked = False
            if self.deathCount == self.deathTimer:
                self.deathCount = 0
                self.dead = False
                self.ghostSpeed = 1/4

    def draw(self): # Ghosts states: Alive, Attacked, Dead Attributes: Color, Direction, Location
        ghostImage = pygame.image.load(ElementPath + "tile152.png")
        currentDir = ((self.dir + 3) % 4) * 2
        if self.changeFeetCount == self.changeFeetDelay:
            self.changeFeetCount = 0
            currentDir += 1
        self.changeFeetCount += 1
        if self.dead:
            tileNum = 152 + currentDir
            ghostImage = pygame.image.load(ElementPath + "tile" + str(tileNum) + ".png")
        elif self.attacked:
            if self.attackedTimer - self.attackedCount < self.attackedTimer//3:
                if (self.attackedTimer - self.attackedCount) % 31 < 26:
                    ghostImage = pygame.image.load(ElementPath + "tile0" + str(70 + (currentDir - (((self.dir + 3) % 4) * 2))) + ".png")
                else:
                    ghostImage = pygame.image.load(ElementPath + "tile0" + str(72 + (currentDir - (((self.dir + 3) % 4) * 2))) + ".png")
            else:
                ghostImage = pygame.image.load(ElementPath + "tile0" + str(72 + (currentDir - (((self.dir + 3) % 4) * 2))) + ".png")
        else:
            if self.color == "blue":
                tileNum = 136 + currentDir
                ghostImage = pygame.image.load(ElementPath + "tile" + str(tileNum) + ".png")
            elif self.color == "pink":
                tileNum = 128 + currentDir
                ghostImage = pygame.image.load(ElementPath + "tile" + str(tileNum) + ".png")
            elif self.color == "orange":
                tileNum = 144 + currentDir
                ghostImage = pygame.image.load(ElementPath + "tile" + str(tileNum) + ".png")
            elif self.color == "red":
                tileNum = 96 + currentDir
                if tileNum < 100:
                    ghostImage = pygame.image.load(ElementPath + "tile0" + str(tileNum) + ".png")
                else:
                    ghostImage = pygame.image.load(ElementPath + "tile" + str(tileNum) + ".png")

        ghostImage = pygame.transform.scale(ghostImage, (int(square * spriteRatio), int(square * spriteRatio)))
        screen.blit(ghostImage, (self.col * square + spriteOffset, self.row * square + spriteOffset, square, square))

    def isValidTwo(self, cRow, cCol, dist, visited):
        if cRow < 3 or cRow >= len(gameBoard) - 5 or cCol < 0 or cCol >= len(gameBoard[0]) or gameBoard[cRow][cCol] == 3:
            return False
        elif visited[cRow][cCol] <= dist:
            return False
        return True

    def isValid(self, cRow, cCol):
        if cCol < 0 or cCol > len(gameBoard[0]) - 1:
            return True
        for ghost in game.ghosts:
            if ghost.color == self.color:
                continue
            if ghost.row == cRow and ghost.col == cCol and not self.dead:
                return False
        if not ghostGate.count([cRow, cCol]) == 0:
            if self.dead and self.row < cRow:
                return True
            elif self.row > cRow and not self.dead and not self.attacked and not game.lockedIn:
                return True
            else:
                return False
        if gameBoard[cRow][cCol] == 3:
            return False
        return True

    def setDir(self): #Very inefficient || can easily refactor
        # BFS search -> Not best route but a route none the less
        dirs = [[0, -self.ghostSpeed, 0],
                [1, 0, self.ghostSpeed],
                [2, self.ghostSpeed, 0],
                [3, 0, -self.ghostSpeed]
        ]
        random.shuffle(dirs)
        best = 10000
        bestDir = -1
        for newDir in dirs:
            if self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]]) < best:
                if not (self.lastLoc[0] == self.row + newDir[1] and self.lastLoc[1] == self.col + newDir[2]):
                    if newDir[0] == 0 and self.col % 1.0 == 0:
                        if self.isValid(math.floor(self.row + newDir[1]), int(self.col + newDir[2])):
                            bestDir = newDir[0]
                            best = self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]])
                    elif newDir[0] == 1 and self.row % 1.0 == 0:
                        if self.isValid(int(self.row + newDir[1]), math.ceil(self.col + newDir[2])):
                            bestDir = newDir[0]
                            best = self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]])
                    elif newDir[0] == 2 and self.col % 1.0 == 0:
                        if self.isValid(math.ceil(self.row + newDir[1]), int(self.col + newDir[2])):
                            bestDir = newDir[0]
                            best = self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]])
                    elif newDir[0] == 3 and self.row % 1.0 == 0:
                        if self.isValid(int(self.row + newDir[1]), math.floor(self.col + newDir[2])):
                            bestDir = newDir[0]
                            best = self.calcDistance(self.target, [self.row + newDir[1], self.col + newDir[2]])
        self.dir = bestDir

    def calcDistance(self, a, b):
        dR = a[0] - b[0]
        dC = a[1] - b[1]
        return math.sqrt((dR * dR) + (dC * dC))

    def setTarget(self):
        if gameBoard[int(self.row)][int(self.col)] == 4 and not self.dead:
            self.target = [ghostGate[0][0] - 1, ghostGate[0][1]+1]
            return
        elif gameBoard[int(self.row)][int(self.col)] == 4 and self.dead:
            self.target = [self.row, self.col]
        elif self.dead:
            self.target = [14, 13]
            return

        # Records the quadrants of each ghost's target
        quads = [0, 0, 0, 0]
        for ghost in game.ghosts:
            # if ghost.target[0] == self.row and ghost.col == self.col:
            #     continue
            if ghost.target[0] <= 15 and ghost.target[1] >= 13:
                quads[0] += 1
            elif ghost.target[0] <= 15 and ghost.target[1] < 13:
                quads[1] += 1
            elif ghost.target[0] > 15 and ghost.target[1] < 13:
                quads[2] += 1
            elif ghost.target[0]> 15 and ghost.target[1] >= 13:
                quads[3] += 1

        # Finds a target that will keep the ghosts dispersed
        while True:
            self.target = [randrange(31), randrange(28)]
            quad = 0
            if self.target[0] <= 15 and self.target[1] >= 13:
                quad = 0
            elif self.target[0] <= 15 and self.target[1] < 13:
                quad = 1
            elif self.target[0] > 15 and self.target[1] < 13:
                quad = 2
            elif self.target[0] > 15 and self.target[1] >= 13:
                quad = 3
            if not gameBoard[self.target[0]][self.target[1]] == 3 and not gameBoard[self.target[0]][self.target[1]] == 4:
                break
            elif quads[quad] == 0:
                break

    def move(self):
        # print(self.target)
        self.lastLoc = [self.row, self.col]
        if self.dir == 0:
            self.row -= self.ghostSpeed
        elif self.dir == 1:
            self.col += self.ghostSpeed
        elif self.dir == 2:
            self.row += self.ghostSpeed
        elif self.dir == 3:
            self.col -= self.ghostSpeed

        # Incase they go through the middle tunnel
        self.col = self.col % len(gameBoard[0])
        if self.col < 0:
            self.col = len(gameBoard[0]) - 0.5



    def setAttacked(self, isAttacked):
        self.attacked = isAttacked

    def isAttacked(self):
        return self.attacked

    def setDead(self, isDead):
        self.dead = isDead

    def isDead(self):
        return self.dead
    
    
    ########
    
    
    
def displayLaunchScreen():
    # Draw Pacman Title
    pacmanTitle = ["text016.png", "text000.png", "text448.png", "text012.png", "text000.png", "text013.png"]
    for i in range(len(pacmanTitle)):
        char = pygame.image.load(TextPath + pacmanTitle[i])
        char = pygame.transform.scale(char, (int(square * 4), int(square * 4)))
        screen.blit(char, ((2 + 4 * i) * square, 2 * square, square, square))

    # Draw "Character / Nickname"
    characterTitle = [
        # Character
        "text002.png", "text007.png", "text000.png", "text018.png", "text000.png", "text002.png", "text020.png", "text004.png", "text018.png",
        # /
        "text015.png", "text042.png", "text015.png",
        # Nickname
        "text013.png", "text008.png", "text002.png", "text010.png", "text013.png", "text000.png", "text012.png", "text004.png"
    ]
    for i in range(len(characterTitle)):
        char = pygame.image.load(TextPath + characterTitle[i])
        char = pygame.transform.scale(char, (int(square), int(square)))
        screen.blit(char, ((4 + i) * square, 10 * square, square, square))

    # Draw Characters and their Nickname
    characters = [
        # Red Ghost
        [
            "text449.png", "text015.png", "text107.png", "text015.png", "text083.png", "text071.png", "text064.png", "text067.png", "text078.png", "text087.png",
            "text015.png", "text015.png", "text015.png", "text015.png",
            "text108.png", "text065.png", "text075.png", "text072.png", "text077.png", "text074.png", "text089.png", "text108.png"
        ],
        # Pink Ghost
        [
            "text450.png", "text015.png", "text363.png", "text015.png", "text339.png", "text336.png", "text324.png", "text324.png", "text323.png", "text345.png",
            "text015.png", "text015.png", "text015.png", "text015.png",
            "text364.png", "text336.png", "text328.png", "text333.png", "text330.png", "text345.png", "text364.png"
        ],
        # Blue Ghost
        [
            "text452.png", "text015.png", "text363.png", "text015.png", "text193.png", "text192.png", "text211.png", "text199.png", "text197.png", "text213.png", "text203.png",
            "text015.png", "text015.png", "text015.png",
            "text236.png", "text200.png", "text205.png", "text202.png", "text217.png", "text236.png"
        ],
        # Orange Ghost
        [
            "text451.png", "text015.png", "text363.png", "text015.png", "text272.png", "text270.png", "text266.png", "text260.png", "text281.png",
            "text015.png", "text015.png", "text015.png", "text015.png", "text015.png",
            "text300.png", "text258.png", "text267.png", "text281.png", "text259.png", "text260.png", "text300.png"
        ]
    ]
    for i in range(len(characters)):
        for j in range(len(characters[i])):
            if j == 0:
                    char = pygame.image.load(TextPath + characters[i][j])
                    char = pygame.transform.scale(char, (int(square * spriteRatio), int(square * spriteRatio)))
                    screen.blit(char, ((2 + j) * square - square//2, (12 + 2 * i) * square - square//3, square, square))
            else:
                char = pygame.image.load(TextPath + characters[i][j])
                char = pygame.transform.scale(char, (int(square), int(square)))
                screen.blit(char, ((2 + j) * square, (12 + 2 * i) * square, square, square))
    # Draw Pacman and Ghosts
    event = ["text449.png", "text015.png", "text452.png", "text015.png",  "text015.png", "text448.png", "text453.png", "text015.png", "text015.png", "text015.png",  "text453.png"]
    for i in range(len(event)):
        ele = pygame.image.load(TextPath + event[i])
        ele = pygame.transform.scale(ele, (int(square * 2), int(square * 2)))
        screen.blit(ele, ((4 + i * 2) * square, 24 * square, square, square))
    # Draw PlatForm Line
    wall = ["text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png"]
    for i in range(len(wall)):
        platform = pygame.image.load(TextPath + wall[i])
        platform = pygame.transform.scale(platform, (int(square * 2), int(square * 2)))
        screen.blit(platform, ((i * 2) * square, 26 * square, square, square))
    # "Duy Pham 2024"
    credit = ["text387.png", "text405.png", "text409.png", "text015.png", "text400.png", "text391.png", "text384.png", "text396.png", "text015.png", "text418.png", "text416.png", "text418.png", "text420.png"]
    for i in range(len(credit)):
        char = pygame.image.load(TextPath + credit[i])
        char = pygame.transform.scale(char, (int(square*1.5), int(square*1.5)))
        screen.blit(char, ((4.3 + 1.5 * i) * square, 28.75 * square, square, square))
    # "Press Space to Play"
    instructions = ["text016.png", "text018.png", "text004.png", "text019.png", "text019.png", "text015.png", "text019.png", "text016.png", "text000.png", "text002.png", "text004.png", "text015.png", "text020.png", "text014.png", "text015.png", "text016.png", "text011.png", "text000.png", "text025.png"]
    for i in range(len(instructions)):
        char = pygame.image.load(TextPath + instructions[i])
        char = pygame.transform.scale(char, (int(square), int(square)))
        screen.blit(char, ((4.5 + i) * square, 32.5 * square - 10, square, square))

    pygame.display.update()

def displayGameOverScreen():
    # Draw Pacman Title
    pacmanTitle = ["text016.png", "text000.png", "text448.png", "text012.png", "text000.png", "text013.png"]
    for i in range(len(pacmanTitle)):
        letter = pygame.image.load(TextPath + pacmanTitle[i])
        letter = pygame.transform.scale(letter, (int(square * 4), int(square * 4)))
        screen.blit(letter, ((2 + 4 * i) * square, 2 * square, square, square))

    # Draw "Character / Nickname"
    characterTitle = [
        # Character
        "text002.png", "text007.png", "text000.png", "text018.png", "text000.png", "text002.png", "text020.png", "text004.png", "text018.png",
        # /
        "text015.png", "text042.png", "text015.png",
        # Nickname
        "text013.png", "text008.png", "text002.png", "text010.png", "text013.png", "text000.png", "text012.png", "text004.png"
    ]
    for i in range(len(characterTitle)):
        letter = pygame.image.load(TextPath + characterTitle[i])
        letter = pygame.transform.scale(letter, (int(square), int(square)))
        screen.blit(letter, ((4 + i) * square, 10 * square, square, square))

    #Draw Characters and their Nickname
    characters = [
        # Red Ghost
        [
            "text449.png", "text015.png", "text107.png", "text015.png", "text083.png", "text071.png", "text064.png", "text067.png", "text078.png", "text087.png",
            "text015.png", "text015.png", "text015.png", "text015.png",
            "text108.png", "text065.png", "text075.png", "text072.png", "text077.png", "text074.png", "text089.png", "text108.png"
        ],
        # Pink Ghost
        [
            "text450.png", "text015.png", "text363.png", "text015.png", "text339.png", "text336.png", "text324.png", "text324.png", "text323.png", "text345.png",
            "text015.png", "text015.png", "text015.png", "text015.png",
            "text364.png", "text336.png", "text328.png", "text333.png", "text330.png", "text345.png", "text364.png"
        ],
        # Blue Ghost
        [
            "text452.png", "text015.png", "text363.png", "text015.png", "text193.png", "text192.png", "text211.png", "text199.png", "text197.png", "text213.png", "text203.png",
            "text015.png", "text015.png", "text015.png",
            "text236.png", "text200.png", "text205.png", "text202.png", "text217.png", "text236.png"
        ],
        # Orange Ghost
        [
            "text451.png", "text015.png", "text363.png", "text015.png", "text272.png", "text270.png", "text266.png", "text260.png", "text281.png",
            "text015.png", "text015.png", "text015.png", "text015.png", "text015.png",
            "text300.png", "text258.png", "text267.png", "text281.png", "text259.png", "text260.png", "text300.png"
        ]
    ]
    for i in range(len(characters)):
        for j in range(len(characters[i])):
            if j == 0:
                    letter = pygame.image.load(TextPath + characters[i][j])
                    letter = pygame.transform.scale(letter, (int(square * spriteRatio), int(square * spriteRatio)))
                    screen.blit(letter, ((2 + j) * square - square//2, (12 + 2 * i) * square - square//3, square, square))
            else:
                letter = pygame.image.load(TextPath + characters[i][j])
                letter = pygame.transform.scale(letter, (int(square), int(square)))
                screen.blit(letter, ((2 + j) * square, (12 + 2 * i) * square, square, square))
    # Draw Pacman and Ghosts
    event = ["text449.png", "text015.png", "text452.png", "text015.png",  "text015.png", "text448.png", "text453.png", "text015.png", "text015.png", "text015.png",  "text453.png"]
    for i in range(len(event)):
        ele = pygame.image.load(TextPath + event[i])
        ele = pygame.transform.scale(ele, (int(square * 2), int(square * 2)))
        screen.blit(ele, ((4 + i * 2) * square, 24 * square, square, square))
    # Draw PlatForm Line
    wall = ["text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png"]
    for i in range(len(wall)):
        platform = pygame.image.load(TextPath + wall[i])
        platform = pygame.transform.scale(platform, (int(square * 2), int(square * 2)))
        screen.blit(platform, ((i * 2) * square, 26 * square, square, square))
        
    # "Game Over"
    gameover = ["text070.png", "text064.png", "text076.png", "text068.png", "text079.png", "text078.png", "text086.png", "text068.png", "text082.png"]
    for i in range(len(gameover)):
        char = pygame.image.load(TextPath + gameover[i])
        char = pygame.transform.scale(char, (int(square*1.5), int(square*1.5)))
        screen.blit(char, ((7.25 + 1.5 * i) * square, 28.75 * square, square, square))
    # "Press Space to Play"
    toplay = ["text016.png", "text018.png", "text004.png", "text019.png", "text019.png", "text015.png", "text019.png", "text016.png", "text000.png", "text002.png", "text004.png", "text015.png", "text020.png", "text014.png", "text015.png", "text016.png", "text011.png", "text000.png", "text025.png", ]
    for i in range(len(toplay)):
        char = pygame.image.load(TextPath + toplay[i])
        char = pygame.transform.scale(char, (int(square), int(square)))
        screen.blit(char, ((4.5 + i) * square, 32.5 * square - 10, square, square))
    # "Press Enter to Exit"
    toexit = ["text016.png", "text018.png", "text004.png", "text019.png", "text019.png", "text015.png", "text004.png", "text013.png", "text020.png", "text004.png", "text018.png", "text015.png", "text020.png", "text014.png", "text015.png", "text004.png", "text024.png", "text008.png", "text020.png", ]
    for i in range(len(toexit)):
        char = pygame.image.load(TextPath + toexit[i])
        char = pygame.transform.scale(char, (int(square), int(square)))
        screen.blit(char, ((4.5 + i) * square, 35 * square - 10, square, square))

    pygame.display.update()    