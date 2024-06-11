import pygame

TextPath = "Assets/Sprites/TextSprites/"
square = 25
spriteRatio = 3/2 
spriteOffset = square * (1 - spriteRatio) * (1/2)
screen = pygame.display.set_mode((700, 900))

class MenuElements:
    def __init__(self):
        self.gameTitle = ["text016.png", "text000.png", "text448.png", "text012.png", "text000.png", "text013.png"]
        self.characterTitle = [
            # Character
            "text002.png", "text007.png", "text000.png", "text018.png", "text000.png", "text002.png", "text020.png", "text004.png", "text018.png",
            # /
            "text015.png", "text042.png", "text015.png",
            # Nickname
            "text013.png", "text008.png", "text002.png", "text010.png", "text013.png", "text000.png", "text012.png", "text004.png"
        ]
        self.characters = [
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
        # Draw Pacman & Ghosts
        self.event = ["text449.png", "text015.png", "text452.png", "text015.png", "text015.png", "text448.png", "text453.png", "text015.png", "text015.png", "text015.png", "text453.png"]
        # Draw Platform Line
        self.wall = ["text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png", "text454.png"]
        # "Duy Pham 2024"     
        self.credit = ["text387.png", "text405.png", "text409.png", "text015.png", "text400.png", "text391.png", "text384.png", "text396.png", "text015.png", "text418.png", "text416.png", "text418.png", "text420.png"]
        # "Press Space to Play"
        self.toplay = ["text016.png", "text018.png", "text004.png", "text019.png", "text019.png", "text015.png", "text019.png", "text016.png", "text000.png", "text002.png", "text004.png", "text015.png", "text020.png", "text014.png", "text015.png", "text016.png", "text011.png", "text000.png", "text025.png"]
        # "Press Enter to Exit"
        self.toexit = ["text016.png", "text018.png", "text004.png", "text019.png", "text019.png", "text015.png", "text004.png", "text013.png", "text020.png", "text004.png", "text018.png", "text015.png", "text020.png", "text014.png", "text015.png", "text004.png", "text024.png", "text008.png", "text020.png"]
        # "Game Over"
        self.gameover = ["text070.png", "text064.png", "text076.png", "text068.png", "text079.png", "text078.png", "text086.png", "text068.png", "text082.png"]
        # "You Won"
        self.youwon = ["text217.png", "text206.png", "text213.png", "text207.png", "text215.png", "text206.png", "text205.png"]
        
    def drawGameTitle(self):
        for i in range(len(self.gameTitle)):
            char = pygame.image.load(TextPath + self.gameTitle[i])
            char = pygame.transform.scale(char, (int(square * 4), int(square * 4)))
            screen.blit(char, ((2 + 4 * i) * square, 2 * square, square, square))

    def drawCharacterTitle(self):
        for i in range(len(self.characterTitle)):
            char = pygame.image.load(TextPath + self.characterTitle[i])
            char = pygame.transform.scale(char, (int(square), int(square)))
            screen.blit(char, ((4 + i) * square, 10 * square, square, square))

    def drawCharactersAndNicknames(self):
        for i in range(len(self.characters)):
            for j in range(len(self.characters[i])):
                if j == 0:
                    char = pygame.image.load(TextPath + self.characters[i][j])
                    char = pygame.transform.scale(char, (int(square * spriteRatio), int(square * spriteRatio)))
                    screen.blit(char, ((2 + j) * square - square//2, (12 + 2 * i) * square - square//3, square, square))
                else:
                    char = pygame.image.load(TextPath + self.characters[i][j])
                    char = pygame.transform.scale(char, (int(square), int(square)))
                    screen.blit(char, ((2 + j) * square, (12 + 2 * i) * square, square, square))

    def drawPacmanAndGhosts(self):
        for i in range(len(self.event)):
            ele = pygame.image.load(TextPath + self.event[i])
            ele = pygame.transform.scale(ele, (int(square * 2), int(square * 2)))
            screen.blit(ele, ((4 + i * 2) * square, 24 * square, square, square))

    def drawPlatformLine(self):
        for i in range(len(self.wall)):
            platform = pygame.image.load(TextPath + self.wall[i])
            platform = pygame.transform.scale(platform, (int(square * 2), int(square * 2)))
            screen.blit(platform, ((i * 2) * square, 26 * square, square, square))

    def drawCredit(self):
        for i in range(len(self.credit)):
            char = pygame.image.load(TextPath + self.credit[i])
            char = pygame.transform.scale(char, (int(square*1.5), int(square*1.5)))
            screen.blit(char, ((4.3 + 1.5 * i) * square, 28.75 * square, square, square))

    def drawGameOver(self):
        for i in range(len(self.gameover)):
            char = pygame.image.load(TextPath + self.gameover[i])
            char = pygame.transform.scale(char, (int(square*1.5), int(square*1.5)))
            screen.blit(char, ((7.25 + 1.5 * i) * square, 28.75 * square, square, square))
    
    def drawYouWon(self):
        for i in range(len(self.youwon)):
            char = pygame.image.load(TextPath + self.youwon[i])
            char = pygame.transform.scale(char, (int(square*1.5), int(square*1.5)))
            screen.blit(char, ((8.5 + 1.5 * i) * square, 28.75 * square, square, square))

    def drawPressToPlay(self):
        for i in range(len(self.toplay)):
                        char = pygame.image.load(TextPath + self.toplay[i])
                        char = pygame.transform.scale(char, (int(square), int(square)))
                        screen.blit(char, ((4.5 + i) * square, 32.5 * square - 10, square, square))
    

    def drawPressToExit(self):
        for i in range(len(self.toexit)):
            char = pygame.image.load(TextPath + self.toexit[i])
            char = pygame.transform.scale(char, (int(square), int(square)))
            screen.blit(char, ((4.5 + i) * square, 35 * square - 10, square, square))

class displayMenu(MenuElements):
    def displayLaunchMenu(self):
        self.drawGameTitle()
        self.drawCharacterTitle()
        self.drawCharactersAndNicknames()
        self.drawPacmanAndGhosts()
        self.drawPlatformLine()
        self.drawCredit()
        self.drawPressToPlay()
        self.drawPressToExit()
        pygame.display.update()  
    def displayGameOverMenu(self):
        self.drawGameTitle()
        self.drawCharacterTitle()
        self.drawCharactersAndNicknames()
        self.drawPacmanAndGhosts()
        self.drawPlatformLine()
        self.drawGameOver()
        self.drawPressToPlay()
        self.drawPressToExit()
        pygame.display.update()  
    def displayYouWonMenu(self):
        self.drawGameTitle()
        self.drawCharacterTitle()
        self.drawCharactersAndNicknames()
        self.drawPacmanAndGhosts()
        self.drawPlatformLine()
        self.drawYouWon()
        self.drawPressToPlay()
        self.drawPressToExit()
        pygame.display.update()  
livesLoc = [[34, 3], [34, 1]] 
print(livesLoc[1][0])