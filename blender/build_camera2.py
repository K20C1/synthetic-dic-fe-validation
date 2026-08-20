import bpy
import numpy as np

path = r"\\wsl.localhost\Ubuntu-20.04\home\map25tbw\projects\dog_bone\finite_tensile\finite_dogbone_deformed.npz"

data = np.load(path)
faces_raw = data["ref_faces"]   # VTK face format: [n, i0, i1, ..., n, i0, i1, ...]
coords = data["coords"]         # shape (n_steps, n_points, 3)

n_steps, n_points, _ = coords.shape
print(f"Loaded: {n_steps} timesteps, {n_points} surface points")

# Use step 0 (reference/undeformed) as the mesh's initial vertices.
verts = coords[0].tolist()

# Convert VTK face array to Blender face list.
# VTK stores faces as [count, v0, v1, ..., count, v0, v1, ...] but flattened.
faces = []
i = 0
while i < len(faces_raw):
    count = faces_raw[i]
    faces.append(tuple(faces_raw[i+1 : i+1+count]))
    i += 1 + count

print(f"Parsed {len(faces)} faces")

# Build the mesh and object.
mesh = bpy.data.meshes.new("dogbone_fea")
mesh.from_pydata(verts, [], faces)
mesh.update()

obj = bpy.data.objects.new("dogbone_fea", mesh)
bpy.context.collection.objects.link(obj)

print("Mesh built and linked.")
