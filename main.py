import pygame
from pygame.locals import *
from pygame import mixer # Reproducir sonido en el juego
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('JuegoFinal')


# Tipo de letra
font = pygame.font.SysFont('Lucida Console', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)


# Variables del juego 
tile_size = 50
game_over = 0 # 1, 0, -1
main_menu = True
level = 0
max_levels = 8
score = 0
white = (255, 255, 255)
blue = (0, 0, 255)


# Imagenes del juego
bg_img = pygame.transform.scale(pygame.image.load("img2/spacebg.png"), (screen_height, screen_width))
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')


# Sonido usando mixer y archivos wav
pygame.mixer.music.load('img/mgk-dontletmego.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('img/get_coin.wav')
coin_fx.set_volume(0.6)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.6)
game_over_fx = pygame.mixer.Sound('img/gameover_piano.wav')
game_over_fx.set_volume(2)

# Renderizar texto en el juego (Ganaste, perdiste)
def draw_game_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


# Poner las variables en el estado inicial o vacio
def reset_level(level):
	player.reset(100, screen_height - 130)
	spinner_enemy_group.empty()
	moving_platform_group.empty()
	apple_group.empty()
	lava_group.empty()
	exit_group.empty()

	# Cargar archivo en binario (Eficiencia, compatibilidad, seguridad)
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)
	
  # Imagen referencial de nuestras manzanas
	apple_score = Apple(tile_size // 2, tile_size // 2)
	apple_group.add(apple_score)
	
	return world


class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		# Posicion del mouse
		pos = pygame.mouse.get_pos()

		# Colision del cursor con boton, evento click
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:  # Solo una vez hacer click
				action = True
				self.clicked = True

		# Reseteamos atributo click para que funcione posteriormente
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		# Poner boton en el juego
		screen.blit(self.image, self.rect)

		return action



class Player():
	def __init__(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1,5):
			img_right = pygame.image.load(f'img2/player_{num}.png')
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False) # Flip eje X 

			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('img/ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True

	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20

		if game_over == 0:
			# Movimiento jugador
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			# Animacion
			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			# Gravedad
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y


			# Colision
			self.in_air = True
			for tile in world.tile_list:
				# Si colisiona en eje X 
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				# Si colisiona en eje Y
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					# Si toca algun objeto por debajo a.k.a esta saltando y colisiona
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					# Si esta encima del piso a.k.a cayendose
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			# Colision con enemigos
			if pygame.sprite.spritecollide(self, spinner_enemy_group, False):
				game_over = -1
				game_over_fx.play()

			# Colision con lava 
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				game_over_fx.play()

			# Si el jugador colisiona con la puerta, pasa al siguiente nivel
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1


			# Colision con plataforma movible
			for platform in moving_platform_group:
				# Eje x
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				# Eje Y
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					# Colision debajo de la plataforma
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					# Arriba de la plataforma movible
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					# Moverse izquierda a derecha
					if platform.move_x != 0:
						self.rect.x += platform.move_direction


			# Aumentar a las coordinadas del jugador
			self.rect.x += dx
			self.rect.y += dy


		elif game_over == -1:
			self.image = self.dead_image
			draw_game_text('PERDISTE!', font, (255,255,255), (screen_width // 2) - 200, screen_height // 2)
			if self.rect.y > 200:
				self.rect.y -= 5

		# Poner al jugador en pantalla
		screen.blit(self.image, self.rect)

		return game_over


	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1,5):
			img_right = pygame.image.load(f'img2/player_{num}.png')
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False) # Flip eje X 

			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('img/ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True



class World():
	def __init__(self, data):
		self.tile_list = []

		# Cargar estructuras (img)
		dirt_img = pygame.image.load('img2/a/estructura_9.png')
		grass_img = pygame.image.load('img2/a/estructura_3.png')

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
					blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
					spinner_enemy_group.add(blob)
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
					moving_platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
					moving_platform_group.add(platform)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					coin = Apple(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					apple_group.add(coin)
					
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
					exit_group.add(exit)
				col_count += 1
			row_count += 1


	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])



class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('enemy.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y 
		self.move_direction = 1
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1


class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img2/a/estructura_9.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


class Apple(pygame.sprite.Sprite):
	
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img2/apple.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/exit.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


player = Player(100, screen_height - 130)

spinner_enemy_group = pygame.sprite.Group()
moving_platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
apple_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Mostrar Score en la pantalla
apple_score = Apple(tile_size // 2, tile_size // 2)
apple_group.add(apple_score)


# Cargar el archivo binario y crear nuestro mundo(nivel)
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)


# Botones
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)


run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))

	if main_menu == True:
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
	else:
		world.draw()

		if game_over == 0:
			spinner_enemy_group.update()
			moving_platform_group.update()
			# Actualizar manzanas
			# Revisar si la manzana fue recolectada
			if pygame.sprite.spritecollide(player, apple_group, True):
				score += 1
				coin_fx.play()
			draw_game_text('X ' + str(score), font_score, white, tile_size - 10, 10)
		
		spinner_enemy_group.draw(screen)
		moving_platform_group.draw(screen)
		lava_group.draw(screen)
		apple_group.draw(screen)
		exit_group.draw(screen)

		game_over = player.update(game_over)

		# Si el jugador pierde (muere)
		if game_over == -1:
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0

		# Si se completa el nivel
		if game_over == 1:
			# Resetear el nivel y pasar al siguiente nivel
			level += 1
			if level <= max_levels:
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				draw_game_text('GANASTE!', font, (255,255,255), (screen_width // 2) - 140, screen_height // 2)
				if restart_button.draw():
					level = 1
					# Resetear nivel
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()