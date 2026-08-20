import bpy
import os
import time

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = r"C:\Users\lorna\Documents\TW\Blender\Specimen renders\tensile"

FILENAME_PREFIX = "specimen"

CAM_1_NAME = "Camera_1"    # → _0.tif (Camera 0 in VIC-3D)
CAM_2_NAME = "Camera_2"    # → _1.tif (Camera 1 in VIC-3D)

FRAME_RANGE = (1, 11)

# Render quality settings
SAMPLES    = 1024
FIXED_SEED = 0

# Resolution
RESOLUTION_X          = 2464
RESOLUTION_Y          = 2056
RESOLUTION_PERCENTAGE = 100

HIDE_DURING_RENDER = [] 

# ============================================================
# PRE-FLIGHT
# ============================================================
scene = bpy.context.scene

for name in (CAM_1_NAME, CAM_2_NAME):
    if name not in bpy.data.objects:
        raise RuntimeError(f"Missing camera: {name}")

cam1 = bpy.data.objects[CAM_1_NAME]
cam2 = bpy.data.objects[CAM_2_NAME]

os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Output directory: {OUTPUT_DIR}")

start_frame, end_frame = FRAME_RANGE
total_frames = end_frame - start_frame + 1
print(f"Frame range: {start_frame} to {end_frame}")
print(f"Total renders: {total_frames * 2} ({total_frames} pairs)")

# ============================================================
# FORCE NVIDIA OPTIX GPU ONLY
# ============================================================
scene.render.engine = 'CYCLES'

cycles_addon = bpy.context.preferences.addons.get("cycles")
if cycles_addon is None:
    raise RuntimeError("Cycles add-on preferences could not be found.")

prefs = cycles_addon.preferences
prefs.compute_device_type = 'OPTIX'

if hasattr(prefs, "refresh_devices"):
    prefs.refresh_devices()
else:
    prefs.get_devices()

gpu_found = False
print("\n=== CYCLES DEVICES ===")
for device in prefs.devices:
    if device.type == 'OPTIX':
        device.use = True
        gpu_found = True
    elif device.type == 'CPU':
        device.use = False
    print(
        f"Device: {device.name} | "
        f"Type: {device.type} | "
        f"Enabled: {device.use}"
    )

if not gpu_found:
    raise RuntimeError(
        "No OptiX GPU was found. "
        "Check Edit > Preferences > System > Cycles Render Devices."
    )

scene.cycles.device = 'GPU'
print(f"Scene Cycles device: {scene.cycles.device}")
print("======================\n")

# ============================================================
# SAVE STATE
# ============================================================
saved_state = {
    'filepath':              scene.render.filepath,
    'active_camera':         scene.camera,
    'current_frame':         scene.frame_current,
    'file_format':           scene.render.image_settings.file_format,
    'color_mode':            scene.render.image_settings.color_mode,
    'color_depth':           scene.render.image_settings.color_depth,
    'engine':                scene.render.engine,
    'cycles_device':         scene.cycles.device,
    'samples':               scene.cycles.samples,
    'seed':                  scene.cycles.seed,
    'use_animated_seed':     scene.cycles.use_animated_seed,
    'use_adaptive_sampling': scene.cycles.use_adaptive_sampling,
    'use_denoising':         scene.cycles.use_denoising,
    'resolution_x':          scene.render.resolution_x,
    'resolution_y':          scene.render.resolution_y,
    'resolution_percentage': scene.render.resolution_percentage,
    'hide_render':           {},
    'hide_viewport':         {},
}
for name in HIDE_DURING_RENDER:
    obj = bpy.data.objects.get(name)
    if obj:
        saved_state['hide_render'][name]   = obj.hide_render
        saved_state['hide_viewport'][name] = obj.hide_viewport

# ============================================================
# CONFIGURE RENDER SETTINGS
# ============================================================
scene.render.image_settings.file_format = 'TIFF'
scene.render.image_settings.color_mode  = 'BW'
scene.render.image_settings.color_depth = '8'

