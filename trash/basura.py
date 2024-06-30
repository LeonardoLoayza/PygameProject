# importando librerias
import pygame 
from pygame.locals import * 

pygame.init() 

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000
 
screen = pygame.display.set_mode((screen_width, screen_height))

tile_size = 50
game_over = 0 
main_menu = True

# Cargar las imagenes
restart_img = pygame.image.load('img/restart_btn.png')
bg_img = pygame.transform.scale(pygame.image.load("img2/atardcerme_0.jpg"), (screen_height, screen_width))
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

class Button():
  def __init__(self, x, y, image):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.clicked = False
    
  def draw(self):
    # PARAAAAAAAAAAAAAAAAAAAAA QUE SIRVE ACTION ?
    action = False
    # Posicion de mouse 
    pos = pygame.mouse.get_pos()
    # collidepoint nos permite saber si el cursor esta sobre el objeto button
    if self.rect.collidepoint(pos):
      # Revisar si hacemos click izquierdo
      if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
        action = True 
        self.clicked = True

    if pygame.mouse.get_pressed()[0] == 0:
      self.clicked = False  
            
    screen.blit(self.image, self.rect)
    return action 

# Todo: Mover clase a otro file
class Player(): 
  def __init__(self, x,y):
    self.reset(x, y)
    
  def update(self, game_over):
    dx = 0
    dy = 0
    # walk_cooldown, index y counter los usaremos para animaciones 
    walk_cooldown = 5
    
    if game_over == 0:  
      # Mecanica de saltar, movimiento
      key = pygame.key.get_pressed()
      # Prevenir que pueda saltar infinitas veces com la tecla apretada
      if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
        self.vel_y = -15
        self.jumped = True
      if key[pygame.K_SPACE] == False:
        self.jumped = False 
      # Cada tic se incrementa el counter y se actualiza la posicion del personaje
      # A que lado va (izquierda o derecha)
      if key[pygame.K_LEFT]:
        dx -= 5
        self.counter += 1
        self.direction = -1
      if key[pygame.K_RIGHT]:
        dx += 5   
        self.counter += 1
        self.direction = 1
      # Cuando se para, se pone la animacion inicial (IDLE)
      if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
        self.index = 0 
        self.counter = 0 
        # Revisar que lado el personaje esta viendo y cargar los sprites
        if self.direction == 1: 
          self.image = self.images_right[self.index]
        if self.direction == -1:
          self.image = self.images_left[self.index]

      # Animacion 
      # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
      # Counter aumenta cada vez que apretamos el key de movimiento
      # Luego actualizamos la 
      if self.counter > walk_cooldown:
        self.counter = 0
        self.index += 1
        if self.index >= len(self.images_right):
          self.index = 0
        if self.direction == 1: 
          self.image = self.images_right[self.index]
        if self.direction == -1:
          self.image = self.images_left[self.index]

      # Gravedad, no exceder 10   
      self.vel_y += 1
      if self.vel_y > 10:
        self.vel_y = 10 
      dy += self.vel_y 
      
      # Verificar colision
      self.in_air = True
      for tile in world.tile_list: 
        # Colision en X
        if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
          dx = 0
        
        # Si colisiona con algo en Y 
        if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
          # Verificar si esta debajo del suelo, saltar
          if self.vel_y < 0: 
            dy = tile[1].bottom - self.rect.top
            self.vel_y = 0 
          # Verificar si esta encima del suelo, caerse
          elif self.vel_y >= 0:
            dy = tile[1].top - self.rect.bottom
            self.vel_y = 0 
            self.in_air = False
            
        
      # Si nuestro objeto Player colisiona con el enemigo
      if pygame.sprite.spritecollide(self, blob_group, False):
        game_over = -1
      
      if pygame.sprite.spritecollide(self, lava_group, False):
        game_over = -1
        
      # Actualizar coordenadas jugador 
      self.rect.x += dx 
      self.rect.y += dy 
      
      # rect.bottom es igual a la maxima altura de la pantalla
      # hacer que dy igual a 0 
      # porque 
      
    elif game_over == -1:
      self.image = self.dead_image
      if self.rect.y > 200:
        self.rect.y -= 5
      
    screen.blit(self.image, self.rect)
    pygame.draw.rect(screen, (255,255,255), self.rect, 6)
    return game_over
  
  def reset(self, x, y):
    self.images_right = [] 
    self.images_left = [] 
    self.index = 0 
    self.counter = 0
    
    # Tengo 4 imagenes para representar los movimientos de caminar
    # Las cargo, escalo y agrego a mi lista de animaciones. 
    for num in range(1,5):
      img_right = pygame.image.load(f'img2/player_{num}.png')
      img_right = pygame.transform.scale(img_right, (40, 80))
      img_left = pygame.transform.flip(img_right, True, False) # Flip eje X 

      self.images_right.append(img_right)
      self.images_left.append(img_left)
      
    self.image = self.images_right[self.index]
    self.dead_image = pygame.image.load('img/ghost.png')
    # define the position and dimensions of the player sprite on the screen
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.width = self.image.get_width()
    self.height = self.image.get_height() 
    self.vel_y = 0
    self.jumped = False
    # 1 derecha, -1 izquierda
    self.direction = 0
    self.in_air = True
    
       
