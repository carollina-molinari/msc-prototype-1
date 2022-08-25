#Loading the packages

import picamera
import time
import numpy as np
from fractions import Fraction
from nuvem import nuvem

# Taking the picture 
                 
# Especifing the "slowly" stabilization conditions for taking the picture in picamera
            
def calibration_set(ss, awb, es):
    teste = []
    speed = 9985
    awbgains = (Fraction(5, 4), Fraction(179, 256))
    if ss != speed:
        print("Error in camera.shutter_speed:", ss)
        print("Expected value:", speed)
        teste.append(1)
    else:
        teste.append(0)
    if awb != awbgains:
        print("Error in camera.awb_gains:", awb)
        print("Expected value:", awbgains)
        teste.append(1)
    else:
        teste.append(0)
    if es != speed:
        print("Error in camera.exposure_speed:", es)
        print("Expected value:", speed)
        teste.append(1)
    else:
        teste.append(0)

    return teste
            
def imageamento_picamera(nome_analise_input):
    with picamera.PiCamera() as camera:
        h = 2500 # change this to anything < 2592, anything over 2592 will likely get a memory wrror when plotting 
        camera_res = (int(h), int(0.75*h)) # keeping the natural 3/4 resolution of the camera
        # we need to round to the nearest 16th and 32nd (requirement for picamera)
        camera_res = (int(16*np.floor(camera_res[1]/16)), int(32*np.floor(camera_res[0]/32)))
        camera.resolution = (camera_res[1],camera_res[0])
        # Set ISO to the desired value
        # To fix exposure time, set the shutter_speed attribute to a reasonable value.
        camera.iso = 100
        camera.exposure_mode = 'off'
        time.sleep(1)
        camera.shutter_speed = 10000
        # To fix exposure gains, let analog_gain and digital_gain settle on reasonable values, then set exposure_mode to 'off'.
        camera.exposure_compensation = 0
        #To fix white balance, set the awb_mode to 'off', then set awb_gains to a (red, blue) tuple of gains.
        camera.awb_mode = 'off'
        camera.awb_gains = (Fraction(5, 4), Fraction(179, 256))
        time.sleep(5)
        #print(camera.awb_gains)
        camera.zoom = (0, 0.25, 1.0, 0.5)
        camera.brightness = 59
        camera.sharpness = 0
        camera.contrast = 0
        camera.saturation = 0
        # defining the output format of the file - I selected '.png'
        fileName = nome_analise_input + '.png'
        teste = calibration_set(camera.shutter_speed, camera.awb_gains, camera.exposure_speed)
        # If pass in consistent test, take the picture 
        if teste == [0,0,0]:
            #print("Pass in consistent test!")
            # The picamera will save the picture taken in the path defined bellow 
            camera.capture('adicionar aqui o seu caminho de rede'+ fileName, format='png')
            print("Imagem capturada!")
            #print(parameters_camera)
        else:
            sys.exit("Não passou no teste de consistência...")
    
    nuvem(fileName)
    return fileName, teste

