import bpy
import math
from mathutils import Vector, Euler

# ============================================================
# VIC-Gimbal style calibration sweep
# Target is rotated at a fixed centre position on optical axis
# ============================================================

TARGET_NAME = "Calib_Target"
CAM_1_NAME  = "Camera_1"
CAM_2_NAME  = "Camera_2"

# Home position - on Camera 1's optical axis, at working distance,
# at true gauge (AOI) mid-height. AOI spans world Z = 70.005 to 124.23,
# derived from mesh-local Y = 40 to 94.225 (dogbone origin at world Z = 164.23).
TARGET_HOME_LOCATION = Vector((12.5, 2.0, 97.12))

# Rotation grid — ±10° azimuth (Z axis) and ±10° elevation (X axis)
AZIMUTH_STEPS   = [-10, -5, 0, 5, 10]
ELEVATION_STEPS = [-10, -5, 0, 5, 10]
FRAMES_PER_POSE = 1

# ============================================================
# PRE-FLIGHT
# ============================================================
for name in (TARGET_NAME, CAM_1_NAME, CAM_2_NAME):
    if name not in bpy.data.objects:
        raise RuntimeError(f"Missing scene object: {name}")

target = bpy.data.objects[TARGET_NAME]
scene = bpy.context.scene
target.rotation_mode = 'XYZ'
target.location = TARGET_HOME_LOCATION

# ============================================================
# BUILD POSE LIST
# ============================================================
poses = []
for az in AZIMUTH_STEPS:
    for el in ELEVATION_STEPS:
        poses.append((el, 0.0, az))

print(f"\n{'='*60}")
print(f"VIC-Gimbal style calibration sweep")
print(f"Total poses: {len(poses)}")
print(f"Home position: {TARGET_HOME_LOCATION}")
print(f"{'='*60}")

# ============================================================
# CLEAR AND WRITE KEYFRAMES
# ============================================================
if target.animation_data:
    target.animation_data_clear()

frame = 1
for i, (rx, ry, rz) in enumerate(poses):
    target.location       = TARGET_HOME_LOCATION
    target.rotation_euler = Euler((math.radians(rx),
                                   math.radians(ry),
                                   math.radians(rz)), 'XYZ')
    target.keyframe_insert(data_path="location",       frame=frame)
    target.keyframe_insert(data_path="rotation_euler", frame=frame)
    frame += FRAMES_PER_POSE

# Constant interpolation — version-agnostic
def get_fcurves(action):
    if hasattr(action, 'fcurves'):
        return list(action.fcurves)
    fcurves = []
    for slot in action.slots:
        for layer in action.layers:
            for strip in layer.strips:
                cb = strip.channelbag(slot)
                if cb:
                    fcurves.extend(cb.fcurves)
    return fcurves

for fcurve in get_fcurves(target.animation_data.action):
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'CONSTANT'

scene.frame_start = 1
scene.frame_end = frame - 1
scene.frame_current = 1

print(f"\nAnimation written: {len(poses)} poses across frames 1 to {frame - 1}")
print(f"Ready to play in the animation window.")
