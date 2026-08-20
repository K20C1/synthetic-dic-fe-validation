import pyvista as pv
import numpy as np

reader = pv.get_reader("tensile_out.e")

# Enable global node IDs on the underlying VTK reader...BEFORE reading.
try:
    vtk_reader = reader.reader
    vtk_reader.SetGenerateGlobalNodeIdArray(True)
    print("Enabled global node IDs on:", type(vtk_reader).__name__)
except Exception as e:
    print("Could not enable global IDs:", e)

reader.set_active_time_point(0)
block = reader.read()['Element Blocks']['specimen']

# Checking the VOLUME block.
print("\n=== point_data on volume block ===")
print(list(block.point_data.keys()))

candidates = ['GlobalNodeId', 'GlobalNodeID', 'vtkGlobalPointIds',
              'PedigreeNodeId', 'ids']
found = [k for k in block.point_data.keys() if k in candidates]
print("Global-ID arrays found on volume:", found)

for name in found:
    arr = block.point_data[name]
    print(f"{name}: dtype={arr.dtype}, n={len(arr)}, "
          f"min={arr.min()}, max={arr.max()}, unique={len(np.unique(arr))}")

# Debugging to see whether the global IDs survive skinning.
surf0 = block.extract_surface(algorithm='dataset_surface')
print("\n=== point_data on SKINNED SURFACE ===")
print(list(surf0.point_data.keys()))
if 'GlobalNodeId' in surf0.point_data.keys():
    arr = surf0.point_data['GlobalNodeId']
    print(f"GlobalNodeId survives skinning: n={len(arr)}, unique={len(np.unique(arr))}")
else:
    print("GlobalNodeId did NOT survive skinning — will need to carry it manually.")