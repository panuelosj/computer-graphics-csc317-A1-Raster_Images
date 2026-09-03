"""Shared, non-student helper code for the Python computer graphics course.

Students never need to edit anything in this package. It provides:

* :mod:`cgcommon.testkit`  -- the tiny test/grading backend used by every
  assignment's ``run_tests.py`` and by the grader.
* :mod:`cgcommon.image`    -- image loading (PNG) and saving (PPM/PNG).
* :mod:`cgcommon.objio`    -- Wavefront ``.obj`` reading/writing helpers.
* :mod:`cgcommon.viewer`   -- thin convenience wrappers around polyscope.
* :mod:`cgcommon.interact` -- mouse grab-and-drag picking + keyboard helpers
  for the interactive polyscope demos.
"""

__all__ = ["testkit", "image", "objio", "viewer", "interact"]
