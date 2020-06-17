import ctypes
import keyboard
import cv2
import numpy
import datetime

#The following code shows how to call the sdk library in the python
class NEON_DEVICE_INFO(ctypes.Structure):
    _fields_ = [('FW_VER',ctypes.c_char * 10),
				('LIB_VER',ctypes.c_char * 20),
				('VendorName',ctypes.c_char * 25),
				('DeviceModel',ctypes.c_char * 25),
				('DeviceSeriesNo',ctypes.c_char * 20),
				('DeviceType',ctypes.c_int)]

# Save img flag
bSaveImg = False

# Load C library
dll = ctypes.windll.LoadLibrary('Neon.dll')

# Open device
device_handle = dll.Neon_DeviceOpen()

# Get Device info
dll.Neon_DeviceInfo.argtypes = [ctypes.c_int, ctypes.POINTER(NEON_DEVICE_INFO)]
Python_info = NEON_DEVICE_INFO()
dll.Neon_DeviceInfo(device_handle, Python_info)

# Get Device width and height
Width = ctypes.c_uint(0)
Height = ctypes.c_uint(0)
dll.Neon_GetImageWidth(device_handle, ctypes.byref(Width))
dll.Neon_GetImageHeight(device_handle, ctypes.byref(Height))

# Print device info
print('********************')
print("FW version:" + str(Python_info.FW_VER))
print("LIB_VER:"    + str(Python_info.LIB_VER))
print("VendorName:" + str(Python_info.VendorName))
print("DeviceModel:"+ str(Python_info.DeviceModel))
print("DeviceSeriesNo:"+ str(Python_info.DeviceSeriesNo))
print("DeviceType:"    + str(Python_info.DeviceType))
print('Width=', str(Width.value), '  Height=', str(Height.value))
print('********************')

# Set callback function
# The callback function is called when a frame is ready
# Callback type; 0 = frame callback, 1 ~ 4 = DI callback
NeonCallType = 0 
Neon_SetCallback = dll.Neon_SetCallback
Neon_SetCallback.restype = None

# Declaration in C
# typedef void (__stdcall *NEONCALLBACK)(int Handle, int Type, void* Buffer, int Size);
NEONCBFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int)

# Declaration in C
#int PASCAL Neon_SetCallback(int Handle, int Type, NEONCALLBACK Fun);
def py_neon_callback_func(neon_handle, callback_type, frame_buffer, frame_size):
	global bSaveImg, Width, Height

# Save image
	if bSaveImg == True:
		bSaveImg = False		
		imgPath = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+'.png'
		b_imgPath = imgPath.encode('utf-8')
		ret = dll.Neon_SaveImage(neon_handle, b_imgPath, frame_buffer)
		print('--Neon_SaveImage '+ str(ret))				

# Get data from ctypes array into numpy
	buffer_from_memory = ctypes.pythonapi.PyMemoryView_FromMemory
	buffer_from_memory.restype = ctypes.py_object
	buffer = buffer_from_memory(frame_buffer, frame_size)
	imgData = numpy.frombuffer(buffer, numpy.uint8)
	imgData = imgData.reshape(Height.value, Width.value)		

# Preview
	cv2.imshow('img',imgData)
	cv2.waitKey(10)	
	return 0

# SetCallback
neon_callback_func = NEONCBFUNC(py_neon_callback_func)
Neon_SetCallback(device_handle, NeonCallType, neon_callback_func)

def Neon_control(input_dll,input_device):	
	global bSaveImg
	while(True):
		print('Input: 1,2,3 or 4 (1.Acquisition Start. 2.Acquisition Stop. 3.Save Image 4.exit)')
		input = keyboard.read_key()
		if input== '1':			
			# The number of frames to be captured: 
			# 0: continuous
			ret = input_dll.Neon_AcquisitionStart(input_device,0)
			print('--Neon_Acquisition Start: '+ str(ret))			
		elif input == '2':
			ret = input_dll.Neon_AcquisitionStop(input_device)
			print('--Neon_Acquisition Stop: '+ str(ret))
			
		elif input == '3':
			bSaveImg = True		
			cv2.waitKey(500)
		else:
			print("Exiting\n")
			cv2.destroyAllWindows()
			exit(0)					

Neon_control(dll,device_handle)