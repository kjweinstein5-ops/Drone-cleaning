"""Stage 3 — Surface & asset segmentation.

Identifies what each face is: solar / window / tile / shingle / stucco / gutter /
roof — or an EXCLUSION zone (chimney, HVAC, person) that gets no spray.

Three signals, fused conservatively (docs/3D_DATA_PIPELINE.md §4):
  A. RGB semantic classification (BUY the backbone, BUILD the labels)
  B. Deterministic geometry rules from the mesh (plane/normal/height/edge)
  C. Thermal signature (condition + HVAC/vent disambiguation)

Conflicts resolve to the most pressure-sensitive class. Safety over coverage.
"""
