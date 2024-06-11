import pygame, copy, math
from Board import boardPattern

gameBoard = copy.deepcopy(boardPattern)
class Pacman:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.mouthOpen = False
        self.pacSpeed = 1/4
        self.mouthChangeDelay = 5
        self.mouthChangeCount = 0
        self.dir = 0 # 0: North, 1: East, 2: South, 3: West
        self.newDir = 0

    def canMove(row, col):
        if col == -1 or col == len(gameBoard[0]):
            return True
        if gameBoard[int(row)][int(col)] != 3:
            return True
        return False
    
    def update(self):
        if self.newDir == 0:
            if self.canMove(math.floor(self.row - self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 1:
            if self.canMove(self.row, math.ceil(self.col + self.pacSpeed)) and self.row % 1.0 == 0:
                self.col += self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 2:
            if self.canMove(math.ceil(self.row + self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 3:
            if self.canMove(self.row, math.floor(self.col - self.pacSpeed)) and self.row % 1.0 == 0:
                self.col -= self.pacSpeed
                self.dir = self.newDir
                return

        if self.dir == 0:
            if self.canMove(math.floor(self.row - self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.pacSpeed
        elif self.dir == 1:
            if self.canMove(self.row, math.ceil(self.col + self.pacSpeed)) and self.row % 1.0 == 0:
                self.col += self.pacSpeed
        elif self.dir == 2:
            if self.canMove(math.ceil(self.row + self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.pacSpeed
        elif self.dir == 3:
            if self.canMove(self.row, math.floor(self.col - self.pacSpeed)) and self.row % 1.0 == 0:
                self.col -= self.pacSpeed

    # Draws pacman based on his current state
    def draw(self):
        if not game.started:
            pacmanImage = pygame.image.load(ElementPath + "element112.png")
            pacmanImage = pygame.transform.scale(pacmanImage, (int(tile * 1.5), int(tile * 1.5)))
            screen.blit(pacmanImage, (self.col * tile + spriteOffset, self.row * tile + spriteOffset, tile, tile))
            return

        if self.mouthChangeCount == self.mouthChangeDelay:
            self.mouthChangeCount = 0
            self.mouthOpen = not self.mouthOpen
        self.mouthChangeCount += 1
        # pacmanImage = pygame.image.load("Sprites/element049.png")
        if self.dir == 0:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(ElementPath + "element049.png")
            else:
                pacmanImage = pygame.image.load(ElementPath + "element051.png")
        elif self.dir == 1:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(ElementPath + "element052.png")
            else:
                pacmanImage = pygame.image.load(ElementPath + "element054.png")
        elif self.dir == 2:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(ElementPath + "element053.png")
            else:
                pacmanImage = pygame.image.load(ElementPath + "element055.png")
        elif self.dir == 3:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(ElementPath + "element048.png")
            else:
                pacmanImage = pygame.image.load(ElementPath + "element050.png")

        pacmanImage = pygame.transform.scale(pacmanImage, (int(tile * 1.5), int(tile * 1.5)))
        screen.blit(pacmanImage, (self.col * tile + spriteOffset, self.row * tile + spriteOffset, tile, tile))
