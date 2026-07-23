Release Notes
=============

Release 0.4.0 (2026-06-04)
--------------------------

- Add strike angle to output metrics
- Continue update to Python 3.12
- Add check for number of points before Delaunay crashes on trend lines
- Ignore segments of zero length to prevent warning from numpy
- Have consistency in output labels: name, vs data name vs data group name
- Refresh screenshots of UIJsons in docs


Release 0.3.0 (2026-01-09)
--------------------------

- Migrate peak-finder to curve-apps


Release 0.2.0 (2025-02-07)
--------------------------

- Replace geoapps-edge detection code for curve-apps.edge_detection
- Freeze parameters and update InputFile data on BaseData construction
- Make the canny add_data optional on get_edges method
- Move Contouring app to curve-apps repo
- Use scikit-image.measure instead of matplotlib contours
- Formalize out_group as empty string or UIJsonGroup selector
- Do not include top level files in wheels

Release 0.1.0 (2024-04-17)
--------------------------

**(First release)**

New features
^^^^^^^^^^^^

- Add metrics to edge detection.
- Migration of Edge Detection application from MiraGeoscience/geoapps.git
- Add Trend Line application for detection lines from point data.
- Add azimuth based filters on Trend Lines
- Create documentation
