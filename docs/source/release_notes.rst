Release Notes
=============

Release 0.4.0 (2026-06-04)
--------------------------

- GEOPY-2588: Add strike angle to output metrics
- GEOPY-2741: Continue update to Python 3.12
- GEOPY-1513: Add check for number of points before Delaunay crashes on trend lines
- GEOPY-2608: Ignore segments of zero length to prevent warning from numpy
- GEOPY-2759: have consistency in output labels: name, vs data name vs data group name
- GEOPY-2745: Refresh screenshots of UIJsons in docs


Release 0.3.0 (2026-01-09)
--------------------------

- GEOPY-2491: Migrate peak-finder to curve-apps


Release 0.2.0 (2025-02-07)
--------------------------

- GEOPY-1484: Replace geoapps-edge detection code for curve-apps.edge_detection
- GEOPY-1529: Freeze parameters and update InputFile data on BaseData construction
- GEOPY-1527: Make the canny add_data optional on get_edges method
- GEOPY-761: Move Contouring app to curve-apps repo
- GEOPY-1551: Use scikit-image.measure instead of matplotlib contours
- GEOPY-1582: Formalize out_group as empty string or UIJsonGroup selector
- GEOPY-1860: do not include top level files in wheels

Release 0.1.0 (2024-04-17)
--------------------------

**(First release)**

New features
^^^^^^^^^^^^

- GEOPY-292: Add metrics to edge detection.
- GEOPY-768: Migration of Edge Detection application from MiraGeoscience/geoapps.git
- GEOPY-1310: Add Trend Line application for detection lines from point data.
- GEOPY-1348: Add azimuth based filters on Trend Lines
- GEOPY-1400: Create documentation
