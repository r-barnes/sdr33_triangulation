sdr33_triangulation
===================

The Sokkia SDR33 data logger is used in surveying to record data from and to
control certain total stations.

A total station works by firing a laser pulse at a distant object and recording
the length of time it takes for the pulse to return. This can be used to
calculate the distance to the object. Since the total station also records the
angles at which the pulse is fired, the distant object can be located in 3D
space.

Some total stations can record the laser's reflection off of a variety of
surfaces, but, more commonly, the total station requires the use of a special
mirror or "prism" for the reflection to work.

Situations arise where a point to be surveyed cannot be accessed with the
prism. The location of such points cannot be directly determined.

However, the location of such a point can be triangulated by moving the total
station to two different points and measuring angles to the unknown point.

Since the SDR33 data logger does not have a triangulation option built in, this
program reads the SDR33 data and returns the triangulated position of one or
more points.
