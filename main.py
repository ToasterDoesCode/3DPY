# Imports
from PIL import Image, ImageDraw, ImageOps
import numpy as np

# Get OBJ path from user
path = input("Please enter the path to the OBJ file you'd like to render: \n")
print()

# Declare and initialize needed global variables
vertices = []

faces = []

offset = 0

img = Image.new("RGB", (1920, 1080))
draw = ImageDraw.Draw(img)

# Camera
focal_length = 2

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
            
            vertices.append(vertex)
            
    
    # Get faces from OBJ file
    for line in data:

        if line[0] == "f":
            # line is a face
            
            face = []
            
            for substring in line.split(" ")[1:]:
                face.append(vertices[int(substring.split("/")[0]) - 1])
            faces.append(face)

scale = 300

projected_faces = []

for face in faces:
    face_projected = []
    
    for vertex in face:
        
        x = vertex[0]
        y = vertex[1]
        z = vertex[2]
        
        vertex_projected_screen = (((((focal_length * x) / (focal_length + z))) * scale) + 1920 / 2, (((focal_length * y) / (focal_length + z)) * scale + 1080 / 2))
        
        print("Projected vertex: " + str(vertex_projected_screen))
        
        face_projected.append(vertex_projected_screen)
        
    projected_faces.append(face_projected)
    
    
# Get face averages and depths
for i in range(len(faces)):
    face_average = []
    
    for v in range(len(faces[i])):
        face_average.append(faces[i][v][0])
    
    first = np.mean(face_average)
    face_average = []
    
    for v in range(len(faces[i])):
        face_average.append(faces[i][v][1])
    
    second = np.mean(face_average)
    face_average = []
    
    for v in range(len(faces[i])):
        face_average.append(faces[i][v][2])
    
    third = np.mean(face_average)
    face_average = (float(first), float(second), float(third))
    
    depth = np.sqrt(face_average[0] ** 2 + face_average[1] ** 2 + face_average[2] ** 2)
    projected_faces[i].append(depth)

projected_faces = sorted(projected_faces, key=lambda x:x[len(x) - 1], reverse=True)

# Render faces
for i in range(len(projected_faces)):
    projected_faces[i].pop(len(projected_faces[i]) - 1)
    
    shade = int(i / len(projected_faces) * 255 + 10)
    
    draw.polygon(projected_faces[i], fill=(shade, shade, shade))

# Render lines
for face in projected_faces:

    for i in range(1, len(face)):
        draw.line((face[i - 1][0], face[i - 1][1], face[i][0], face[i][1]), fill=(255, 255, 255))

# Render points
#for face in projected_faces:
#    for vertex_projected in face:
#        draw.ellipse((vertex_projected[0] - 5, vertex_projected[1] - 5, vertex_projected[0] + 5, vertex_projected[1] + 5), fill=(255,255,255))

img = ImageOps.flip(img)
img.show()