
from vector import Vector2

def create(mesh, vector1, vector2, initial_position):
    initial_index = len(mesh.vertices)

    # print("quadmesh.create - " + str(initial_index))

    mesh.vertices.append(initial_position)
    mesh.vertices.append(initial_position.add(vector1))
    mesh.vertices.append(initial_position.add(vector1).add(vector2))
    mesh.vertices.append(initial_position.add(vector2))

    mesh.uvs = []
    mesh.uvs.append(Vector2(0,0))
    mesh.uvs.append(Vector2(1,0))
    mesh.uvs.append(Vector2(1,1))
    mesh.uvs.append(Vector2(0,1))

    mesh.add_triangle(initial_index+0, initial_index+1, initial_index+3)
    mesh.add_triangle(initial_index+1, initial_index+3, initial_index+2)
    mesh.add_triangle(initial_index+0, initial_index+3, initial_index+1)
    mesh.add_triangle(initial_index+1, initial_index+2, initial_index+3)