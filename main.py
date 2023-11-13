# Imports
from PIL import Image, ImageDraw, ImageOps
from msvcrt import getch
import math
import pygame

# Get OBJ path from user
path = input("Please enter the path to the OBJ file you'd like to render: \n")
print()

# Declare and initialize needed global variables
vertices_obj = []

faces_obj = []

offset = 0.01

# Camera properties
focal_length = 0.005

cam_pos = [0, 0, 0]

# Control properties
mouse_sens = 0.1

# Open OBJ
with open(path, "r") as f:
    # Get information from OBJ file
    data = f.readlines()
    
    # Get vertices from OBJ file
    for line in data:
        if line[0] == "v" and line[1] == " ":
            # line is a vertex
            
            vertex = []
            
            i = 0
            
            for substring in line.split(" ")[1:]:
                vertex.append(float(substring) + offset + cam_pos[i])
                i += 1
            
            vertices_obj.append(vertex)
            
    
    # Get faces from OBJ file
    for line in data:

        if line[0] == "f":
            # line is a face
            face = []
            
            for substring in line.split(" ")[1:]:
                face.append(vertices_obj[int(substring.split("/")[0]) - 1])
            faces_obj.append(face)

scale = int(input("What scale?"))

# Rotate vertex
def rotate_vertex(vert, axis, deg):
    rot_x = [
        [1, 0, 0],
        [0, math.cos(deg[0]), -math.sin(deg[0])],
        [0, math.sin(deg[0]), math.cos(deg[0])]
    ]
    
    rot_y = [
        [math.cos(deg[1]), 0, math.sin(deg[1])],
        [0, 1, 0],
        [-math.sin(deg[1]), 0, math.cos(deg[1])]
    ]
    
    rot_z = [
        [math.cos(deg[2]), -math.sin(deg[2]), 0],
        [math.sin(deg[2]), math.cos(deg[2]), 0],
        [0, 0, 1]
    ]
    
    rot = []
    
    new_coordinates = [0, 0, 0]
    for a in range(len(axis)):
    
        if axis[a] == "x":
            rot = rot_x
        elif axis[a] == "y":
            rot = rot_y
        elif axis[a] == "z":
            rot = rot_z
        
        for i in range(2):
            new_coordinates[i] = rot[i][0] * vert[0] + rot[i][1] * vert[1] + rot[i][2] * vert[2]
    
    return new_coordinates

# Rotate object
def rotate_object(axis, deg):
    faces_rot = []

    for f in range(len(faces_obj)):
        for v in range(len(faces_obj[f])):
            face_rot.append(rotate_vertex(faces_obj[f][v], axis, deg))
        faces_rot.append(face_rot)
    return faces_rot

# Draw a frame
def draw_frame(faces, rotation=(0, 0, 0)):
    img = Image.new("RGB", (1920, 1080))
    draw = ImageDraw.Draw(img)
    
    projected_faces = []
    
    for face in faces:
        face_projected = []
        
        for vertex in face:
            
            x = rotate_vertex(vertex, "xy", rotation)[0] + offset - cam_pos[0]
            y = rotate_vertex(vertex, "yz", rotation)[1] + offset - cam_pos[1]
            z = rotate_vertex(vertex, "xz", rotation)[2] + offset - cam_pos[2]

            vertex_projected_screen = ((((x / (focal_length /z))) * scale) + 1920 / 2, ((y / (focal_length / z)) * scale + 1080 / 2))
            
            face_projected.append(vertex_projected_screen)
            
        projected_faces.append(face_projected)
        
        
    # Get face averages and depths
    for i in range(len(faces)):
        face_average = []
        
        for v in range(len(faces[i])):
            face_average.append(faces[i][v][0])
        
        first = sum(face_average) / len(face_average)
        face_average = []
        
        for v in range(len(faces[i])):
            face_average.append(faces[i][v][1])
        
        second = sum(face_average) / len(face_average)
        face_average = []
        
        for v in range(len(faces[i])):
            face_average.append(faces[i][v][2])
        
        third = sum(face_average) / len(face_average)
        face_average = (float(first), float(second), float(third))
        
        depth = math.sqrt(face_average[0] ** 2 + face_average[1] ** 2 + face_average[2] ** 2)
        projected_faces[i].append(depth)
    
    projected_faces = sorted(projected_faces, key=lambda x:x[len(x) - 1], reverse=True)
    
    # Prep faces array
    for i in range(len(projected_faces)):
        projected_faces[i].pop(len(projected_faces[i]) - 1)
    
    # Render lines
    for face in projected_faces:
        
        for i in range(1, len(face)):
            pygame.draw.line(screen, "white", (face[i - 1][0], face[i - 1][1]), (face[i][0], face[i][1]))
    
    draw_points = True
    point_radius = 2
    
    # Render points
    if draw_points:
        for face in projected_faces:
            for vertex_projected in face:
                pygame.draw.circle(screen, "white", vertex_projected, 5)
    
    img = ImageOps.flip(img)
    return img

current_faces = faces_obj

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # Draw a frame
    draw_frame(current_faces, rotation=(0, pygame.mouse.get_pos()[0] * -mouse_sens, pygame.mouse.get_pos()[1] * mouse_sens))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
