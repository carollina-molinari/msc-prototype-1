import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.gridspec as gridspec
from time import sleep
from datetime import datetime
from checking_lum import checando_luminosidade
from checking_picamera import imageamento_picamera
from histogramas_func import histogramas_rgb_hsv_lab
from nuvem import nuvem
import math
import os
import subprocess
import time

plt.rc('xtick', labelsize=8)    
plt.rc('ytick', labelsize=8)

# Start GUI
root = tk.Tk()
root.geometry('+%d+%d'%(10,30))
root.wm_title("Digital Imaging Tool - Wine Samples")

# This removes the maximize button
root.resizable(0,0)

# Header Area
header = Frame(root, width=875, height=70)
header.grid(columnspan=3, rowspan=2, row=0)

# Top Area
main_content = Frame(root, width=875, height=220, bg="MistyRose3")
main_content.grid(columnspan=3,rowspan=2,row=2)

# Lower Area
lower_content = Frame(root, width=875, height=240, bg="thistle")
lower_content.grid(columnspan=3,rowspan=2,row=4)

# Wine logo
logo_wine = Image.open('wine_rgb.png'). #you can add your own image here
logo_wine = logo_wine.resize((50,50))
logo_wine = ImageTk.PhotoImage(logo_wine)
logo_wine_label = tk.Label(image=logo_wine)
logo_wine_label.image = logo_wine
logo_wine_label.place(x=10, y=10)

# First instructions        
instructions = tk.Label(root, text="Nome da análise (uva-ano-id): ", font="Realway")
instructions.place(x=100, y=25)             
now = datetime.now()
data_medicao = now.strftime("%d_%m_%Y_%H_%M_%S")

# Message box for instructions
def clicker():

    instrucoes = "Para utilizar essa ferramenta com êxito, siga as seguintes etapas: \
    \n 1) Com a amostra de vinho devidamente alocada, insira o nome no campo em branco e clique no botão <Pronto!> \
    \n 2) Automaticamente, serão verificadas as condições de luminosidade e de configuracao da picamera. \
    \n 3) Se as condições estiverem apropriadas, você verá em alguns segundos, a imagem capturada da amostra\
    \n 4) Aguarde mais alguns instantes, enquanto os histogramas RGB, HSV e L*a*b* estão sendo calculados \
    \n 5) Após finalizada a análise, não se preocupe pois todas as análises foram salvas automaticamente no dropbox.\
    \n Boas análises! :-) "

    global pop
    pop = Toplevel(root)
    pop.title("Read me")
    pop.geometry('+%d+%d'%(10,30))
    pop.wm_title("Como usar essa ferramenta?")
    pop.resizable(0,0)
    header = Frame(pop, width=875, height=100)
    pop.config(bg="MistyRose4")
    pop.label = Label(pop, text=instrucoes, bg="MistyRose4", fg="white", font=("Helvetivca", 10))   
    pop.label.pack(pady=10)
    
    
#Read me Button
    
readme_text = tk.StringVar()
readme_btn = tk.Button(root, image=logo_wine, command=lambda:clicker(), font="Raleway")
readme_text.set("Read me")
readme_btn.place(x=10, y=10)


# Text box to write the wine sample name 
text_box = tk.Text(root, height=1,width=40)
text_box.place(x=350,y=25)

# retrieve_input: checks if the written name is valid (more than 3 letters)
# if valid, continue with the next functions

def format_axes(fig):
    for i,ax in enumerate(fig.axes):
        ax.tick_params(labelsize=8)