class World():
  def __init__(self, data):
    self.tile_list = []
    
    dirt_img = pygame.image.load('img2/a/estructura_9.png')
    grass_img = pygame.image.load('img2/a/estructura_3.png')
    # se usa row_count y column_count para posicionar bien 
    # los tiles de acuerdo al tile_size y el world_data  
    # se escala con el tile_size
    row_count = 0
    for row in data:
      col_count = 0
      for tile in row:
        if tile == 1:
          img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = col_count * tile_size
          img_rect.y = row_count * tile_size
          tile = (img, img_rect)
          self.tile_list.append(tile)
        if tile == 2:
          img = pygame.transform.scale(grass_img, (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = col_count * tile_size
          img_rect.y = row_count * tile_size
          tile = (img, img_rect)
          self.tile_list.append(tile)
        if tile == 3:
          # Aca acomodo la posicion y de mi enemigo
          blob = Enemy(col_count * tile_size, row_count * tile_size + 5)
          blob_group.add(blob)
        col_count += 1
        if tile == 6:
          lava = Lava(col_count * tile_size - 50, row_count * tile_size) 
          lava_group.add(lava)
        
      row_count += 1
    
  def draw(self): 
    for tile in self.tile_list:
      screen.blit(tile[0],tile[1])
      pygame.draw.rect(screen, (255,255,255), tile[1], 2)
    
class Enemy(pygame.sprite.Sprite): 
  # Nos ayuda a trabajar con grupos, por ejemplo puedo usar un metodo "kill"
  # Y este eliminaria a todas las instancias de la clase. 
  # Esta clase donde hacemos herencia ya tiene metodo: draw y update
  # Asi que solo dibujaran lo que self.image sea cuando llame a metodo draw()
  def __init__(self, x, y):
    # Inicializando el constructor de clase padre
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load('img2/spinner.png')
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.move_direction = 1
    self.move_counter = 0 
    
  def update(self):
    #Todo: Explicar el movimiento de los enemigos
    self.rect.x += self.move_direction 
    self.move_counter += 1
    if abs(self.move_counter) > 50: 
      self.move_direction *= -1 
      self.move_counter *= -1      
    
class Lava(pygame.sprite.Sprite): 
  def __init__(self,x,y):
    pygame.sprite.Sprite.__init__(self)
    img = pygame.image.load('img/lava.png')
    self.image = pygame.transform.scale(img, (tile_size, tile_size))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y


# matriz con la informacion del juego
world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

player = Player(100, screen_height - 130)
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
world = World(world_data)
# Why do I create this blob group ? How to explain ?

# Crear los Botones 
restart_button = Button(screen_width // 2 - 50, screen_height // 2 +100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

run = True 

while run:
  # Insertando componentes del mapa del juego
  clock.tick(fps)
  screen.blit(bg_img, (0,0))
  
  # Main menu inicia true y mostramos el menu
  # Con los botones dibujados, si hacemos click 
  # cambiara la variable run o main_menu
  if main_menu == True: 
    if exit_button.draw():
      run = False
    if start_button.draw():
      main_menu = False
  else: 
    world.draw()
  
    if game_over == 0:
      blob_group.update()
    
    # Con este blob_group llamamos una funcion y esta la aplica a todos 
    # los enemigos, osea no usamos update por cada enemigo en nuestro nivel
    blob_group.update()
    lava_group.draw(screen)
    blob_group.draw(screen)
    
    game_over = player.update(game_over)
    
    if game_over == -1:
      if restart_button.draw():
        player.reset(100, screen_height - 130)
        game_over = 0

  # Evento cerrar juego
  for event in pygame.event.get():
    if event.type == pygame.QUIT: 
      run = False 
      
  pygame.display.update()
      
pygame.quit()
