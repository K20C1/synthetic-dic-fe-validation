import bpy
from mathutils import Vector, Matrix

# ============================================================
# Camera 1 — build to match VIC-3D calibration for Basler acA2440-75um
# ============================================================

# --- Intrinsics ---
PIXEL_PITCH_MM   = 0.00345
RESOLUTION_X     = 2464
RESOLUTION_Y     = 2056
F_PIXELS         = 5193.14
CX_PIXELS        = 1191.36
CY_PIXELS        = 979.638

SENSOR_WIDTH_MM  = RESOLUTION_X * PIXEL_PITCH_MM
SENSOR_HEIGHT_MM = RESOLUTION_Y * PIXEL_PITCH_MM
FOCAL_LENGTH_MM  = F_PIXELS * PIXEL_PITCH_MM

SHIFT_X = (RESOLUTION_X/2 - CX_PIXELS) / RESOLUTION_X
SHIFT_Y = (CY_PIXELS - RESOLUTION_Y/2) / RESOLUTION_X

# --- Extrinsics (specimen centre at world X = +12.5) ---
SPECIMEN_CENTRE_X_MM = 12.5    # specimen mesh extends X = 0 to +25
SPECIMEN_FRONT_Y_MM  = 2.0     # front face at Y = +2, back at Y = 0
AOI_CENTRE_Z_MM      = 82.23   # specimen occupies Z = 0.23 to 164.23
WORKING_DISTANCE_MM  = 245.0

CAMERA_LOCATION = Vector((SPECIMEN_CENTRE_X_MM,
                          SPECIMEN_FRONT_Y_MM + WORKING_DISTANCE_MM,
                          AOI_CENTRE_Z_MM))
AOI_CENTER      = Vector((SPECIMEN_CENTRE_X_MM, 1.0, AOI_CENTRE_Z_MM))

# ============================================================
# Build camera
# ============================================================
if "Camera_1" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Camera_1"], do_unlink=True)

cam_data = bpy.data.cameras.new("Camera_1")
cam_obj  = bpy.data.objects.new("Camera_1", cam_data)
bpy.context.collection.objects.link(cam_obj)

cam_data.type          = 'PERSP'
cam_data.lens          = FOCAL_LENGTH_MM
cam_data.sensor_fit    = 'HORIZONTAL'
cam_data.sensor_width  = SENSOR_WIDTH_MM
cam_data.sensor_height = SENSOR_HEIGHT_MM
cam_data.shift_x       = SHIFT_X
cam_data.shift_y       = SHIFT_Y
cam_data.clip_start    = 10.0
cam_data.clip_end      = 5000.0

scene = bpy.context.scene
scene.render.resolution_x = RESOLUTION_X
scene.render.resolution_y = RESOLUTION_Y
scene.render.resolution_percentage = 100

direction = (AOI_CENTER - CAMERA_LOCATION).normalized()
world_up  = Vector((0, 0, 1))
right     = direction.cross(world_up).normalized()
up        = right.cross(direction).normalized()

rot = Matrix((
    (right.x, up.x, -direction.x, 0.0),
    (right.y, up.y, -direction.y, 0.0),
    (right.z, up.z, -direction.z, 0.0),
    (0.0,     0.0,   0.0,         1.0),
))
cam_obj.matrix_world = Matrix.Translation(CAMERA_LOCATION) @ rot
scene.camera = cam_obj

print(f"Camera 1 at {CAMERA_LOCATION}")
print(f"Aiming at {AOI_CENTER}")