def retrieve_input():
    nome_analise_input=text_box.get("1.0","end-1c")
    text_box.config(state='disabled')
    browse_btn.config(state='disabled')
    browse_text.set("Pronto!")
    nome_analise_input= nome_analise_input.replace(" ","")

    #print(nome_analise_input)
    if len(nome_analise_input)>3:
        print('Nome Ok! Seguir com Análise de Luminosidade')
        check_luminosity_text=Label(root, text='Checando luminosidade...      ', bg="MistyRose3", fg='white').place(x=50, y=77)
        plot_lux(50,100, nome_analise_input)

    else:
        l2.grid(column=3,row=0)
        text_box.config(state='normal')
        browse_btn.config(state='normal')
        browse_text.set("Digite novamente")

    return nome_analise_input

# Click button
browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, command=lambda:retrieve_input(), font="Raleway", bg='MediumPurple4', fg='white')
browse_text.set("Confirmar")
browse_btn.place(x=680, y=18)

# For future PCA analysis implementation
#def pca_window():
#    window = Tk()
#    window.title("PCA analysis")
#    header_pca = Frame(window, width=1000, height=570)
#    header_pca.grid(columnspan=3, rowspan=2, row=0)
#    window.geometry('+%d+%d'%(200,50))
#    label_02=Label(window,text='loadings and escores', relief="solid").place(x=50,y=100)
#    sair_btn=tk.Button(window, text='Fechar', command=lambda:window.destroy(), width=8, bg='MediumPurple4').place(x=900,y=500)

def plot_histogramas(nome_analise_input):

    print("Iniciando a etapa de identificação e obtenção dos histogramas de cores da amostra...")
    cut, h, s, v, r, g, b = histogramas_rgb_hsv_lab(nome_analise_input)
    text_recorte = "Recorte"
    recorte = Image.open(cut)
    recorte = recorte.resize((175,130))
    recorte = ImageTk.PhotoImage(recorte)
    recorte_label = tk.Label(image=recorte)
    recorte_label.image = recorte
    recorte_label.place(x=625, y=120)
    recorte_titulo = Label(root,text=text_recorte, bg="MistyRose3", fg = 'white').place(x=695,y=77)
   
    # Plot RGB
    style.use("ggplot")
    y1 = r
    y2 = g
    y3 = b
    fig = Figure(figsize=(2.5,1.7), dpi=100)
    fig.patch.set_facecolor('thistle')
    fig.patch.set_alpha(1)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(y1, 'r', label="r")
    ax.plot(y2, 'g', label="g")
    ax.plot(y3, 'b', label="b")
    ax.legend()
    ax.ticklabel_format(style='sci',scilimits=(0,0),axis='y')
    ax.yaxis.major.formatter_useMathText = True
    ax.tick_params(axis='y', labelsize=5)
    ax.set_title("RGB", fontsize=12)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().place(x=50,y=315)
    
    # Plot HSV
    style.use("ggplot")
    y1 = h
    y2 = s
    y3 = v
    fig = Figure(figsize=(2.5,1.7), dpi=100)
    fig.patch.set_facecolor('thistle')
    fig.patch.set_alpha(1)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(y1, label="h")
    ax.plot(y2, label="s")
    ax.plot(y3, label="v")
    ax.legend()
    ax.ticklabel_format(style='sci',scilimits=(0,0),axis='y')
    ax.yaxis.major.formatter_useMathText = True
    ax.tick_params(axis='y', labelsize=5)
    ax.set_title("HSV", fontsize=12)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().place(x=325,y=315)
    
    root.config(cursor="")

    #histogramas_title=Label(root, text='Histogramas', bg='thistle', fg='white').place(x=370, y=290)

