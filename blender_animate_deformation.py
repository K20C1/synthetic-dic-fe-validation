# Reading MOOSE FEA Output into Blender - Step 4: Animating the Deformation
# 13 July 2026

# Applied project (MAC465 Python development): animates the imported cube across
# the load steps by updating its vertex positions each frame. Runs in Blender
# after blender_geometry_import.py has built the "cube_fea" object.

# Draws on: NumPy (loading the .npz, flattening arrays); Blender bpy (frame-change
# handlers, mesh vertex updates); functions and control flow from the bridge.

import bpy
import numpy as np


# ---------------------------------------------------------------------------
# 1. LOAD THE PER-TIMESTEP COORDINATES
# ---------------------------------------------------------------------------

path = r"\\wsl.localhost\Ubuntu-20.04\home\map25tbw\projects\moose_blender\cube_deformed.npz"
coords = np.load(path)["coords"]        # shape (n_steps, n_points, 3)
n_steps = coords.shape[0]

obj = bpy.data.objects["cube_fea"]      # the mesh built by blender_geometry_import.py
mesh = obj.data


# ---------------------------------------------------------------------------
# 2. MATCH THE FRAME RANGE TO THE TIMESTEPS
# ---------------------------------------------------------------------------

# Frame 1 maps to timestep 0, frame n_steps to the final timestep.
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = n_steps


# ---------------------------------------------------------------------------
# 3. UPDATE THE MESH ON EACH FRAME
# ---------------------------------------------------------------------------

def update_mesh(scene):
    t = scene.frame_current - 1
    t = max(0, min(t, n_steps - 1))     # clamp so out-of-range frames do not error
    flat = coords[t].ravel()            # flatten to (n_points*3,) for foreach_set
    mesh.vertices.foreach_set("co", flat)
    mesh.update()


# ---------------------------------------------------------------------------
# 4. REGISTER THE HANDLER AND SHOW THE FIRST FRAME
# ---------------------------------------------------------------------------

# Clear any previous handler first so re-running does not stack duplicates.
bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(update_mesh)

# Trigger once so the current frame updates immediately.
update_mesh(bpy.context.scene)
print("Animation handler registered.")
