def update(self, game_over):
    dx = 0
    dy = 0
    walk_cooldown = 5
    
    if game_over == 0:  
      # Mecanica de saltar, movimiento
      key = pygame.key.get_pressed()
      # Prevenir que pueda saltar infinitas veces
      if key[pygame.K_SPACE] and self.jumped == False:
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
      for tile in world.tile_list: 
        # Colision en X
        if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
          dx = 0
        
        # Si colisiona con algo en Y 
        if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
          # Verificar si esta debajo del suelo 
          if self.vel_y < 0: 
            dy = tile[1].bottom - self.rect.top
            self.vel_y = 0 
          # Verificar si esta encima del suelo
          elif self.vel_y >= 0:
            dy = tile[1].top - self.rect.bottom
            self.vel_y = 0 
        
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
    pygame.draw.rect(screen, (255,255,255), self.rect, 2)
    return game_over