"""Geometry layer — Stage 1 of the drone-scan pipeline.

Turns a photogrammetry (or future LiDAR) reconstruction into a mesh of faces
the rest of the pipeline consumes. Source-agnostic by design: swap SfM for
LiDAR without touching Stage 2+. See docs/3D_DATA_PIPELINE.md §8.
"""
