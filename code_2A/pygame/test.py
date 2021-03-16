import pygame

# Window size
WINDOW_WIDTH  = 400
WINDOW_HEIGHT = 400
FPS           = 60

# background colours
GREEN = (0, 255, 0)

class HoleSprite( pygame.sprite.Sprite ):
    def __init__( self ):
        pygame.sprite.Sprite.__init__( self )
        # Make a full-image (no hole)
        self.base_image = pygame.Surface( ( 400, 400 ), pygame.SRCALPHA )
        self.base_image.fill( ( 0,0,0,100 ) ) # darken the background
        # Make an image with a see-through window
        self.hole_image = pygame.Surface( ( 400, 400 ), pygame.SRCALPHA )
        self.hole_image.fill( ( 0,0,0,100 ) )
        pygame.draw.circle(self.hole_image, (0, 0, 0, 0), (200, 200), 200) # canal alpha à zéro, donc transparent
        
        # sprite housekeeping
        self.image  = self.base_image
        self.rect   = self.image.get_rect()
        self.last   = 0

    def update( self ):
        time_ms = pygame.time.get_ticks()
        # FLip the images each second
        if ( time_ms - self.last > 1000 ):
            if ( self.image == self.hole_image ):
                self.image = self.base_image
            else:
                self.image = self.hole_image
            self.last = time_ms


### MAIN
pygame.init()
pygame.font.init()
SURFACE = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE
WINDOW  = pygame.display.set_mode( ( WINDOW_WIDTH, WINDOW_HEIGHT ), SURFACE )
pygame.display.set_caption("Hole Sprite Test")


holey = HoleSprite( )


clock = pygame.time.Clock()
done  = False
while not done:

    # Handle user-input
    for event in pygame.event.get():
        if ( event.type == pygame.QUIT ):
            done = True

    # Repaint the screen
    holey.update()
    WINDOW.fill( GREEN )
    WINDOW.blit(holey.image,holey.rect, None)

    pygame.display.flip()
    # Update the window, but not more than 60fps
    clock.tick_busy_loop( FPS )

pygame.quit()