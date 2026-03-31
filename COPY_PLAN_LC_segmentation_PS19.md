# TIF Copy Plan: Reorganize to Two-Level Folder for LC_segmentation_PS19

## Summary

- **Source:** `20X Images/` (three-level: Condition / Age / Sample ID / *.tif)
- **Destination:** `/research/dept/dnb/core_operations/OmeroData/schwagrp/jlee32/LC_segmentation_PS19/` (two-level: Condition / *.tif)
- **Total files to copy:** 255 TIF files (excluding files under `Cellpose Images and ROIs`)
- **Naming:** Each file is renamed to `{original basename} {AgeCompact}.tif` (e.g. `3 Months` → `3Months`)

## Folder mapping

| Source (level 1) | Destination folder |
|------------------|---------------------|
| Control Mice     | Control             |
| PS19 Mice        | PS19                |

## File count by destination

| Destination folder | File count |
|--------------------|------------|
| Control            | 105        |
| PS19               | 150        |
| **Total**          | **255**    |

## Naming example

| Source path | Destination path |
|-------------|-------------------|
| `.../Control Mice/3 Months/241/241 Slide 2 Section A2.tif` | `.../LC_segmentation_PS19/Control/241 Slide 2 Section A2 3Months.tif` |

## Full file list (source → destination)

The complete list of 255 mappings is in **`copy_plan_mapping.txt`** (one line per file: `source|destination`).

### Sample — first 10 (PS19)

```
.../PS19 Mice/4 Months/187/187 Slide 1 Section A2.tif  →  .../PS19/187 Slide 1 Section A2 4Months.tif
.../PS19 Mice/4 Months/187/187 Slide 1 Section D2.tif   →  .../PS19/187 Slide 1 Section D2 4Months.tif
.../PS19 Mice/4 Months/183/183 Slide 2 Section D1.tif  →  .../PS19/183 Slide 2 Section D1 4Months.tif
... (252 more)
```

### Sample — Control (your example)

```
.../Control Mice/3 Months/241/241 Slide 2 Section A2.tif  →  .../Control/241 Slide 2 Section A2 3Months.tif
```

## How to run the copy

```bash
cd "/research/dept/dnb/core_operations/ImageAnalysisScratch/Schwarz/Jimin/20X Images"
chmod +x copy_tif_reorganize.sh
./copy_tif_reorganize.sh
```

The script reads `copy_plan_mapping.txt`, creates `Control/` and `PS19/` under the destination, and copies each file with the new name.
