# Synthetic DIC-FE Validation

Supporting code and data for a dissertation project developing a synthetic
Digital Image Correlation validation workflow using finite-element
simulation and Blender rendering.

## Repository Structure

- `gmsh/` - specimen geometry and mesh generation
- `moose/` - finite-element model input and Exodus output
- `pyvista/` - surface extraction, node mapping, UV generation and deformation processing
- `blender/` - geometry import, camera setup, deformation animation and rendering

## Workflow

Gmsh -> MOOSE -> PyVista -> Blender

The repository contains the main workflow scripts used during development.
Additional verification and utility scripts may be added as the project continues.