# Resolution
scene.render.resolution_x          = RESOLUTION_X
scene.render.resolution_y          = RESOLUTION_Y
scene.render.resolution_percentage = RESOLUTION_PERCENTAGE

# Cycles quality settings
scene.cycles.samples               = SAMPLES
scene.cycles.use_adaptive_sampling = False
scene.cycles.use_denoising         = False

# Fixed seed — identical noise pattern every frame
scene.cycles.seed              = FIXED_SEED
scene.cycles.use_animated_seed = False

print(f"Resolution: {scene.render.resolution_x} x {scene.render.resolution_y} "
      f"@ {scene.render.resolution_percentage}%")
print(f"Samples: {scene.cycles.samples}")
print(f"Adaptive sampling: {scene.cycles.use_adaptive_sampling}")
print(f"Denoising: {scene.cycles.use_denoising}")
print(f"Seed: {scene.cycles.seed} (animated: {scene.cycles.use_animated_seed})\n")

# Hide calibration target etc.
for name in HIDE_DURING_RENDER:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render   = True
        obj.hide_viewport = True

# ============================================================
# RENDER LOOP
# ============================================================
try:
    start_time = time.time()

    for frame_idx, frame_num in enumerate(range(start_frame, end_frame + 1)):
        scene.frame_set(frame_num)

        frame_str = f"{frame_idx + 1:08d}"

        # Render Camera 1 → _0.tif
        scene.camera = cam1
        filename = f"{FILENAME_PREFIX}_{frame_str}_0.tif"
        scene.render.filepath = os.path.join(OUTPUT_DIR, filename)
        bpy.ops.render.render(write_still=True)

        # Render Camera 2 → _1.tif
        scene.camera = cam2
        filename = f"{FILENAME_PREFIX}_{frame_str}_1.tif"
        scene.render.filepath = os.path.join(OUTPUT_DIR, filename)
        bpy.ops.render.render(write_still=True)

        elapsed = time.time() - start_time
        pairs_done = frame_idx + 1
        avg_per_pair = elapsed / pairs_done
        eta = avg_per_pair * (total_frames - pairs_done)
        print(f"  Frame {frame_num:3d} ({pairs_done:2d}/{total_frames}) done"
              f"  [elapsed {elapsed/60:.1f}m, ETA {eta/60:.1f}m]")

    total_elapsed = time.time() - start_time
    print(f"\nCompleted in {total_elapsed/60:.1f} minutes.")

finally:
    # ============================================================
    # RESTORE STATE
    # ============================================================
    scene.render.filepath                   = saved_state['filepath']
    scene.camera                            = saved_state['active_camera']
    scene.frame_set(saved_state['current_frame'])
    scene.render.image_settings.file_format = saved_state['file_format']
    scene.render.image_settings.color_mode  = saved_state['color_mode']
    scene.render.image_settings.color_depth = saved_state['color_depth']
    scene.render.engine                     = saved_state['engine']
    scene.cycles.device                     = saved_state['cycles_device']
    scene.cycles.samples                    = saved_state['samples']
    scene.cycles.seed                       = saved_state['seed']
    scene.cycles.use_animated_seed          = saved_state['use_animated_seed']
    scene.cycles.use_adaptive_sampling      = saved_state['use_adaptive_sampling']
    scene.cycles.use_denoising               = saved_state['use_denoising']
    scene.render.resolution_x               = saved_state['resolution_x']
    scene.render.resolution_y               = saved_state['resolution_y']
    scene.render.resolution_percentage      = saved_state['resolution_percentage']

    for name in HIDE_DURING_RENDER:
        obj = bpy.data.objects.get(name)
        if obj and name in saved_state['hide_render']:
            obj.hide_render   = saved_state['hide_render'][name]
            obj.hide_viewport = saved_state['hide_viewport'][name]

    print(f"\nOutput saved to: {OUTPUT_DIR}")
    print("Scene state restored.")
