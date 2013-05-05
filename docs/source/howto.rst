Tutorial
========

This is a quick run-through of how to use vtkxml-builder to create a set of VTU
files from a set of Python lists.

So, say we have a set of particles that we want to visualize using ParaView or
something similar to that. Each particle has a three-tuple coordinate, a radius
and a temperature.

    >>> x = [1.5, 1.0, 2.5]
    >>> y = [0.5, 3.0, 2.0]
    >>> z = [2.5, 1.5, 3.0]
    >>> r = [1.0, 2.0, 1.5]
    >>> t = [0.0, 0.5, 0.5]

So now we have three lists to represent the position. The particles are located
at (1.5, 0.5, 2.5), (1.0, 3.0, 1.5), and (2.5, 2.0, 3.0). Their radii are 1.0,
2.0, and 1.5, and their temperatures are 0.0, 0.5, and 0.5.

Now we want to actually write some VTU files. We instantiate a :class:`VtuWriter`, then
call its :meth:`write_vtu_file` method and pass in our data. We use the
`scalars` parameter to pass in our scalar data series (radius and temperature)
and the `vectors` parameter to pass in our vectors. We also specify a file name
and, optionally, data types (if you don't specify types they will be guessed).
Also, note that we need to provide the name of the data series to be treated as
positions. This is a special category in VTK, so it needs to be included. The
default is "positions", so if you use that name, you don't have to specify it.

    >>> writer = VtuWriter()
    >>> scalars = {'radius': r, 'temp': t}
    >>> vectors = {'position': [x, y, z]}
    >>> writer.write_vtu_file('vtu0.vtu', scalars, vectors, pname='position')

This will write a VTU file called "vtu0.vtu" to the current directory.
Successive calls to :meth:`write_vtu_file` can then be used to create
additional files.
