import pygame


class ToggleButton:
    def __init__(self, x, y, crash_text, rebound_text, stop_text):
        self.rect = pygame.Rect(x, y, 150, 75)
        font = pygame.font.Font(None, 32)
        self.text = [font.render(crash_text, True, (255, 255, 255)),
                     font.render(rebound_text, True, (255, 255, 255)),
                     font.render(stop_text, True, (255, 255, 255))]

        self.color = [(255, 0, 0),
                      (0, 255, 0),
                      (0, 0, 255)]

        self.state = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color[self.state], self.rect)
        screen.blit(self.text[self.state], self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = (self.state + 1) % 3

    def get_status(self):
        return self.state
