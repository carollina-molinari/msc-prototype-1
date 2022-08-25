import time
from datetime import datetime
import spidev
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
from PIL import Image
import numpy as np
import math
from matplotlib import style
from nuvem import nuvem

# Analysis timing
time_analysis_sec = 5

# Configurating the sensors
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

# TMT36
tempChannel = 1
# sparkfun light sensor = TEMT6000
sf_lightChannel = 0
sleepTime = 1

def getReading(channel):
    rawData = spi.xfer([1,(8+channel)<<4,0])
    processedData = ((rawData[1]&3)<< 8)+ rawData[2]
    return processedData

def convertVoltage(bitValue,decimalPlaces=3):
    voltage = (bitValue * 3.3) / float(1023)
    voltage = round(voltage, decimalPlaces)
    return voltage

def convertTemp(bitValue, decimalPlaces=3):
    temperature = ((bitValue * 330)/float(1023) - 50)
    temperature = round(temperature, decimalPlaces)
    return temperature

def format_axes(fig):
    for i, ax in enumerate(fig.axes):
        ax.tick_params(labelbottom=False, labelleft=False)

def checando_luminosidade(nome_analise):
    nome_analise_input = nome_analise
    style.use("ggplot")
    plt.ion()
    fig = plt.figure(figsize=(5,5), dpi=100)
    gs1 = gridspec.GridSpec(2,1)
    ax1 = fig.add_subplot(gs1[0])
    ax2 = fig.add_subplot(gs1[1])
    ax1.set_xlim(0,time_analysis_sec)
    ax2.set_xlim(0,time_analysis_sec)
    ax1.set_xlabel("time [s]", fontsize=8)
    ax1.set_ylabel("illuminance [lux]", fontsize=8)
    ax1.set_title("TEMT6000", fontsize=12)
    ax2.set_xlabel("time [s]", fontsize=8)
    ax2.set_ylabel("Temperature [°C]", fontsize=8)
    ax2.set_title("TEMP036", fontsize=12)
    dados_luminosidade_lux = list()
    dados_temperatura = list()

    # Saving the temperature and luminosity data into a .txt file 
    with open('dados_luminosidade_temperatura.txt','a') as f:
        f.write(nome_analise_input)
        f.write("\n")
        f.write("Dados de luminosidade e temperatura")
        i=1
        while i < (time_analysis_sec+1):
            # TEMT6000 - reading light data
            lightData_sp = getReading(sf_lightChannel)
            # TEMT6000 - voltage light data 
            lightVoltage_sp = convertVoltage(lightData_sp)
            # TEMT6000 - converting voltage to current
            current_temt = lightVoltage_sp/10000
            microamps = current_temt*1000000
            # TEMT6000 - converting microamps to illuminance (I = (1/2)*lx + 0)
            lx = microamps*2
            # TMP36 - reading sensor
            tempData = getReading(tempChannel)
            # TMP36 - voltage
            tempVoltage = convertVoltage(tempData)
            # TMP36 - temperature C
            temperature = convertTemp(tempData)
            # Printing outputs
            #li_data= ("Resistance = {} kohm; Lux{} lx".format(\
            #    resistance,lux_ldr))
            li_data_sp= ("Current = {} microamp; Lux = {} lx".format(microamps, lx))
            sleep(sleepTime)
            #print(li_data_sp, temperature)
            dados_luminosidade_lux.append(lx);
            dados_temperatura.append(temperature);
            ax1.scatter(i,lx);
            ax2.scatter(i,temperature);
            plt.tight_layout()
            plt.pause(0.0001)
            f.write("Medição número = {}".format(str(i)))
            f.write("\n")
            f.write("Luminosidade = {} amps".format(str(microamps)))
            f.write("\n")
            f.write("Luminosidade = {} lx".format(str(lx)))
            f.write("\n")
            f.write("Temperatura = {} C".format(str(temperature)))
            f.write("\n")
            sleep(sleepTime)
            i = i + 1
    f.close()
    sum_lx = 0

    for element in dados_luminosidade_lux:
        sum_lx = sum_lx + element

    mean_lx = sum_lx/len(dados_luminosidade_lux)
    nome_graf_lum = nome_analise_input + '.png'
    plt.savefig(nome_graf_lum, bbox_inches='tight')
    nuvem(nome_graf_lum)
    #print("Gráfico de output dos sensores salvo")

    if mean_lx > 550:
        print("Condição de luminosidade ok! Média igual a {}".format(mean_lx))

    else:
        print("Condição inapropriada!Média igual a {}".format(mean_lx))

    nuvem('dados_luminosidade_temperatura.txt')
    return mean_lx, dados_luminosidade_lux


  
