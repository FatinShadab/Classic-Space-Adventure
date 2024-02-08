import sys
import random
import pygame

class Laser:
    # Class variable to keep track of laser instances based on the shooter class
    INSTANCES = dict({})
    
    def __init__(self, color, startingCoords, direction, shooterClass):
        # Initialize laser properties
        self.color = color
        self.startingCoords = startingCoords
        
        # Set velocity based on direction
        if direction > 0:
            self.vel = 5
        else:
            self.vel = -5
        
        # Create a rectangle for the laser
        self.rect = pygame.Rect(*self.startingCoords, 10, 20)
        
        # Add the laser instance to the dictionary of instances based on shooter class
        if shooterClass in Laser.INSTANCES.keys():
            Laser.INSTANCES[shooterClass].append(self)
        else:
            Laser.INSTANCES[shooterClass] = [self]
            
    def move(self):
        # Move the laser vertically based on its velocity
        self.rect.y += self.vel

    def render(self, windowSurface):
        # Draw the laser on the window surface
        pygame.draw.rect(windowSurface, self.color, self.rect)

class Enemy:
    def __init__(self, playGrid):
        # Initialize enemy properties
        self.xRange = (5, playGrid[0]-5)
        self.yRange = (0, playGrid[1])
        
        # Set a random velocity for the enemy
        self.vel = random.choice((0.1, 0.12, 0.14, 0.15, 0.16))
        self.generatedYCoord = random.choice(range(-8, -4, 1))
        
        # Load and scale the enemy image
        self.image = pygame.image.load("resource/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        
        # Set initial coordinates using pygame Vector2
        self.coord = pygame.math.Vector2(random.choice(range(*self.xRange, 5)), self.generatedYCoord)
     
    def auto_move(self):
        # Move the enemy vertically based on its velocity
        self.coord += pygame.math.Vector2(0, self.vel)

    def shoot(self):
        # Create a laser instance when the enemy shoots
        Laser("Red", self.coord*20, 1, Enemy)
    
    def get_solid_rect(self):
        # Define a solid rectangle for collision detection based on the enemy image
        solidRect = self.image.get_rect(topleft=self.coord * 20)
        solidRect.x += 15
        solidRect.y += 70
        solidRect.centery -= 55
        solidRect.width -= 30
        solidRect.height -= 70
        
        return solidRect
    
    def render(self, windowSurface):
        # Draw the enemy image on the window surface
        windowSurface.blit(self.image, self.image.get_rect(topleft=self.coord * 20))

class Ship:
    def __init__(self, playGrid):
        # Initialize player ship properties
        self.xRange = (0, playGrid[0])
        self.yRange = (0, playGrid[1])
        
        # Load and scale the player ship image
        self.image = pygame.image.load("resource/ship.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        
        # Set initial coordinates using pygame Vector2
        self.coord = pygame.math.Vector2(15 , 30)
        self.hp = 100
        
    def move_left(self):
        # Move the player ship left if within the grid boundaries
        if self.coord[0] - 1 > 0:
            self.coord += pygame.math.Vector2(-2, 0)
        
    def move_right(self):
        # Move the player ship right if within the grid boundaries
        if self.coord[0] + 6 < self.xRange[1]:
            self.coord += pygame.math.Vector2(2, 0)
            
    def shoot(self):
        # Create a laser instance when the player ship shoots
        leserCoord = self.coord + pygame.math.Vector2(2.2, -0.5)
        Laser("Purple", leserCoord*20, -1, Ship)
    
    def get_solid_rect(self):
        # Define a solid rectangle for collision detection based on the player ship image
        solidRect = self.image.get_rect(topleft=self.coord * 20)
        solidRect.centery += 50
        solidRect.height -= 80
        
        return solidRect
        
    def render(self, windowSurface):
        # Draw the player ship image on the window surface
        windowSurface.blit(self.image, self.image.get_rect(topleft=(self.coord * 20)))

class Game:
    # Class variables for game-related constants
    TITLE = "Classic Space Adventure"
    VOLUME = 0.85
    MENU_STATE = 0
    PLAY_STATE = 1
    PAUSE_STATE = 2
    
    def __init__(self):
        # Initialize pygame and game-related properties
        pygame.init()
        self.active = True
        self.score = 0
        
        # Set window dimensions and cell size
        self.windowRow = 38
        self.windowCol = 36
        self.cellSize = 20
        
        # Calculate window width and height based on cell size
        self.windowWH = (
            self.windowCol * self.cellSize,
            self.windowRow * self.cellSize
        )
        
        self.width, self.height = self.windowWH
        self.state = Game.MENU_STATE
        
        # Initialize pygame clock and maximum frames per second
        self.clock = pygame.time.Clock()
        self.maxFPS = 60
        
        # List to store enemy instances
        self.enemies = []
        
    def __config_window(self):
        # Configure the game window
        self.mainWindowSurface = pygame.display.set_mode(self.windowWH)
        pygame.display.set_caption(Game.TITLE)

    def __config_font(self):
        # Configure the font for rendering text
        self.font = pygame.font.Font("resource/Pixeltype.ttf", 50)
        self.font.bold = True

    def __config_sound(self):
        # Configure game sounds
        self.collisionSE = pygame.mixer.Sound("resource/enemyPlayerCollision.wav")
        self.laserSE = pygame.mixer.Sound("resource/shoot.wav")
        self.HitSE = pygame.mixer.Sound("resource/bulletCollide.mp3")
        self.bgMusic = pygame.mixer.Sound("resource/Infraction-Battlefield-Logo-Version-2-pr.mp3")
        
        # Set volume for each sound
        self.collisionSE.set_volume(Game.VOLUME)
        self.laserSE.set_volume(Game.VOLUME)
        self.HitSE.set_volume(Game.VOLUME)
        self.bgMusic.set_volume(0.1)

    def __config_game_entities(self):
        # Create player ship instance
        self.player = Ship((self.windowCol, self.windowRow))

    def __reset(self):
        # Reset game state and player properties
        self.player.hp = 100
        self.score = 0
        self.enemies.clear()

    def __clean_up(self):
        # Clean up pygame and exit
        pygame.quit()
        sys.exit()
    
    def __render_menu_scene(self):
        # Render the menu scene with instructions
        pygame.draw.rect(self.mainWindowSurface, "Black", (0, self.height//2 - 150, self.width, self.height/2.5))
        pygame.draw.rect(self.mainWindowSurface, "Blue", (10, self.height//2 - 140, self.width - 20, self.height/2.5 - 20))
        if self.player.hp != 100:
            self.mainWindowSurface.blit(self.font.render("Press Enter To Play Again !", False, "Black"), (150, self.height - 500))
        else:
            self.mainWindowSurface.blit(self.font.render("Press Enter To Play!", False, "Black"), (200, self.height - 500))
            self.mainWindowSurface.blit(self.font.render("Press 'ESC' To Pause", False, "Black"), (200, self.height - 400))
            self.mainWindowSurface.blit(self.font.render("Press 'Arrow KEYS' To Move", False, "Black"), (150, self.height - 350))
            self.mainWindowSurface.blit(self.font.render("Press 'SPACE' To Shoot", False, "Black"), (200, self.height - 300))
    
    def __render_pause_scene(self):
        # Render the pause scene
        pygame.draw.rect(self.mainWindowSurface, "Black", pygame.Rect(15*self.cellSize, 15*self.cellSize, 40, 80))
        pygame.draw.rect(self.mainWindowSurface, "Black", pygame.Rect(18*self.cellSize, 15*self.cellSize, 40, 80))
    
    def __decrease_player_hp(self, amount):
        # Decrease player's health and check for game over
        self.player.hp -= amount
        
        if self.player.hp < 0:
            self.player.hp = 0
            self.state = Game.MENU_STATE
    
    def __check_player_enemy_collision(self):
        # Check for collisions between player and enemies
        for enemy in self.enemies:
            r1 = enemy.get_solid_rect()
            r2 = self.player.get_solid_rect()
            
            if r1.colliderect(r2):
                # Play collision sound, remove enemy, and decrease player's health
                self.collisionSE.play()
                self.enemies.remove(enemy)
                self.__decrease_player_hp(10)

    def __check_leser_enemy_collision(self):
        # Check for collisions between lasers and enemies
        if Ship in Laser.INSTANCES.keys():
            for leser in Laser.INSTANCES[Ship]:
                for enemy in self.enemies:
                    if leser.rect.colliderect(enemy.get_solid_rect()):
                        # Play hit sound, remove enemy and laser, and increase score
                        self.HitSE.play()
                        self.enemies.remove(enemy)
                        Laser.INSTANCES[Ship].remove(leser)
                        self.score += 10
                        break               

    def __generate_enemy_wave(self):
        # Generate a wave of enemies if none exist
        if len(self.enemies) == 0:
            for i in range(1, random.randint(5, 10)):
                self.enemies.append(Enemy((self.windowCol, self.windowRow)))
    
    def __update_game_world(self):
        # Update positions of enemies and lasers, and check for out-of-bounds enemies
        for enemy in self.enemies:
            enemy.auto_move()
            if enemy.coord[1] > self.windowRow + 5:
                # Remove enemies that are out of bounds and decrease player's health
                self.enemies.remove(enemy)
                self.__decrease_player_hp(5)
        
        for key, lesers in Laser.INSTANCES.items():
            for leser in lesers:
                leser.move()
                if self.height < leser.rect.y < 0:
                    # Remove lasers that are out of bounds
                    Laser.INSTANCES[key].remove(leser)
        
    def __activate_gameloop(self):
        # Activate the game loop
        self.bgMusic.play(-1)  # -1 for infinite loop
        while self.active:
            # Input processing and update caused by user input part
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.active = False
                if event.type == pygame.KEYDOWN:
                    if self.state == Game.MENU_STATE:
                        if event.key == pygame.K_RETURN:
                            # Start or restart the game when Enter is pressed
                            self.state = Game.PLAY_STATE
                            self.__reset()
                    if self.state == Game.PLAY_STATE:
                        # Handle player controls during gameplay
                        if event.key == pygame.K_LEFT:
                            self.player.move_left()
                        if event.key == pygame.K_RIGHT:
                            self.player.move_right()
                        if event.key == pygame.K_SPACE:
                            # Play laser sound and make the player ship shoot
                            self.laserSE.play()
                            self.player.shoot()
                    if event.key == pygame.K_ESCAPE and self.state != Game.MENU_STATE:
                        # Toggle between pause and play states when Escape is pressed
                        self.state = Game.PAUSE_STATE if self.state != Game.PAUSE_STATE else Game.PLAY_STATE
                
            # Game Logic Update Part
            if self.state == Game.PLAY_STATE:
                self.__generate_enemy_wave()
                self.__update_game_world()
                self.__check_leser_enemy_collision()
                self.__check_player_enemy_collision()

            # Render Part
            self.mainWindowSurface.fill("Blue")

            # Draw enemies on the window surface
            [enemy.render(self.mainWindowSurface) for enemy in self.enemies] 
            
            # Draw player ship on the window surface
            self.player.render(self.mainWindowSurface)
            
            # Draw lasers on the window surface
            for lesers in Laser.INSTANCES.values():
                for leser in lesers:
                    leser.render(self.mainWindowSurface)
                    
            # Display player's health and score
            self.mainWindowSurface.blit(self.font.render(f"HP : {self.player.hp}", False, "Black"), (10, 10, 100, 100))
            self.mainWindowSurface.blit(self.font.render(f"Score : {self.score}", False, "Black"), (26 * self.cellSize, 10, 100, 100))
            
            # Display menu or pause scenes based on game state
            if self.state == Game.MENU_STATE:
                self.__render_menu_scene()
            if self.state == Game.PAUSE_STATE:
                self.__render_pause_scene()

            pygame.display.flip()
            pygame.display.update()
        
            self.clock.tick(self.maxFPS)

        # Clean up and exit the game
        self.__clean_up()

    def run(self):
        # Run the game
        self.__config_window()
        self.__config_font()
        self.__config_sound()
        self.__config_game_entities()
        self.__activate_gameloop()


if __name__ == "__main__":
    # Run the game when the script is executed
    Game().run()
