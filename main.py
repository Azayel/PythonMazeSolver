from calendar import c
from dataclasses import field
from dis import dis
from glob import glob

from math import dist
import random
from re import T
from tkinter import Grid, Variable
from turtle import left
import pygame
from requests import NullHandler 

openList=[]
closedList=[]

height = width = 1000
dimension = 20
sq_size = width // dimension
screen = pygame.display.set_mode((width,height))
stack=[]
generating = True
start_cell_coord=(0,0)
end_cell_coord=(dimension-1,dimension-1)
back_path = []
solved=False

#Creating Class Field
#Class Field has following tasks:
#Class Field stores the actual Field data and is responsible for managing any changes that are being made to it.


class Field():
    def __init__(self,size):
        self.grid=[[Cell(i,j) for i in range(size)] for j in range(size)]


class Cell():
    def __init__(self,r,c):
        self.f=0
        self.g=0
        self.h=0
        self.start_cell=False
        self.end_cell=False
        self.r = r
        self.c = c
        self.visited=False
        self.walls = [True,True,True,True] #TOP RIGHT BOTTOM LEFT
        self.a_neighbors=[]
        self.previous=None
    def wall(self):
        if self.visited:
            pygame.draw.rect(screen,pygame.Color("black"),pygame.Rect(self.c*sq_size,self.r*sq_size,sq_size,sq_size))
        #Top
        if self.walls[0]:
            pygame.draw.line(screen,pygame.Color("gray"),(self.c*sq_size,self.r*sq_size),(self.c*sq_size+sq_size,self.r*sq_size))
        #Right
        if self.walls[1]:
            pygame.draw.line(screen,pygame.Color("gray"),(self.c*sq_size+sq_size,self.r*sq_size),(self.c*sq_size+sq_size,self.r*sq_size+sq_size))
        #Bottom
        if self.walls[2]:
            pygame.draw.line(screen,pygame.Color("gray"),(self.c*sq_size+sq_size,self.r*sq_size+sq_size),(self.c*sq_size,self.r*sq_size+sq_size))
        #Left
        if self.walls[3]:
            pygame.draw.line(screen,pygame.Color("gray"),(self.c*sq_size,self.r*sq_size),(self.c*sq_size,self.r*sq_size+sq_size))

    def add_Neighbors(self):
        
        if self.c+1 in range(0,dimension):
            if self.walls[1] == False:
                self.a_neighbors.insert(0,field_object.grid[self.c+1][self.r])
        if self.c-1 in range(0,dimension):
            if self.walls[3] == False:
                self.a_neighbors.insert(0,field_object.grid[self.c-1][self.r])
        if self.r+1 in range(0,dimension):
            if self.walls[2] == False:
                self.a_neighbors.insert(0,field_object.grid[self.c][self.r+1])
        if self.r-1 in range(0,dimension):
            if self.walls[0] == False:
                self.a_neighbors.insert(0,field_object.grid[self.c][self.r-1])

    def cell_coordinates(self):
        print((self.c*sq_size,self.r*sq_size))

    def checkNeighbours(self):
        neighbours=[]
        if self.r-1 in range(0,dimension):
            top = field_object.grid[self.c][self.r-1]
            if not top.visited:
                neighbours.append(top)
        
        if self.c+1 in range(0,dimension):
            right = field_object.grid[self.c+1][self.r]
            if not right.visited:
                neighbours.append(right)

        if self.c in range(0,dimension) and self.r+1 in range(0,dimension):
            bottom = field_object.grid[self.c][self.r+1]
            if not bottom.visited:
                neighbours.append(bottom)

        if self.c-1 in range(0,dimension):
            left = field_object.grid[self.c-1][self.r]
            if not left.visited:
                neighbours.append(left)
        

        if len(neighbours) > 0:
            r = random.randint(0,len(neighbours)-1)
            
            return neighbours[r]

        else:
            
            return None
    
    def highlight(self):
        pygame.draw.rect(screen,pygame.Color("green"),pygame.Rect(self.c*sq_size,self.r*sq_size,sq_size,sq_size))
        
    def unhighlight(self):
        pygame.draw.rect(screen,pygame.Color("purple"),pygame.Rect(self.c*sq_size,self.r*sq_size,sq_size,sq_size))

field_object=Field(dimension)

current=field_object.grid[0][0]


def heuristic(a,b):
    distance = dist((a.c,a.r),(b.c,b.r))
    return distance
   

