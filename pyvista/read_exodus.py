# Reading MOOSE FEA Output into Blender - Step 1: Inspecting the Exodus File
# 8 July 2026

# Applied project (MAC465 Python development): using Python to bridge a finite
# element solver (MOOSE) and Blender.

# Draws on: Modules and File Handling (Imperial bridge); Functions and OOP
# (recursion); Collections and Control Flow.

# Opens the Exodus output and prints its structure so the extraction step knows
# which arrays are available before processing.

import pyvista as pv


# ---------------------------------------------------------------------------
# 1. OPEN THE EXODUS FILE
# ---------------------------------------------------------------------------

# A reader exposes the timestep count before the full mesh is read.
reader = pv.get_reader("tensile_out.e")
print("Number of time points:", reader.number_time_points)

mesh = reader.read()
print("Top-level blocks:", len(mesh))


# ---------------------------------------------------------------------------
# 2. DESCRIBE THE BLOCK STRUCTURE
# ---------------------------------------------------------------------------

# Exodus meshes are nested MultiBlocks; recursion walks the tree, indenting deeper.
def describe(block, name, indent=""):
    if isinstance(block, pv.MultiBlock):
        print(f"{indent}{name!r}: MultiBlock with {len(block)} sub-blocks")
        for i in range(len(block)):
            describe(block[i], block.get_block_name(i), indent + "  ")
    elif block is None:
        print(f"{indent}{name!r}: empty")
    else:
        # Leaf blocks hold the data; the array keys (e.g. disp_) drive the next step.
        print(f"{indent}{name!r}: {type(block).__name__}, "
              f"n_points={block.n_points}, n_cells={block.n_cells}")
        print(f"{indent}   point_data: {block.point_data.keys()}")
        print(f"{indent}   cell_data: {block.cell_data.keys()}")


for i in range(len(mesh)):
    describe(mesh[i], mesh.get_block_name(i))
