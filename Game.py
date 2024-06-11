import pygame
import math
from random import randrange
from Board import boardPattern
from Menu import displayMenu
import random
import copy
import os

BoardPath = "Assets/Sprites/BoardSprites/"
IntermissionPath = "Assets/Sprites/WhiteBoardSprites/"
ElementPath = "Assets/Sprites/ElementSprites/"
TextPath = "Assets/Sprites/TextSprites/"
DataPath = "Assets/HighScoreSaved/"
MusicPath = "Assets/Sounds/"

pygame.mixer.init()
pygame.init()
print(pygame.mixer.music.get_busy())

gameBoard = copy.deepcopy(boardPattern)

spriteRatio = 1.5
tile = 25 # Size of each unit tile
spriteOffset = tile * (1 - 1.5) * (1/2)

(width, height) = (len(gameBoard[0]) * tile, len(gameBoard) * tile) # Game screen (700, 900)
screen = pygame.display.set_mode((width, height))
pygame.display.flip()

musicPlaying = 0 # 0: Chomp | 1: Important | 2: Siren
pelletColor = (222, 161, 133)

COMMAND_KEYS = {
    "UP":[pygame.K_w, pygame.K_UP],
    "DOWN":[pygame.K_s, pygame.K_DOWN],
    "RIGHT":[pygame.K_d, pygame.K_RIGHT],
    "LEFT":[pygame.K_a, pygame.K_LEFT]
}

