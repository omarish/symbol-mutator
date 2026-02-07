class ndarray:
    def __init__(self, shape, dtype=float):
        self.shape = shape
        self.dtype = dtype

    def sum(self, axis=None):
        """Sum of array elements over a given axis."""
        pass

    def mean(self, axis=None):
        """Compute the arithmetic mean along the specified axis."""
        pass

def array(object, dtype=None, copy=True, order='K', subok=False, ndmin=0):
    """Create an array.
    
    :param object: An array, any object exposing the array interface.
    :param dtype: The desired data-type for the array.
    """
    return ndarray(len(object), dtype=dtype)

def eye(N, M=None, k=0, dtype=float, order='C'):
    """Return a 2-D array with ones on the diagonal and zeros elsewhere."""
    pass
