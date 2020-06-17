import ctypes

# reference https://docs.python.org/3.6/library/ctypes.html#callback-functions

libc = ctypes.cdll.msvcrt
IntArray5 = ctypes.c_int * 5
ia = IntArray5(5, 1, 7, 33, 99)
qsort = libc.qsort
qsort.restype = None

#declaire
#void qsort(void *base, size_t nitems, size_t size, int (*compar)(const void *, const void*))
CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))

def py_cmp_func(a, b):
	print("py_cmp_func", a[0], b[0])
	return 0

cmp_func = CMPFUNC(py_cmp_func)
qsort(ia, len(ia), ctypes.sizeof(ctypes.c_int), cmp_func) 

for i in ia: print(i, end=" ")