def picture_picamera(nome_analise_input):
    dados_picamera = imageamento_picamera(nome_analise_input)
    #print(dados_picamera[0])
    if dados_picamera[1] == [0,0,0]:
        picamera_status=Label(root, text='OK', bg='dark sea green').place(x=500, y=77)
        text_foto_vinho = "Imagem da amostra: " + str(nome_analise_input)
        foto_vinho_titulo=Label(root, text=text_foto_vinho, bg='MistyRose3', fg='white', font=(None,8)).place(x=355, y=255)
        foto_vinho = Image.open(dados_picamera[0])
        foto_vinho = foto_vinho.resize((175,130))
        foto_vinho = ImageTk.PhotoImage(foto_vinho)
        foto_vinho_label = tk.Label(image=foto_vinho)
        foto_vinho_label.image = foto_vinho
        foto_vinho_label.place(x=355,y=120)
        main_content.update_idletasks()
        # Call plot_histogramas function that will plot all the color histogram
        plot_histogramas(nome_analise_input)
        plt.close('all')
        #PCA button
        #pca_btn_text = tk.StringVar()
        #pca_btn = tk.Button(root, command=lambda:pca_window(), textvariable=pca_btn_text, font="Raleway", bg='MediumPurple4', fg='white')
        #pca_btn_text.set("PCA")
        #pca_btn.place(x=940, y=530)
    else:
        picamera_status=Label(root, text='Não', relief="solid", bg='maroon', fg='white').place(x=500, y=77)
        message_error=Label(root, text='A análise não será realizada devido à \n condições inapropriadas de estabilização da picamera. \n Por favor, verifique as condições e tente novamente', bg='maroon', fg='white', font=12).place(x=375, y=150)

def plot_lux(x2,y2,nome_analise_input):

    dados_sensores = checando_luminosidade(nome_analise_input)
    style.use("ggplot")
    time_data = [1,2,3,4,5]
    lum_data = dados_sensores[1]
    count=0
    for lum in lum_data:
        lum = round(lum,2)
        lum_data[count] = lum
        count +=1
        
    #print(lum_data)
    luminosidade_media = int(dados_sensores[0])
    fig = Figure(figsize=(2.5,1.7),dpi=100)
    fig.patch.set_facecolor('rosybrown')
    fig.patch.set_alpha(0.65)
    ax = fig.add_subplot(1, 1, 1)
    format_axes(fig)
    ax.plot(time_data, lum_data, marker='o')
    ax.tick_params(axis='y', labelsize=8)
    ax.set_title('[s] vs [lux]', y=1.0, pad=-4, fontsize=8)
    ax.set_ylim([500,650])

    #ax.ticklabel_format(style='sci',scilimits=(0,0),axis='y')
    #ax.yaxis.major.formatter_useMathText = True
    #ax.set_xlabel('[s]')
    #ax.set_ylabel('[lux]')
    plotcanvas = FigureCanvasTkAgg(fig, root)
    plotcanvas.get_tk_widget().place(x=x2,y=y2)
    plt.close('all')
    # luminosidade_media>550 is the minimum condition to take a picture! You can change this if you want :-)
    if luminosidade_media > 200:
        root.config(cursor="watch")
        #print("Luminosidade média acima de 550, seguindo com a captura da imagem...")
        luminosity_status=Label(root, text='OK', bg='dark sea green').place(x=258, y=77)
        check_luminosity_text=Label(root, text='Checando picamera...', bg='MistyRose3', fg='white').place(x=355, y=77)
        plotcanvas.draw()
        picture_picamera(nome_analise_input)
    else:
        luminosity_status=Label(root, text='Não', bg='maroon', fg='white').place(x=258, y=77)
        message_error=Label(root, text='A análise não será realizada devido à \n condições inapropriadas de luminosidade. \n Por favor, verifique as condições e tente novamente', bg='maroon', fg='white', font=12).place(x=375, y=150)

# Restarting GUI    
def restart_program():
    root.destroy()
    subprocess.call(["xdg-open","gui_wines_experiment.pyw"])
    subprocess.call(["python3","gui_wines_experiment.pyw"])

# Again button
again_text = tk.StringVar()
again_btn = tk.Button(root, textvariable=again_text, command=lambda:restart_program(), font="Raleway", bg='MediumPurple4', fg='white')
again_text.set("Só mais uma!")
again_btn.place(x=730, y=490)
    
# End GUI
root.mainloop()

