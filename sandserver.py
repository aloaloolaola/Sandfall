import pygame
from materials import *
import numpy as np
from random import randint
import socket
from time import sleep
import threading

PAUSED = 0
cells = []

def init(dimx, dimy):
    cells_grid = np.zeros((dimy, dimx), dtype="O")
    return (cells_grid)

cells_grid = init(squares_x, squares_y)

def draw_materials(surface, materials, material_size, selected, offset):
    pygame.draw.rect(surface, col_selected, (offset, selected * material_size, material_size, material_size))
    for key in material_dict:
        pygame.draw.rect(surface, material_dict[key].color, (offset + 5, int(key) * material_size + 5, material_size - 10, material_size - 10))

def respond():
    s = socket.socket()
    host = "0.0.0.0"
    port = 12345
    s.bind((host, port))
    s.listen(5)
    while True:
        c, addr = s.accept()
        thread = threading.Thread(target = new_client, args = (c,addr))
        thread.start()

def new_client(c,addr):
    global cells
    thread = threading.Thread(target = get_clicks, args = (c,addr))
    thread.start()
    while True:
        cells_send = str([[cell.x, cell.y, cell.color] for cell in cells]) + "#"
        c.sendall(bytes(cells_send, encoding = "utf-8"))
        sleep(1/UPS)

def get_clicks(c, addr):
    global cells, cells_grid, squares_x, squares_y
    while True:
        click = eval(c.recv(1024))
        if len(click[0]) == 4:
            print(click)
            for pos in get_line((click[0][0], click[0][1]), (click[0][2], click[0][3])):
                if get_cell(pos[0], pos[1], cells_grid, squares_y, squares_x).state == "":
                    set_cell(pos[0], pos[1], cells, cells_grid, material_dict[str(click[2])](pos[0], pos[1]))
            
        if click[1] == (0, 0, 1):
            cell = get_cell(click[0][0], click[0][1], cells_grid, squares_y, squares_x)
            if cell.state not in ("", "1"):
                remove_cell(cell, cells, cells_grid)
        elif click[1] == (1, 0, 0):
            if get_cell(click[0][0], click[0][1], cells_grid, squares_y, squares_x).state == "":
                set_cell(click[0][0], click[0][1], cells, cells_grid, material_dict[str(click[2])](click[0][0], click[0][1]))
        

def get_line(start, end): # not mine
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
 
    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)
 
    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
 
    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
 
    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1
 
    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1
 
    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx
 
    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

def main(dimx, dimy, cellsize):
    pygame.init()
    clock = pygame.time.Clock()


    line_start = (-1, -1)

    selected = 0

    global PAUSED
    global cells

    while True:
        clock.tick(UPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    PAUSED = not PAUSED
                if event.key == pygame.K_RETURN:
                    PAUSED = -1

        if PAUSED < 1:
            for cell in cells:
                cell.update(cells, cells_grid, dimx, dimy)

        if PAUSED == -1:
            PAUSED = 1

        for cell in cells:
            if get_cell(cell.x, cell.y, cells_grid, dimx, dimy) != cell:
                print(cell.x, cell.y, "is wrong!")
                print(cells_grid)
                throwexception()

def start():
    main(squares_x, squares_y, square_size)

thread1 = threading.Thread(target = respond)
thread2 = threading.Thread(target = start)

thread1.start()
thread2.start()
