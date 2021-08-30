import socket               # Import socket module
from time import sleep
import pygame
import threading
from materials import *

s = socket.socket()         # Create a socket object
ip = input("ip: ")
host = socket.gethostname() if ip == "" else ip
port = 12345                # Reserve a port for your service.




jah = True
cells = []

s = socket.socket()
try:
    s.connect((host, port))
except Exception as e:
    print("oi ei, ", e)
    jah = False


def draw_materials(surface, materials, material_size, selected, offset):
    pygame.draw.rect(surface, col_selected, (offset, selected * material_size, material_size, material_size))
    for key in material_dict:
        pygame.draw.rect(surface, material_dict[key].color, (offset + 5, int(key) * material_size + 5, material_size - 10, material_size - 10))

def get_cells():

    global cells
    
    while True:
        try:
            message = s.recv(1048576)
            cells = eval(message)
        except:
            print("oi ei ", message, " on arusaamatu")

def send_click(mouse_pos, buttons, material):
    s.sendall(bytes(str([mouse_pos, buttons, material]), encoding = "utf-8"))

def main():
    pygame.init()
    surface = pygame.display.set_mode((squares_x * square_size + material_size, max(squares_y * square_size, material_size * num_materials)))
    selected = 0
    line_start = (-1, -1)

    global cells
    
    while True:
        pygame.time.Clock().tick(UPS)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed() == (1, 0, 0):
                    if squares_x * square_size < mouse_x < squares_x * square_size + material_size and 0 < mouse_y < material_size * num_materials:
                        selected = mouse_y//material_size
                
                elif pygame.mouse.get_pressed() == (0, 1, 0):
                    if line_start == (-1, -1):
                        line_start = pygame.mouse.get_pos()
                        line_start = (line_start[0] // square_size, line_start[1] // square_size)
                    else:
                        line_end = pygame.mouse.get_pos()
                        line_end = (line_end[0] // square_size, line_end[1] // square_size)
                        send_click((line_start[0], line_start[1], line_end[0], line_end[1]), pygame.mouse.get_pressed(), selected)
                            
                        line_start = (-1, -1)

        if pressed != (False, False, False) and 0 < mouse_x < squares_x * square_size and 0 < mouse_y < squares_y * square_size:
            send_click((mouse_x // square_size, mouse_y // square_size), pressed, selected)

        surface.fill(col_background)
        pygame.draw.rect(surface, col_empty, (0, 0, squares_x * square_size, squares_y * square_size))

        draw_materials(surface, material_dict, material_size, selected, squares_x * square_size)
            
        for x, y, color in cells:
            pygame.draw.rect(surface, color, (x*square_size, y*square_size, square_size-1, square_size-1))
        
        if line_start != (-1, -1):
            pygame.draw.circle(surface, col_selected, ((line_start[0]+0.5) * square_size, (line_start[1]+0.5) * square_size), 10)
            pygame.draw.line(surface, col_selected, ((line_start[0]+0.5) * square_size, (line_start[1]+0.5) * square_size), ((pygame.mouse.get_pos()[0] // square_size + 0.5) * square_size, (pygame.mouse.get_pos()[1] // square_size + 0.5) * square_size))

        pygame.display.update()

if jah:
    thread1 = threading.Thread(target = get_cells)
    thread2 = threading.Thread(target = main)

    thread1.start()
    thread2.start()