def create_window():
    global generating
    global start_cell_coord
    global end_cell_coord
    pygame.display.set_caption("A*")
    

    

    running = True

    while running:
        
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #Getting the GRID Coordinates for the mouse events
                mouse_coordinates=pygame.mouse.get_pos()
                mouse_coordinates_x=int((mouse_coordinates[0]/width)*dimension)
                mouse_coordinates_y=int((mouse_coordinates[1]/width)*dimension)
                
                generating=False
                current.unhighlight()
                
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    mouse_coordinates=pygame.mouse.get_pos()
                    mouse_coordinates_x=int((mouse_coordinates[0]/width)*dimension)
                    mouse_coordinates_y=int((mouse_coordinates[1]/width)*dimension)
                    field_object.grid[mouse_coordinates_x][mouse_coordinates_y].start_cell=True
                    start_cell_coord=(mouse_coordinates_x,mouse_coordinates_y)
                    openList.insert(0,field_object.grid[start_cell_coord[0]][start_cell_coord[1]])
                if event.key == pygame.K_e:
                    mouse_coordinates=pygame.mouse.get_pos()
                    mouse_coordinates_x=int((mouse_coordinates[0]/width)*dimension)
                    mouse_coordinates_y=int((mouse_coordinates[1]/width)*dimension)
                    field_object.grid[mouse_coordinates_x][mouse_coordinates_y].end_cell=True
                    end_cell_coord=(mouse_coordinates_x,mouse_coordinates_y)
                    
        draw_status(screen,field_object.grid)
        pygame.time.Clock().tick(15)
        pygame.display.flip()

def draw_status(screen,field):
    #draw_grid(screen,field)
    if generating:
        draw_wall_grid(screen,field)
    else:
        for i in range(dimension):
            for j in range(dimension):
                field[i][j].add_Neighbors()
        draw_maze(screen,field)
        



def draw_maze(screen,field):
    global back_path
    global openList_current
    global solved
    
    if len(openList)>0:
        
        lowest_Index=0
        for i in range(len(openList)):
            
            if openList[i].f < openList[lowest_Index].f:
                
                lowest_Index = i
       
        openList_current=openList[lowest_Index]
        #openList_current=field_object.grid[openList_current[0]][openList_current[1]]
        print((openList_current.c,openList_current.r))
        if openList_current.end_cell:
            solved=True
            back_path = []
            temp = openList_current
            back_path.insert(0,temp)
            while(temp.previous):
                back_path.insert(0,temp.previous)
                temp= temp.previous
            
        
        openList.remove(openList_current)
        closedList.insert(0,openList_current)

        neighbors = openList_current.a_neighbors
       
        for i in neighbors:
            
            if i not in closedList:
                tempG = openList_current.g + 1

                if i in openList:
                    if tempG<i.g:
                        i.g=tempG
                else:
                    i.g = tempG
                    openList.insert(0,i)
                i.h = heuristic(i,field_object.grid[end_cell_coord[0]][end_cell_coord[1]])
                i.f = i.g + i.h
                i.previous =  openList_current
            

    else:
        #no solution
        pass

    for r in range(dimension):
        for c in range(dimension):
            field[r][c].wall()
            if field[r][c].start_cell == True:
                pygame.draw.circle(screen,pygame.Color("blue"),(c*sq_size+(sq_size/2),r*sq_size+(sq_size/2)),10)
            elif field[r][c].end_cell == True:
                pygame.draw.circle(screen,pygame.Color("pink"),(c*sq_size+(sq_size/2),r*sq_size+(sq_size/2)),10)
    
    for i in openList:
        if not solved:
            pygame.draw.circle(screen,pygame.Color("green"),(i.c*sq_size+(sq_size/2),i.r*sq_size+(sq_size/2)),5)
    
    for i in closedList:
        if not solved:
            #pygame.draw.circle(screen,pygame.Color("red"),(i.c*sq_size+(sq_size/2),i.r*sq_size+(sq_size/2)),10)
            if i.previous != None:
                pygame.draw.line(screen,pygame.Color("blue"),(i.c*sq_size+(sq_size/2),i.r*sq_size+(sq_size/2)),(i.previous.c*sq_size+(sq_size/2),i.previous.r*sq_size+(sq_size/2)))
        else:
            pass
    
    for i in back_path:
        if i.previous != None:
            pygame.draw.line(screen,pygame.Color("red"),(i.c*sq_size+(sq_size/2),i.r*sq_size+(sq_size/2)),(i.previous.c*sq_size+(sq_size/2),i.previous.r*sq_size+(sq_size/2)))
        #pygame.draw.circle(screen,pygame.Color("gray"),(i.c*sq_size+(sq_size/2),i.r*sq_size+(sq_size/2)),3)
    

def draw_wall_grid(screen,field):
    
    global current
    
    current.visited=True
    next = current.checkNeighbours()
    
    if next:
        next.visited = True
        stack.insert(0,current)
        removeWalls(current,next)
        current = next
    elif len(stack)>0:
        current= stack.pop()
        


    for r in range(dimension):
        for c in range(dimension):
            field[r][c].wall()
    current.highlight()
    

def removeWalls(current , next):
    x = next.c - current.c
    
    
    if x==1:
        next.walls[3]=False
        current.walls[1]=False
        
    elif x==-1:
        next.walls[1]=False
        current.walls[3]=False
    
    y = next.r - current.r
    
    if y==1:
        next.walls[0]=False
        current.walls[2]=False
    elif y==-1:
        current.walls[0]=False
        next.walls[2]=False
    



if __name__ == "__main__":
    create_window()
    
    
    
    
