# Imports
import math
import pygame
import numpy as np
import threading

# Needed global variables
# Display
screen_size = screen_width, screen_height = 1080, 720

display_foreground = (255, 255, 255)
display_background = (0, 0, 0)

display_grid = (120, 120, 120)

scale = 10

# Camera
fov = 95
cam_pos = [0, 0, 0]
cam_rot = [0, 0, 0]
cam_plane = [0, 0, 5]

# OBJ data
obj_faces = []
obj_vertices = []

# Game control
game_running = False

# Necessary functions
def transform_vector(v, m):
    return np.array(v) @ np.array(m)

# Rotate vertex
def rotate_project_vertex(vert, deg, origin):
    x_rot = [
        [1, 0, 0],
        [0, math.cos(deg[0]), math.sin(deg[0])],
        [0, -math.sin(deg[0]), math.cos(deg[0])]
    ]
    
    y_rot = [
        [math.cos(deg[1]), 0, -math.sin(deg[1])],
        [0, 1, 0],
        [math.sin(deg[1]), 0, math.cos(deg[1])]
    ]
    
    z_rot = [
        [math.cos(deg[2]), math.sin(deg[2]), 0],
        [-math.sin(deg[2]), math.cos(deg[2]), 0],
        [0, 0, 1]
    ]
    
    # Combine the matrices by multiplying them together
    rot = np.array(x_rot) @ np.array(y_rot) @ np.array(z_rot)
    
    # Project
    projected_vector = np.subtract(np.array(vert), np.array(origin)) @ rot
    
    # Transform to screen coordinates and return
    return [(((cam_plane[2] / projected_vector[2]) * projected_vector[0] + cam_plane[0]) * scale) + screen_width / 2, (((cam_plane[2] / projected_vector[2]) * projected_vector[1] + cam_plane[1]) * scale) + screen_height / 2]

# Read an OBJ
def read_obj(path):
    with open(path, 'r') as f:
        # Read lines of file
        obj_lines = f.readlines()
        
        # Loop through each line and read
        for obj_line in obj_lines:
            # Check if line is a vertex
            if obj_line[0] == "v" and obj_line[1] == " ":
                # Line is a vertex, read
                # Temporary variable to store current vertex
                obj_current_vertex = []
                
                for obj_coord in obj_line.split(" ")[1:]:
                    obj_current_vertex.append(float(obj_coord))
                
                # Add to all vertices
                obj_vertices.append(obj_current_vertex)
                
            # Check if line is a face
            if obj_line[0] == "f":
                # Line is a face, read
                # Temporary variable to store current face
                obj_current_face = []
                
                for obj_vertex_i in obj_line.split(" ")[1:]:
                    # Add vertex at index to face
                    obj_current_face.append(obj_vertices[int(obj_vertex_i.split("/")[0]) - 1])
                
                # Add to all faces
                obj_faces.append(obj_current_face)
                
def draw_frame(faces):
    # Out variable to store output
    projected_vertices = []
    
    # Loop through each face
    for face in faces:
        current_projected_face = []
    
        # Loop through each vertex
        for vertex in face:
            # Project and store
            projected_vertex = rotate_project_vertex(vertex, cam_rot, cam_pos)
            projected_vertices.append(projected_vertex)
            
            
        
        # Draw face
        #pygame.draw.polygon(screen, display_foreground, current_projected_face)

    vertex_depths = []
    
    # Draw
    for face in faces:
        for vertex in face:
            # Get vertex depth
            vertex_depths.append(math.sqrt((vertex[0] - cam_pos[0]) ** 2) + (vertex[1] - cam_pos[1]) ** 2 + (vertex[2] - cam_pos[2]) ** 2)
    
    for vertex in sorted(projected_vertices, key=lambda x : vertex_depths[projected_vertices.index(x)]):
        pygame.draw.circle(screen, display_foreground, vertex, 5)
    
# Set up pygame
pygame.init()
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()

# Obj stuff
obj_file = input()
read_obj(obj_file)

running = True

while running:

    for event in pygame.event.get():
        # Key presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                cam_pos[0] -= math.sin(cam_rot[0]) * math.cos(cam_rot[1])
                cam_pos[1] -= math.sin(cam_rot[0]) * math.sin(cam_rot[1])
                cam_pos[2] -= math.cos(cam_rot[0])
            if event.key == pygame.K_s:
                cam_pos[0] += math.sin(cam_rot[0]) * math.cos(cam_rot[1])
                cam_pos[1] += math.sin(cam_rot[0]) * math.sin(cam_rot[1])
                cam_pos[2] += math.cos(cam_rot[0])
            if event.key == pygame.K_a:
                cam_pos[1] -= math.sin(cam_rot[0]) * math.cos(cam_rot[1])
                cam_pos[0] -= math.sin(cam_rot[0]) * math.sin(cam_rot[1])
                cam_pos[2] -= math.cos(cam_rot[0])
            
            if event.key == pygame.K_UP:
                cam_rot[0] -= 5
            if event.key == pygame.K_DOWN:
                cam_rot[0] += 5
            if event.key == pygame.K_LEFT:
                cam_rot[1] -= 5
            if event.key == pygame.K_RIGHT:
                cam_rot[1] += 5
                
        if event.type == pygame.MOUSEWHEEL:
            cam_plane[2] += event.y
    
    # PROBLEM: Roll (Z component of cam_rot) is unknown, need to calculate it somehow.
    cam_rot[0] = math.radians(pygame.mouse.get_pos()[0] / 2)
    cam_rot[1] = math.radians(-pygame.mouse.get_pos()[1] / 2)
    
    # Refresh screen
    screen.fill(display_background)

    draw_frame(obj_faces)

    # Draw to screen
    pygame.display.flip()

    # Limit FPS
    clock.tick(60)

pygame.quit()