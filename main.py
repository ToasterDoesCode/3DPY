# Imports
from PIL import Image, ImageDraw, ImageOps
import math

# Get OBJ path from user
path = input("Please enter the path to the OBJ file you'd like to render: \n")
print()

# Declare and initialize needed global variables
vertices_obj = []

faces_obj = []

offset = 0.01

# Camera
focal_length = 20

# Open OBJ
with open(path, "r") as f:
    # Get information from OBJ file
    data = f.readlines()
    
    # Get vertices from OBJ file
    for line in data:
        if line[0] == "v" and line[1] == " ":
            # line is a vertex
            
            vertex = []
            
            for substring in line.split(" ")[1:]:
                vertex.append(float(substring) + offset)
            
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

def rotate_vertex(vert, axis, deg):
    rot_x = [
        [1, 0, 0],
        [0, math.cos(deg), -math.sin(deg)],
        [0, math.sin(deg), math.cos(deg)]
    ]
    
    rot_y = [
        [math.cos(deg), 0, math.sin(deg)],
        [0, 1, 0],
        [-math.sin(deg), 0, math.cos(deg)]
    ]
    
    rot_z = [
        [math.cos(deg), -math.sin(deg), 0],
        [math.sin(deg), math.cos(deg), 0],
        [0, 0, 1]
    ]
    
    rot = []
    
    if axis == "x":
        rot = rot_x
    elif axis == "y":
        rot = rot_y
    elif axis == "z":
        rot = rot_z
    
    new_coordinates = [0, 0, 0]
    
    for i in range(2):
        new_coordinates[i] = rot[i][0] * vert[0] + rot[i][1] * vert[1] + rot[i][2] * vert[2]
    
    return new_coordinates
    
def draw_frame(faces):
    img = Image.new("RGB", (1920, 1080))
    draw = ImageDraw.Draw(img)
    
    projected_faces = []
    
    for face in faces:
        face_projected = []
        
        for vertex in face:
            
            x = vertex[0] + offset
            y = vertex[1] + offset
            z = vertex[2] + offset

            vertex_projected_screen = (((((focal_length * x) / (focal_length + z))) * scale) + 1920 / 2, (((focal_length * y) / (focal_length + z)) * scale + 1080 / 2))
            
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
    
    draw_faces = True
    
    # Render faces
    for i in range(len(projected_faces)):
        projected_faces[i].pop(len(projected_faces[i]) - 1)
        if draw_faces:
            shade = int(i / len(projected_faces) * 255 + 10)
    
            draw.polygon(projected_faces[i], fill=(shade, shade, shade))
    
    # Render lines
    for face in projected_faces:
    
        for i in range(1, len(face)):
            draw.line((face[i - 1][0], face[i - 1][1], face[i][0], face[i][1]), fill=(255, 255, 255))
    
    draw_points = True
    point_radius = 2
    
    if draw_points:
        for face in projected_faces:
            for vertex_projected in face:
                draw.ellipse((vertex_projected[0] - point_radius, vertex_projected[1] - point_radius, vertex_projected[0] + point_radius, vertex_projected[1] + point_radius), fill=(255,255,255))
    
    img = ImageOps.flip(img)
    return img
    
def rotate_object(axis, deg):
    faces_rot = []

    for f in range(len(faces_obj)):
        face_rot = []
        
        for v in range(len(faces_obj[f])):
            face_rot.append(rotate_vertex(faces_obj[f][v], axis, deg))
        faces_rot.append(face_rot)
    return faces_rot

gif_frames = []

for i in range(10):
    gif_frames.append(draw_frame(rotate_object("y", i * (360 / 60))))

print(gif_frames)

gif_frames[0].save('out.gif', save_all=True, append_images=gif_frames[1:], duration=10, loop=0)