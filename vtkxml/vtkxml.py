"""
vtkxml
~~~~~~

This module provides tools for creating VTK XML files for use with ParaView and
other similar data visualization tools. It is meant to be used within a
separate post-processing script to turn raw data output into an XML file.

.. todo:: Add writer for other grid types
"""
try:
    from xml.dom import minidom as dom
except ImportError:
    # Python 2.5
    from xml.dom import ext as dom


class VtuWriter(object):
    """
    :param bit64: If true, use 64 bit value strings.

    Writer for VTK unstructured grid XML files. The primary public methods are
    :meth:`write_data_file` and :meth:`write_pvd_file`.

    Usage example:

    >>> import tempfile, os
    >>> td = tempfile.gettempdir()
    >>> w= VtuWriter()
    >>> v = {'positions': [[1, 2.5, 3], [2, 1, 3], [3.5, 1, 2]]}
    >>> s = {'temps': [1.0, 2.0, 1.5]}
    >>> w.write_data_file(os.path.join(td, 'vtu0.vtu'), s, v)

    .. todo:: Add support for cell and vert data in addition to point data
    """
    def __init__(self, bit64=False):
        self.fnames = []
        self.bit64 = bit64

    @staticmethod
    def vectors_to_string(*vectors):
        """
        :param \*vectors: A list of lists, each with an element of a vector.

        Convert a list of one or more vectors into a string, where each line
        contains one element from each of the vectors. See the example below.
        Note that the order of the elements is preserved.

        >>> print VtuWriter.vectors_to_string([1,2,3], [4,5,6])
        1 4
        2 5
        3 6
        >>> print VtuWriter.vectors_to_string([1,2,3])
        1
        2
        3
        """
        lines = []
        for v in zip(*vectors):
            lines.append(' '.join([str(i) for i in v]))
        return '\n'.join(lines)

    def guess_scalar_type(self, data):
        """
        :param data: A list of scalar data values.

        Guess the data type of the series. Assumes 32 bit values unless `bit64`
        was specified to the constructor. If a valid type cannot be found, a
        `ValueError` exception is raised.

        >>> w32 = VtuWriter()
        >>> w32.guess_scalar_type([1,2,3])
        'UInt32'
        >>> w32.guess_scalar_type([-1,2,3])
        'Int32'
        >>> w32.guess_scalar_type([1.0, 2.0, 3.0])
        'Float32'
        >>> w32.guess_scalar_type([1.0, 2, 3.0])
        'Float32'
        >>> w64 = VtuWriter(bit64=True)
        >>> w64.guess_scalar_type([1,2,3])
        'UInt64'
        >>> w64.guess_scalar_type([-1,2,3])
        'Int64'
        >>> w64.guess_scalar_type([1.0, 2.0, 3.0])
        'Float64'
        >>> w64.guess_scalar_type([1.0, 2, 3.0])
        'Float64'
        """
        # Int and UInt
        if all(type(x) is int for x in data):
            # UInt
            if all(x >= 0 for x in data):
                return 'UInt64' if self.bit64 else 'UInt32'
            else:
                return 'Int64' if self.bit64 else 'Int32'
        # Float
        if all(type(x) in (float, int) for x in data):
            return 'Float64' if self.bit64 else 'Float32'
        raise ValueError('Failed to detect valid data type')

    def guess_vector_type(self, data):
        """
        :param data: A list of vector element lists. Each list contains the
            data for a particular element of a vector.

        Guess the data type of the vector series. Behaves the same as
        `guess_scalar_type`.

        >>> w32 = VtuWriter()
        >>> w32.guess_vector_type([[1,2,3], [1,2,3]])
        'UInt32'
        >>> w32.guess_vector_type([[-1,2,3], [1,2,3]])
        'Int32'
        >>> w32.guess_vector_type([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]])
        'Float32'
        >>> w32.guess_vector_type([[1.0, 2, 3.0], [1, 2, 3]])
        'Float32'
        >>> w64 = VtuWriter(bit64=True)
        >>> w64.guess_vector_type([[1,2,3], [1,2,3]])
        'UInt64'
        >>> w64.guess_vector_type([[-1,2,3], [1,2,3]])
        'Int64'
        >>> w64.guess_vector_type([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]])
        'Float64'
        >>> w64.guess_vector_type([[1.0, 2, 3.0], [1, 2, 3]])
        'Float64'
        """
        types = [self.guess_scalar_type(col) for col in data]
        # UInt
        if all(x in ('UInt32', 'UInt64') for x in types):
            return types[0]
        # Int
        if all(x in ('Int32', 'Int64', 'UInt32', 'UInt64') for x in types):
            return 'Int64' if self.bit64 else 'Int32'
        # Float
        return 'Float64' if self.bit64 else 'Float32'

    def generate_scalar(self, doc, name, data, datatype):
        """
        :param doc: An `xml.dom.minidom.Document` object.
        :param name: Name of the data series.
        :param data: List of data series values.
        :param datatype: Data type to use for data series.

        Generates a ``<DataArray>`` XML element that contains scalar data.
        """
        scalar = doc.createElementNS('VTK', 'DataArray')
        scalar.setAttribute('Name', name)
        scalar.setAttribute('type', datatype or self.guess_scalar_type(data))
        scalar.setAttribute('format', 'ascii')
        scalar.appendChild(doc.createTextNode(self.vectors_to_string(data)))
        return scalar

    def generate_vector(self, doc, name, data, datatype):
        """
        :param doc: An `xml.dom.minidom.Document` object.
        :param name: Name of the data series.
        :param data: List of data series values.
        :param datatype: Data type to use for data series.

        Generates a ``<DataArray>`` XML element that contains vector data.
        """
        ncomp = len(data)
        vector = doc.createElementNS('VTK', 'DataArray')
        vector.setAttribute('Name', name)
        vector.setAttribute('type', datatype or self.guess_vector_type(data))
        vector.setAttribute('format', 'ascii')
        vector.setAttribute('NumberOfComponents', str(ncomp))
        vector.appendChild(doc.createTextNode(self.vectors_to_string(*data)))
        return vector

    def write_data_file(self, fn, scalars, vectors, types={}, pname='positions'):
        """
        :param fn: Filename to save XML document to, including extension.
        :param scalars: Dictionary of scalar data series.
        :param vectors: Dictionary of vector data series.
        :param types: Dictionary of type strings.
        :param pname: Positions vector series name.

        Create an XML file with filename `fn` that contains the data given.
        Data are passed in using the `scalars` and `vectors` parameters. These
        are dictionaries of the form

        ::

            {<field_name>: [<elements_1>, <elements_2>,...,<elements_n>], ...}

        for vectors and

        ::

            {<field_name>: <elements>, ...}

        for scalars, where `<elements>` and `<elements_i>` are lists of data
        values. So, for example, a bunch of particle positions might be passed
        in using a `vectors` dictionary such as

        ::

            {'positions': [[1,2,3], [1,2,3], [1,2,3]]}

        which would correspond to particles located at (1, 1, 1), (2, 2, 2),
        (3, 3, 3). Similarly, two scalar variables could be created using a
        `scalars` argument like the one given below.

        ::

            {'radius': [3, 2, 5], 'mass': [5, 8, 3]}

        In this case, the particle located at (1, 1, 1) in the `vectors`
        example would have radius `3` and mass `5`, etc.

        Data types may optionally be provided for each data series using the
        `types` parameter. Vector and scalars types are provided in a single
        dictionary in which the keys are the field names from the `vector` and
        `scalar` arguments and the values are valid VTK data type strings such
        as `UInt32` or `Float32`. Any data series that do not have types
        provided will have their types auto-detected.

        Finally, the `pname` parameter may be used to specify the name of a
        vector data series that should be treated as points in the unstructured
        grid. The default is `positions`. A points vector is required.
        """
        npts = len(vectors[pname][0])
        doc = dom.Document()
        # <VTKFile>
        root = doc.createElementNS('VTK', 'VTKFile')
        root.setAttribute('type', 'UnstructuredGrid')
        root.setAttribute('version', '0.1')
        root.setAttribute('byte_order', 'LittleEndian')
        doc.appendChild(root)
        # <UnstructuredGrid>
        ug = doc.createElementNS('VTK', 'UnstructuredGrid')
        root.appendChild(ug)
        # <Piece>
        piece = doc.createElementNS('VTK', 'Piece')
        piece.setAttribute('NumberOfPoints', str(npts))
        piece.setAttribute('NumberOfCells', '0')
        ug.appendChild(piece)
        # <Points>
        points = doc.createElementNS('VTK', 'Points')
        piece.appendChild(points)
        points.appendChild(self.generate_vector(
            doc, pname, vectors[pname], types.get(pname, None)))
        # <PointData>
        pdata = doc.createElementNS('VTK', 'PointData')
        piece.appendChild(pdata)
        for name in vectors:
            if name == pname:
                continue
            pdata.appendChild(self.generate_vector(
                doc, name, vectors[name], types.get(name, None)))
        for name in scalars:
            pdata.appendChild(self.generate_scalar(
                doc, name, scalars[name], types.get(name, None)))
        # <Cells>
        cells = doc.createElementNS('VTK', 'Cells')
        piece.appendChild(cells)
        cc = doc.createElementNS('VTK', 'DataArray')
        cc.setAttribute('type', 'Int32')
        cc.setAttribute('Name', 'connectivity')
        cc.setAttribute('format', 'ascii')        
        cells.appendChild(cc)
        connectivity = doc.createTextNode('0')
        cc.appendChild(connectivity)
        # <CellData>
        cd = doc.createElementNS('VTK', 'CellData')
        piece.appendChild(cd)
        # Write to file and exit
        with open(fn, 'w') as outfile:
            try:
                doc.writexml(outfile, newl='\n')
            except AttributeError:
                # Python 2.5
                dom.PrettyPrint(doc, outfile)
        self.fnames.append(fn)

    def write_pvd_file(self, fn):
        """
        :param fn: Filename to save PVD file to.

        Write a PVD file with filename `fn` that contains references to the
        data files previously created with this instance.
        """
        pvd = dom.Document()
        # <VTKFile>
        root = pvd.createElementNS('VTK', 'VTKFile')
        root.setAttribute('type', 'Collection')
        root.setAttribute('version', '0.1')
        root.setAttribute('byte_order', 'LittleEndian')
        pvd.appendChild(root)
        # <Collection>
        collection = pvd.createElementNS('VTK', 'Collection')
        root.appendChild(collection)
        # <DataSet> (several)
        for i, f in enumerate(self.fnames):
            ds = pvd.createElementNS('VTK', 'DataSet')
            ds.setAttribute('timestep', str(i))
            ds.setAttribute('group', '')
            ds.setAttribute('part', '0')
            ds.setAttribute('file', f)
            collection.appendChild(ds)
        with open(fn, 'w') as outfile:
            try:
                pvd.writexml(outfile, newl='\n')
            except AttributeError:
                # Python 2.5
                dom.PrettyPrint(pvd, outfile)