class Game:
    def __init__(self, level, score):
        self.paused = True
        self.ghostUpdateDelay = 1
        self.ghostUpdateCount = 0
        self.pacmanUpdateDelay = 1
        self.pacmanUpdateCount = 0
        self.tictakChangeDelay = 10
        self.tictakChangeCount = 0
        self.ghostsAttacked = False
        self.highScore = self.getHighScore()
        self.score = score
        self.level = level
        self.lives = 3
        self.ghosts = [Ghost(14.0, 13.5, "red", 0), Ghost(17.0, 11.5, "blue", 1), Ghost(17.0, 13.5, "pink", 2), Ghost(17.0, 15.5, "orange", 3)]
        self.pacman = Pacman(26.0, 13.5) # Center of Second Last Row
        self.total = self.getCount()
        self.ghostScore = 200
        self.levels = [[350, 250], [150, 450], [150, 450], [0, 600]]
        random.shuffle(self.levels)
        # Level index and Level Progress
        self.ghostStates = [[1, 0], [0, 0], [1, 0], [0, 0]]
        index = 0
        for state in self.ghostStates:
            state[0] = randrange(2)
            state[1] = randrange(self.levels[index][state[0]] + 1)
            index += 1
        self.collected = 0
        self.started = False
        self.gameOver = False
        self.gameOverCounter = 0
        self.points = []
        self.pointsTimer = 10
        self.intermission = False
        
        # Berry Spawn Time, Berry Death Time, Berry Eaten
        self.berryState = [200, 400, False]
        self.berryLocation = [20.0, 13.5]
        self.berries = ["element080.png", "element081.png", "element082.png", "element083.png", "element084.png", "element085.png", "element086.png", "element087.png"]
        self.berriesCollected = []
        self.levelTimer = 0
        self.berryScore = 100
        self.lockedInTimer = 100
        self.lockedIn = True
        self.extraLifeGiven = False
        self.musicPlaying = 0

    # Driver method: The games primary update method
    def update(self):
        # pygame.image.unload()
        print(self.ghostStates)
        if self.gameOver:
            self.gameOverFunc()
            return
        
        if self.paused or not self.started and onLaunchScreen:
            self.drawTilesAround(21, 10)
            self.drawTilesAround(21, 11)
            self.drawTilesAround(21, 12)
            self.drawTilesAround(21, 13)
            self.drawTilesAround(21, 14)
            self.drawReady() 
            pygame.display.update()
            return

        
        
        self.levelTimer += 1
        self.ghostUpdateCount += 1
        self.pacmanUpdateCount += 1
        self.tictakChangeCount += 1
        self.ghostsAttacked = False

        if self.score >= 10000 and not self.extraLifeGiven:
            self.lives += 1
            self.extraLifeGiven = True
            self.forcePlayMusic("pacman_extrapac.wav")

        # Draw tiles around ghosts and pacman
        self.clearBoard()
        for ghost in self.ghosts:
            if ghost.attacked:
                self.ghostsAttacked = True

        # Check if the ghost should chase pacman
        index = 0
        for state in self.ghostStates:
            state[1] += 1
            if state[1] >= self.levels[index][state[0]]:
                state[1] = 0
                state[0] += 1
                state[0] %= 2
            index += 1

        index = 0
        for ghost in self.ghosts:
            if not ghost.attacked and not ghost.dead and self.ghostStates[index][0] == 0:
                ghost.target = [self.pacman.row, self.pacman.col]
            index += 1

        if self.levelTimer == self.lockedInTimer:
            self.lockedIn = False

        self.checkSurroundings
        if self.ghostUpdateCount == self.ghostUpdateDelay:
            for ghost in self.ghosts:
                ghost.update()
            self.ghostUpdateCount = 0

        if self.tictakChangeCount == self.tictakChangeDelay:
            #Changes the color of special Tic-Taks
            self.flipColor()
            self.tictakChangeCount = 0

        if self.pacmanUpdateCount == self.pacmanUpdateDelay:
            self.pacmanUpdateCount = 0
            self.pacman.update()
            self.pacman.col %= len(gameBoard[0])
            if self.pacman.row % 1.0 == 0 and self.pacman.col % 1.0 == 0:
                if gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 2:
                    self.playMusic("munch_1.wav")
                    gameBoard[int(self.pacman.row)][int(self.pacman.col)] = 1
                    self.score += 10
                    self.collected += 1
                    # Fill tile with black
                    pygame.draw.rect(screen, (0, 0, 0), (self.pacman.col * tile, self.pacman.row * tile, tile, tile))
                elif gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 5 or gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 6:
                    self.forcePlayMusic("power_pellet.wav")
                    gameBoard[int(self.pacman.row)][int(self.pacman.col)] = 1
                    self.collected += 1
                    # Fill tile with black
                    pygame.draw.rect(screen, (0, 0, 0), (self.pacman.col * tile, self.pacman.row * tile, tile, tile))
                    self.score += 50
                    self.ghostScore = 200
                    for ghost in self.ghosts:
                        ghost.attackedCount = 0
                        ghost.setAttacked(True)
                        ghost.setTarget()
                        self.ghostsAttacked = True
        self.checkSurroundings()
        self.highScore = max(self.score, self.highScore)

        global running
        if self.collected == self.total:
            self.forcePlayMusic("credit.wav")
            for ghost in self.ghosts:
                ghost.draw()
            self.drawTilesAround(self.pacman.row, self.pacman.col)
            pacmanImage = pygame.image.load(ElementPath + "element112.png")
            pacmanImage = pygame.transform.scale(pacmanImage, (int(tile * 1.5), int(tile * 1.5)))
            
            # screen.blit(source, destination)
            # The first argument is pacmanImage, which is the image that we want to draw
            # The second argument is a tuple containing position and size of the pacmanImage (x, y, width (pixel), height(pixel))
            screen.blit(pacmanImage, ((self.pacman.col * tile) + spriteOffset, self.pacman.row * tile + spriteOffset, tile, tile)) 

        # Draws new image
            
            pygame.display.update()
            pygame.time.wait(1500)
            self.intermission = True
            # Blink board from white to blues
            blinkDuration = 2000  # Total duration of blinking
            blinkInterval = 200   # Time interval for each blink
            startTime = pygame.time.get_ticks()
            while pygame.time.get_ticks() - startTime < blinkDuration:
                self.renderIntermission()
                pygame.display.update()
                pygame.time.wait(blinkInterval // 2)
                
                self.render()
                pygame.display.update()
                pygame.time.wait(blinkInterval // 2)
            self.intermission = False
            
            pygame.time.wait(1500)

            print("New Level")
            self.forcePlayMusic("intermission.wav")
            self.level += 1
            self.newLevel()

        if self.level - 1 == 8: #(self.levels[0][0] + self.levels[0][1]) // 50:
            global onExitScreen
            print("You win", self.level, len(self.levels))
            onExitScreen = True
            screen.fill((0, 0, 0))
            currentScreen.displayYouWonMenu()
        else:     
            self.softRender()

    def renderIntermission(self):
        screen.fill((0, 0, 0)) # Create a black screen
        # Draw map
        currentTile = 0
        self.displayLives()
        self.displayScore()
        for i in range(3, len(gameBoard) - 2):
            for j in range(len(gameBoard[0])):
                if gameBoard[i][j] == 3: # Draw wall
                    imageName = str(currentTile)
                    if len(imageName) == 1:
                        imageName = "00" + imageName
                    elif len(imageName) == 2:
                         imageName = "0" + imageName
                    # Get image of desired tile
                    imageName = "intermission" + imageName + ".png"
                    tileImage = pygame.image.load(IntermissionPath + imageName)
                    tileImage = pygame.transform.scale(tileImage, (tile, tile)) # scale each tile image from 70x70 to 25x25


                    screen.blit(tileImage, (j * tile, i * tile, tile, tile))
                currentTile += 1
        pacmanImage = pygame.image.load(ElementPath + "element112.png")
        pacmanImage = pygame.transform.scale(pacmanImage, (int(tile * 1.5), int(tile * 1.5)))
        screen.blit(pacmanImage, (self.pacman.col * tile + spriteOffset, self.pacman.row * tile + spriteOffset, tile, tile))    
        pygame.display.update()
        
        
    # Render method
    def render(self):
        screen.fill((0, 0, 0))  # Create a black screen
        # Draw map
        currentTile = 0
        self.displayLives()
        self.displayScore()
        for i in range(3, len(gameBoard) - 2):
            for j in range(len(gameBoard[0])):
                if gameBoard[i][j] == 3:  # Draw wall
                    imageName = str(currentTile)
                    if len(imageName) == 1:
                        imageName = "00" + imageName
                    elif len(imageName) == 2:
                        imageName = "0" + imageName
                    # Get image of desired tile
                    imageName = "map" + imageName + ".png"
                    tileImage = pygame.image.load(BoardPath + imageName)
                    tileImage = pygame.transform.scale(tileImage, (tile, tile))  # scale each tile image from 70x70 to 25x25

                    # Display image of tile
                    screen.blit(tileImage, (j * tile, i * tile, tile, tile))

                    # pygame.draw.rect(screen, (0, 0, 255),(j * tile, i * tile, tile, tile))  # (x, y, width, height)
                elif gameBoard[i][j] == 2 and not self.intermission:  # Draw Tic-Tak
                    pygame.draw.circle(screen, pelletColor, (j * tile + tile // 2, i * tile + tile // 2), tile // 4)
                elif gameBoard[i][j] == 5 and not self.intermission:  # Draw Special Tik-Tak
                    pygame.draw.circle(screen, pelletColor, (j * tile + tile // 2, i * tile + tile // 2), tile // 2)
                elif gameBoard[i][j] == 6 and not self.intermission:  # Black Special Tik-Tak
                    pygame.draw.circle(screen, (0, 0, 0), (j * tile + tile // 2, i * tile + tile // 2), tile // 2)

                currentTile += 1
        # Draw Sprites
        if not self.intermission:
            for ghost in self.ghosts:
                ghost.draw()
        # Updates the screen
        if self.intermission:
            pacmanImage = pygame.image.load(ElementPath + "element112.png")
            pacmanImage = pygame.transform.scale(pacmanImage, (int(tile * 1.5), int(tile * 1.5)))
            screen.blit(pacmanImage, (self.pacman.col * tile + spriteOffset, self.pacman.row * tile + spriteOffset, tile, tile))  
        else:
            self.pacman.draw()
        pygame.display.update()



    def softRender(self):
        pointsToDraw = []
        for point in self.points:
            if point[3] < self.pointsTimer:
                pointsToDraw.append([point[2], point[0], point[1]])
                point[3] += 1
            else:
                self.points.remove(point)
                self.drawTilesAround(point[0], point[1])

        for point in pointsToDraw:
            self.drawPoints(point[0], point[1], point[2])

        # Draw Sprites
        for ghost in self.ghosts:
            ghost.draw()
        self.pacman.draw()
        self.displayScore()
        self.displayBerries()
        self.displayLives()
        # for point in pointsToDraw:
        #     self.drawPoints(point[0], point[1], point[2])
        self.drawBerry()
        # Updates the screen
        pygame.display.update()

    def playMusic(self, music):
        # return False # Uncomment to disable music
        global musicPlaying
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.unload()
            pygame.mixer.music.load(MusicPath + music)
            pygame.mixer.music.queue(MusicPath + music)
            pygame.mixer.music.play()
            if music == "munch_1.wav":
                musicPlaying = 0
            elif music == "siren_1.wav":
                musicPlaying = 2
            else:
                musicPlaying = 1

    def forcePlayMusic(self, music):
        # return False # Uncomment to disable music
        pygame.mixer.music.unload()
        pygame.mixer.music.load(MusicPath + music)
        pygame.mixer.music.play()
        global musicPlaying
        musicPlaying = 1

    def clearBoard(self):
            # Draw tiles around ghosts and pacman
            for ghost in self.ghosts:
                self.drawTilesAround(ghost.row, ghost.col)
            self.drawTilesAround(self.pacman.row, self.pacman.col)
            self.drawTilesAround(self.berryLocation[0], self.berryLocation[1])
            # Clears Ready! Label
            self.drawTilesAround(20, 10)
            self.drawTilesAround(20, 11)
            self.drawTilesAround(20, 12)
            self.drawTilesAround(20, 13)
            self.drawTilesAround(20, 14)

    def checkSurroundings(self):
        # Check if pacman got killed
        for ghost in self.ghosts:
            if self.touchingPacman(ghost.row, ghost.col) and not ghost.attacked:
                
                if self.lives == 1:
                    print("Game Over") 
                    self.forcePlayMusic("death_1.wav")
                    self.gameOver = True
                    # Remove the ghosts from the screen
                    for ghost in self.ghosts:
                        self.drawTilesAround(ghost.row, ghost.col)
                    self.drawTilesAround(self.pacman.row, self.pacman.col)
                    self.pacman.draw()
                    pygame.display.update()
                    pause(10000000)
                    return
                
                self.started = False
                self.forcePlayMusic("pacman_death.wav")
                reset()
            elif self.touchingPacman(ghost.row, ghost.col) and ghost.isAttacked() and not ghost.isDead():
                ghost.setDead(True)
                ghost.setTarget()
                ghost.ghostSpeed = 1
                ghost.row = math.floor(ghost.row)
                ghost.col = math.floor(ghost.col)
                self.score += self.ghostScore
                self.points.append([ghost.row, ghost.col, self.ghostScore, 0])
                self.ghostScore *= 2
                self.forcePlayMusic("eat_ghost.wav")
                pause(10000000)
        if self.touchingPacman(self.berryLocation[0], self.berryLocation[1]) and not self.berryState[2] and self.levelTimer in range(self.berryState[0], self.berryState[1]):
            self.berryState[2] = True
            self.score += self.berryScore
            self.points.append([self.berryLocation[0], self.berryLocation[1], self.berryScore, 0])
            self.berriesCollected.append(self.berries[(self.level - 1) % 8])
            self.forcePlayMusic("eat_fruit.wav")
    # Displays the current score
    def displayScore(self):
        textOneUp = ["text033.png", "text021.png", "text016.png"]
        textHighScore = ["text007.png", "text008.png", "text006.png", "text007.png", "text015.png", "text019.png", "text002.png", "text014.png", "text018.png", "text004.png"]
        index = 0
        scoreStart = 4
        highScoreStart = 11
        for i in range(scoreStart, scoreStart+len(textOneUp)):
            tileImage = pygame.image.load(TextPath + textOneUp[index])
            tileImage = pygame.transform.scale(tileImage, (tile, tile))
            screen.blit(tileImage, (i * tile, 4, tile, tile))
            index += 1
        score = str(self.score)
        if score == "0":
            score = "00"
        index = 0
        for i in range(0, len(score)):
            digit = int(score[i])
            tileImage = pygame.image.load(TextPath + "text0" + str(32 + digit) + ".png")
            tileImage = pygame.transform.scale(tileImage, (tile, tile))
            screen.blit(tileImage, ((scoreStart + 2 + index) * tile, tile + 4, tile, tile))
            index += 1

        index = 0
        for i in range(highScoreStart, highScoreStart+len(textHighScore)):
            tileImage = pygame.image.load(TextPath + textHighScore[index])
            tileImage = pygame.transform.scale(tileImage, (tile, tile))
            screen.blit(tileImage, (i * tile, 4, tile, tile))
            index += 1

        highScore = str(self.highScore)
        if highScore == "0":
            highScore = "00"
        index = 0
        for i in range(0, len(highScore)):
            digit = int(highScore[i])
            tileImage = pygame.image.load(TextPath + "text0" + str(32 + digit) + ".png")
            tileImage = pygame.transform.scale(tileImage, (tile, tile))
            screen.blit(tileImage, ((highScoreStart + 6 + index) * tile, tile + 4, tile, tile))
            index += 1

    def drawBerry(self):
        if self.levelTimer in range(self.berryState[0], self.berryState[1]) and not self.berryState[2]:
            # print("here")
            berryImage = pygame.image.load(ElementPath + self.berries[(self.level - 1) % 8])
            berryImage = pygame.transform.scale(berryImage, (int(tile * 1.5), int(tile * 1.5)))
            screen.blit(berryImage, (self.berryLocation[1] * tile, self.berryLocation[0] * tile, tile, tile))

    def drawPoints(self, points, row, col):
        pointStr = str(points)
        index = 0
        for i in range(len(pointStr)):
            digit = int(pointStr[i])
            tileImage = pygame.image.load(TextPath + "text" + str(224 + digit) + ".png")
            tileImage = pygame.transform.scale(tileImage, (tile//2, tile//2))
            screen.blit(tileImage, ((col) * tile + (tile//2 * index), row * tile - 20, tile//2, tile//2))
            index += 1

    def drawReady(self):
        ready = ["text274.png", "text260.png", "text256.png", "text259.png", "text281.png", "text283.png"]
        for i in range(len(ready)):
            char = pygame.image.load(TextPath + ready[i])
            char = pygame.transform.scale(char, (int(tile), int(tile)))
            screen.blit(char, ((11 + i) * tile, 20 * tile, tile, tile))
    
    def gameOverFunc(self):
        global running, onExitScreen
        
        if self.gameOverCounter == 12:
            pygame.time.wait(2000)
            self.recordHighScore()
            screen.fill((0, 0, 0))
            onExitScreen = True
            currentScreen.displayGameOverMenu()
 
            return

        # Resets the screen around pacman
        
        for ghost in self.ghosts:
            self.drawTilesAround(ghost.row, ghost.col)
        self.drawTilesAround(self.pacman.row, self.pacman.col)
        self.pacman.draw() 
        self.drawTilesAround(self.pacman.row, self.pacman.col)

        # Draws new image
        pacmanImage = pygame.image.load(ElementPath + "element" + str(116 + self.gameOverCounter) + ".png")
        pacmanImage = pygame.transform.scale(pacmanImage, (int(tile * 1.5), int(tile * 1.5)))
        screen.blit(pacmanImage, (self.pacman.col * tile + spriteOffset, self.pacman.row * tile + spriteOffset, tile, tile))
        pygame.display.update()
        
        
        pause(5000000)
        self.gameOverCounter += 1
        

    def displayLives(self):
        livesLoc = [[34, 1], [34, 3], [34, 5]]
        for i in range(self.lives - 1):
            lifeImage = pygame.image.load(ElementPath + "element054.png")
            lifeImage = pygame.transform.scale(lifeImage, (int(tile * 1.5), int(tile * 1.5)))
            screen.blit(lifeImage, (livesLoc[i][1] * tile, livesLoc[i][0] * tile - spriteOffset, tile, tile))

    def displayBerries(self):
        firstBerrie = [34, 26]
        for i in range(len(self.berriesCollected)):
            berrieImage = pygame.image.load(ElementPath + self.berriesCollected[i])
            berrieImage = pygame.transform.scale(berrieImage, (int(tile * 1.5), int(tile * 1.5)))
            screen.blit(berrieImage, ((firstBerrie[1] - (2*i)) * tile, firstBerrie[0] * tile + 5, tile, tile))

    def touchingPacman(self, row, col):
        if row - 0.5 <= self.pacman.row and row >= self.pacman.row and col == self.pacman.col:
            return True
        elif row + 0.5 >= self.pacman.row and row <= self.pacman.row and col == self.pacman.col:
            return True
        elif row == self.pacman.row and col - 0.5 <= self.pacman.col and col >= self.pacman.col:
            return True
        elif row == self.pacman.row and col + 0.5 >= self.pacman.col and col <= self.pacman.col:
            return True
        elif row == self.pacman.row and col == self.pacman.col:
            return True
        return False

    def newLevel(self):
        reset()
        if self.lives == 1:
            self.lives 
        self.lives += 1
        self.collected = 0
        self.started = False
        self.berryState = [200, 400, False]
        self.levelTimer = 0
        self.lockedIn = True
        for level in self.levels:
            level[0] = min((level[0] + level[1]) - 100, level[0] + 50)
            level[1] = max(100, level[1] - 50)
        random.shuffle(self.levels)
        index = 0
        for state in self.ghostStates:
            state[0] = randrange(2)
            state[1] = randrange(self.levels[index][state[0]] + 1)
            index += 1
        global gameBoard
        gameBoard = copy.deepcopy(boardPattern)
        self.render()

    def drawTilesAround(self, row, col):
        row = math.floor(row)
        col = math.floor(col)
        for i in range(row-2, row+3):
            for j in range(col-2, col+3):
                if i >= 3 and i < len(gameBoard) - 2 and j >= 0 and j < len(gameBoard[0]):
                    imageName = str(((i - 3) * len(gameBoard[0])) + j)
                    if len(imageName) == 1:
                        imageName = "00" + imageName
                    elif len(imageName) == 2:
                         imageName = "0" + imageName
                    # Get image of desired tile
                    imageName = "map" + imageName + ".png"
                    tileImage = pygame.image.load(BoardPath + imageName)
                    tileImage = pygame.transform.scale(tileImage, (tile, tile))
                    # Display image of tile
                    screen.blit(tileImage, (j * tile, i * tile, tile, tile))

                    if gameBoard[i][j] == 2: # Draw Tic-Tak
                        pygame.draw.circle(screen, pelletColor,(j * tile + tile//2, i * tile + tile//2), tile//4)
                    elif gameBoard[i][j] == 5: #Draw Special Tic-Tak
                        pygame.draw.circle(screen, pelletColor,(j * tile + tile//2, i * tile + tile//2), tile//2)
                    elif gameBoard[i][j] == 6: #Black Special Tic-Tak
                        pygame.draw.circle(screen, (0, 0, 0),(j * tile + tile//2, i * tile + tile//2), tile//2)

    # Flips Color of Special Tic-Taks
    def flipColor(self):
        global gameBoard
        for i in range(3, len(gameBoard) - 2):
            for j in range(len(gameBoard[0])):
                if gameBoard[i][j] == 5:
                    gameBoard[i][j] = 6
                    pygame.draw.circle(screen, (0, 0, 0),(j * tile + tile//2, i * tile + tile//2), tile//2)
                elif gameBoard[i][j] == 6:
                    gameBoard[i][j] = 5
                    pygame.draw.circle(screen, (pelletColor),(j * tile + tile//2, i * tile + tile//2), tile//2)

    def getCount(self):
        total = 0
        for i in range(3, len(gameBoard) - 2):
            for j in range(len(gameBoard[0])):
                if gameBoard[i][j] == 2 or gameBoard[i][j] == 5 or gameBoard[i][j] == 6:
                    total += 1
        return total

    def getHighScore(self):
        file = open(DataPath + "HighScore.txt", "r")
        highScore = int(file.read())
        file.close()
        return highScore

    def recordHighScore(self):
        file = open(DataPath + "HighScore.txt", "w").close()
        file = open(DataPath + "HighScore.txt", "w+")
        file.write(str(self.highScore))
        file.close()
        
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
        self.rest = True

    def update(self):
        if self.newDir == 0:
            if canMove(math.floor(self.row - self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 1:
            if canMove(self.row, math.ceil(self.col + self.pacSpeed)) and self.row % 1.0 == 0:
                self.col += self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 2:
            if canMove(math.ceil(self.row + self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 3:
            if canMove(self.row, math.floor(self.col - self.pacSpeed)) and self.row % 1.0 == 0:
                self.col -= self.pacSpeed
                self.dir = self.newDir
                return

        if self.dir == 0:
            if canMove(math.floor(self.row - self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.pacSpeed
        elif self.dir == 1:
            if canMove(self.row, math.ceil(self.col + self.pacSpeed)) and self.row % 1.0 == 0:
                self.col += self.pacSpeed
        elif self.dir == 2:
            if canMove(math.ceil(self.row + self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.pacSpeed
        elif self.dir == 3:
            if canMove(self.row, math.floor(self.col - self.pacSpeed)) and self.row % 1.0 == 0:
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
        ghostImage = pygame.image.load(ElementPath + "element152.png")
        currentDir = ((self.dir + 3) % 4) * 2
        if self.changeFeetCount == self.changeFeetDelay:
            self.changeFeetCount = 0
            currentDir += 1
        self.changeFeetCount += 1
        if self.dead:
            tileNum = 152 + currentDir
            ghostImage = pygame.image.load(ElementPath + "element" + str(tileNum) + ".png")
        elif self.attacked:
            if self.attackedTimer - self.attackedCount < self.attackedTimer//3:
                if (self.attackedTimer - self.attackedCount) % 31 < 26:
                    ghostImage = pygame.image.load(ElementPath + "element0" + str(70 + (currentDir - (((self.dir + 3) % 4) * 2))) + ".png")
                else:
                    ghostImage = pygame.image.load(ElementPath + "element0" + str(72 + (currentDir - (((self.dir + 3) % 4) * 2))) + ".png")
            else:
                ghostImage = pygame.image.load(ElementPath + "element0" + str(72 + (currentDir - (((self.dir + 3) % 4) * 2))) + ".png")
        else:
            if self.color == "blue":
                tileNum = 136 + currentDir
                ghostImage = pygame.image.load(ElementPath + "element" + str(tileNum) + ".png")
            elif self.color == "pink":
                tileNum = 128 + currentDir
                ghostImage = pygame.image.load(ElementPath + "element" + str(tileNum) + ".png")
            elif self.color == "orange":
                tileNum = 144 + currentDir
                ghostImage = pygame.image.load(ElementPath + "element" + str(tileNum) + ".png")
            elif self.color == "red":
                tileNum = 96 + currentDir
                if tileNum < 100:
                    ghostImage = pygame.image.load(ElementPath + "element0" + str(tileNum) + ".png")
                else:
                    ghostImage = pygame.image.load(ElementPath + "element" + str(tileNum) + ".png")

        ghostImage = pygame.transform.scale(ghostImage, (int(tile * 1.5), int(tile * 1.5)))
        screen.blit(ghostImage, (self.col * tile + spriteOffset, self.row * tile + spriteOffset, tile, tile))

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

game = Game(1, 0)
ghostsafeArea = [15, 13] # The location the ghosts escape to when attacked
ghostGate = [[15, 13], [15, 14]]

def canMove(row, col):
    if col == -1 or col == len(gameBoard[0]):
        return True
    if gameBoard[int(row)][int(col)] != 3:
        return True
    return False

# Reset after death
def reset():
    global game
    game.ghosts = [Ghost(14.0, 13.5, "red", 0), Ghost(17.0, 11.5, "blue", 1), Ghost(17.0, 13.5, "pink", 2), Ghost(17.0, 15.5, "orange", 3)]
    for ghost in game.ghosts:
        ghost.setTarget()
    game.pacman = Pacman(26.0, 13.5)
    game.lives -= 1
    game.paused = True
    game.render()

def hardReset():
    global game, gameBoard
    game.ghosts = [Ghost(14.0, 13.5, "red", 0), Ghost(17.0, 11.5, "blue", 1), Ghost(17.0, 13.5, "pink", 2), Ghost(17.0, 15.5, "orange", 3)]
    for ghost in game.ghosts:
        ghost.setTarget()
    game.pacman = Pacman(26.0, 13.5)
    game.lives += 2
    game.paused = True
    game.collected = 0
    game.score = 0
    game.gameOverCounter = 0
    gameBoard = copy.deepcopy(boardPattern)
    game.render()



currentScreen = displayMenu()
currentScreen.displayLaunchMenu()
running = True
onLaunchScreen = True
onExitScreen = False

clock = pygame.time.Clock()

def pause(time):
    cur = 0
    while not cur == time:
        cur += 1

while running:
    clock.tick(40)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            game.recordHighScore()
        elif event.type == pygame.KEYDOWN:
            game.paused = False
            game.started = True
            if event.key in COMMAND_KEYS["UP"]:
                if not onLaunchScreen and not onExitScreen:
                    game.pacman.newDir = 0
            elif event.key in COMMAND_KEYS["RIGHT"]:
                if not onLaunchScreen and not onExitScreen:
                    game.pacman.newDir = 1
            elif event.key in COMMAND_KEYS["DOWN"]:
                if not onLaunchScreen and not onExitScreen:
                    game.pacman.newDir = 2
            elif event.key in COMMAND_KEYS["LEFT"]:
                if not onLaunchScreen and not onExitScreen:
                    game.pacman.newDir = 3
            elif event.key == pygame.K_SPACE:
                if onLaunchScreen:
                    onLaunchScreen = False
                    game.paused = True
                    game.started = False
                    game.render()
                    pygame.mixer.music.load(MusicPath + "pacman_beginning.wav")
                    pygame.mixer.music.play()
                    musicPlaying = 1
                elif onExitScreen:
                    onExitScreen = False
                    game.paused = True
                    game.started = False
                    game.render()
                    game.gameOver = False
                    hardReset()
                    pygame.mixer.music.load(MusicPath + "pacman_beginning.wav")
                    musicPlaying = 1
                    pygame.mixer.music.play()
            elif event.key == pygame.K_ESCAPE:
                running = False
                game.recordHighScore()                                                                                

    if not onLaunchScreen and not onExitScreen:
        game.update()
