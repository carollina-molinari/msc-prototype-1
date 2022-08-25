import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
from PIL import Image
import numpy as np
import cv2
import pandas as pd
from pandas import DataFrame
from numpy import mean
from nuvem import nuvem
import csv
from csv import writer


# Color histograms
    
def histogramas_rgb_hsv_lab(fileName):
    #print("Obtaining the color histograms for the sample...")
       
    # Defining the image that will be analysed
    # fileName = name of the picture taken by picamera
    dt_string = fileName
    core_input_fig = fileName + '.png'
       
    # Reading the colored image
    #font = cv2.FONT_HERSHEY_COMPLEX
    img_camera = cv2.imread(core_input_fig,cv2.IMREAD_COLOR) 

    # Read the same image in another variable and converting to gray scale
    img_gray = cv2.imread(core_input_fig, cv2.IMREAD_GRAYSCALE)

    # Converting image to a binary image (B&W)
    # cv2.thresholds has two outputs = retval (=threshold estimated from Otsu method) and the thresholded image
    ret,threshold = cv2.threshold(img_gray,0,255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    #print("threshold value:",ret)

    name_thresh = fileName + "binimg.png"
    cv2.imwrite(name_thresh,threshold)
    #nuvem(name_thresh)

    # Find contours of the thresholded image
    cnts,_ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea)

    # Contour filtering to get the largest area (---> glass cuvette filled with wine)    
    area_tresh = 0
    for cnt in cnts:
        area = cv2.contourArea(cnt)
        if area > area_tresh:
            area = area_tresh
            big_contour = cnt

    #cv2.drawContours(img_camera,[big_contour],0,(255,0,0),14)
            
    # Compute the center of the contour
    H,W = img_camera.shape[:2]
    M = cv2.moments(big_contour)
    cX = int(M["m10"] / M["m00"])
    #print(cX)
    cY = int(M["m01"] / M["m00"])
    #print(cY)

    # Calculating a rectange inside the big_contour found
    # I put a tolerance to avoid compute the glass and shadow
    # x,y,w,h = cv2.boundingRect(big_contour)
    # In this command the crop is the same area for all the images, centered by centroid
    cut_pixels = img_camera[cY-500:cY+500,cX-200:cX+200,:]
    # Saving the image for counting the pixels 
    name_pixels = dt_string + "pixels.png"
    cv2.imwrite(name_pixels,cut_pixels)
    img_pixels=cv2.imread(name_pixels,0)
    ret_pixel,thresh_pixel=cv2.threshold(img_pixels,133,255,cv2.THRESH_BINARY_INV)
    print("Number of pixels(Must be equal = 400000) = ".format(),cv2.countNonZero(thresh_pixel))

    # Drawing the rectange in the cut portion of the cuvette
    cv2.rectangle(img_camera, (cX-200, cY-500), (cX+200, cY+500),(0,255,255),14)

    # Draw the the center of the shape on the image
    passo_x = int(100*W/cX)
    #print(passo_x)
    passo_y = int(100*H/cY)
    #print(passo_y)
    tamanho_quadrado = int(1*(passo_x+passo_y)/2)
    #print(tamanho_quadrado)
    cv2.circle(img_camera, (cX, cY), 15, (255, 255, 255), -1)
    cv2.putText(img_camera, "", (cX-int(tamanho_quadrado), cY-int(tamanho_quadrado)),
    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
    
    # Saving the picture with centroids

    name_centroides = dt_string + "centroids.png"
    cv2.imwrite(name_centroides,img_camera)
    nuvem(name_centroides)
    
    # Showing the outlined image. 
    #cv2.imshow('image_outlined', img_camera)
        
    ## Creating a mask and do bitwise-op (removing the background)
    mask = np.zeros(img_gray.shape[:2],np.uint8)
    cv2.drawContours(mask, [cnt],-1, 255, -1)
    dst = cv2.bitwise_and(img_camera, img_camera, mask=mask)

    ## Display the image cropped with mask and save it 
    name_corte = dt_string + "cut.png"
    cv2.imwrite(name_corte, dst)
    nuvem(name_corte)
    
    # Creating functions for calling the graphs

    # Function that outputs a gray histogram chart

    def gray_histogram_pic(image,ax,title, x, y):
        # histr is a 256x1 array, each value corresponds to number of pixels in that image with its corresponding pixel value.
        histr = cv2.calcHist([image],[0],None,[256],[0,256])
        histr_transp = np.transpose(histr)
                      
        ax.plot(histr)
        ax.locator_params(nbins=3)
        ax.set_xlabel(x, fontsize=10)
        ax.set_ylabel(y, fontsize=10)
        ax.tick_params(axis='both', labelsize=10)
        ax.set_title(title, fontsize=12)
        c_hist = histr
        return c_hist

    # Function that outputs a color histogram chart, RGB channels   

    # Important info, in the rgb_histogram, picture must be in **rgb** not in bgr
    # If you want to insert a bgr image, you need to change color = ('b','g','r')
    
    def rgb_histogram(image,ax,title,x,y):
        color = ('r','g','b')
        for i,col in enumerate(color):
            histr = cv2.calcHist([image],[i],None,[256],[0,256])
            histr_trans = np.transpose(histr)
            ax.plot(histr,color = col)
            plt.xlim([0,256])

        ax.locator_params(nbins=3)
        ax.set_xlabel(x, fontsize=10)
        ax.set_ylabel(y, fontsize=10)
        ax.tick_params(axis='both', labelsize=10)
        ax.ticklabel_format(style='sci',scilimits=(-3,5),axis='both')
        ax.yaxis.major.formatter_useMathText = True
        ax.set_title(title, fontsize=12)
        # canais para plotar na GUI
        r_histr = cv2.calcHist([image],[0],None,[256],[0,256])
        g_histr = cv2.calcHist([image],[1],None,[256],[0,256])
        b_histr = cv2.calcHist([image],[2],None,[256],[0,256])

        return r_histr, g_histr, b_histr

    # Function that outputs a hsv histogram
    # Important info, in the rgb_histogram, picture must be in **rgb** not in bgr
    # If you want to insert a bgr image, you need to change hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    
    def hsv_histogram(image, ax, title):
        hsv = cv2.cvtColor(image,cv2.COLOR_RGB2HSV)
        hue_hist = cv2.calcHist([hsv],[0],None,[180],[0,180])
        sat_hist = cv2.calcHist([hsv],[1],None,[256],[0,256])
        val_hist = cv2.calcHist([hsv],[2],None,[256],[0,256])
        hue_hist_t = np.transpose(hue_hist)
        sat_hist_t = np.transpose(sat_hist)
        val_hist_t = np.transpose(val_hist)

        ax.plot(hue_hist)
        ax.plot(sat_hist)
        ax.plot(val_hist)
        ax.locator_params(nbins=3)
        #ax.set_xlabel(x, fontsize=10)
        #ax.set_ylabel(y, fontsize=10)
        ax.tick_params(axis='both', labelsize=10)
        ax.ticklabel_format(style='sci',scilimits=(-3,5),axis='both')
        ax.yaxis.major.formatter_useMathText = True
        ax.set_title(title, fontsize=12)
        return hue_hist, sat_hist, val_hist

    #def cielab_histogram(image,ax,title):
    #    cielab = cv2.cvtColor(image, cv2.COLOR_RGB2Lab)
    #    L_hist = cv2.calcHist([cielab],[0],None,[256],[0,256])
    #    a_hist = cv2.calcHist([cielab],[1],None,[256],[0,256])
    #    b_hist = cv2.calcHist([cielab],[2],None,[256],[0,256])
    #    L_hist_t = np.transpose(L_hist)
    #    a_hist_t = np.transpose(a_hist)
    #    b_hist_t = np.transpose(b_hist)
    #
    #    ax.plot(L_hist)
    #    ax.plot(a_hist)
    #    ax.plot(b_hist)
    #    ax.locator_params(nbins=3)
    #    ax.set_xlabel(x, fontsize=10)
    #    ax.set_ylabel(y, fontsize=10)
    #    ax.tick_params(axis='both', labelsize=10)
    #    ax.ticklabel_format(style='sci',scilimits=(-3,5),axis='both')
    #    ax.yaxis.major.formatter_useMathText = True
    #    ax.set_title(title, fontsize=12)
    #    return L_hist, a_hist, b_hist
        
    # function that outputs a gray picture
    def gray_fig_plot(image,ax,title, x, y):
        ax.imshow(image,cmap='gray')
        ax.locator_params(nbins=3)
        #ax.set_xlabel(x, fontsize=10)
        #ax.set_ylabel(y, fontsize=10)
        #ax.tick_params(axis='both', labelsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, fontsize=12)

    # function that outputs a colored picture
    def colored_fig_plot(image,ax,title, x, y):
        ax.imshow(image)
        ax.locator_params(nbins=3)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, fontsize=12)

    # Defining a new picture with ALL it:
    fig = plt.figure()

    #Defining the axis
    gs1 = gridspec.GridSpec(3, 4)
    ax0 = fig.add_subplot(gs1[0])
    ax1 = fig.add_subplot(gs1[1])
    ax2 = fig.add_subplot(gs1[2])
    ax3 = fig.add_subplot(gs1[3])
    ax4 = fig.add_subplot(gs1[4])
    ax5 = fig.add_subplot(gs1[5])
    ax6 = fig.add_subplot(gs1[6])
    ax7 = fig.add_subplot(gs1[7])

    # Converting the BGR pictures CV2 to RGB to Matplotlib
    # Just for info: Grey level = 0.299 * red component + 0.587 * green component + 0.114 * blue component

    # When opening a image using Image from PIL, the output image mode is RGB
    image_rgb = np.array(Image.open(core_input_fig), dtype=np.uint8)
    #image_rgb.mode
    img_gray =cv2.cvtColor(image_rgb,cv2.COLOR_RGB2GRAY)
    #name_gray = dt_string + "img_gray.png"
    #cv2.imwrite(name_gray,img_gray)
    img_camera_rgb = cv2.cvtColor(img_camera,cv2.COLOR_BGR2RGB)

    # Opening the B&W picture and showing the threshold line in histogram
    #imgbw = mpimg.imread(name_thresh)

    # Opening the cropped.png picture
    # image3 = np.array(Image.open(name_corte), dtype=np.uint8)

    # Calling the figures in this order
    # Gray image
    gray_fig_plot(image_rgb,ax0,"Imagem picamera", " ", " ")
    
    # Gray histogram with threshold
    gray_histogram_pic(img_gray,ax1,"Histograma Cinza", " ", " ")
    ax1.axvline(x=ret, color='r')
    ax1.text(ret, 1000, 'T')
    ax1.text(ret+50, 1000, 'B')
    ax1.text(ret-50, 1000, 'F')
    ax1.ticklabel_format(style='sci',scilimits=(-3,4),axis='both')
    ax1.yaxis.major.formatter_useMathText = True

    #extent = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    #fig.savefig('ax1_figure.png', bbox_inches=extent.expanded(1.5, 1.5)) 

    #thresholding image
    binary_image = np.array(Image.open(name_thresh), dtype=np.uint8)
    ax2.imshow(binary_image, cmap = 'binary')
    ax2.locator_params(nbins=3)
    ax2.set_title("Imagem Binária", fontsize=12)
    ax2.set_xticks([])
    ax2.set_yticks([])

    # Processed image
    colored_fig_plot(img_camera_rgb,ax3,"Contorno e Centroide", "", "")

    # Plotting RGB, HSV and Lab histograms
    img_cut_pixels = np.array(Image.open(name_pixels), dtype=np.uint8)
    colored_fig_plot(img_cut_pixels, ax4, "Recorte", "", "")
    r_hist, g_hist, b_hist = rgb_histogram(img_cut_pixels,ax5,"RGB", " ", " ")
    #ax5.ticklabel_format(style='sci',scilimits=(-3,5),axis='both')
    #ax5.yaxis.major.formatter_useMathText = True
    h_hist, s_hist, v_hist = hsv_histogram(img_cut_pixels,ax6,"HSV")
    c_hist = gray_histogram_pic(img_cut_pixels, ax7, "Cinza", " ", " ")
    #ax6.ticklabel_format(style='sci',scilimits=(-3,5),axis='both')
    #ax6.yaxis.major.formatter_useMathText = True

    #Plotting L*a*b* 
    #L_hist, a_hist, bb_hist = cielab_histogram(img_cut_pixels, ax7,"L*a*b*")
    #ax7.ticklabel_format(style='sci',scilimits=(-3,5),axis='both')
    #ax7.yaxis.major.formatter_useMathText = True
                      
    # Showing and saving the plots
    #plt.tight_layout()
    #gs1.tight_layout(fig)
    name_grid = dt_string + "grid.png"
    fig.set_size_inches(15,12)
    plt.savefig(name_grid, bbox_inches='tight')
    nuvem(name_grid)
    
    print("Análise de cor concluída :-)")
    plt.close('all')

    content = [fileName]

    def content_csv(x_hist, lower, upper):
        i = 0
        for i in range(lower,upper):
            v = x_hist.flat[i]
            content.append(v)
            v = []

    content_csv(c_hist,0,256)
    content_csv(r_hist,0,256)
    content_csv(g_hist,0,256)
    content_csv(b_hist,0,256)
    content_csv(h_hist,0,180)
    content_csv(s_hist,0,256)
    content_csv(v_hist,0,256)
    
    with open('wine_samples_data.csv', 'a') as f:
  
        # Pass this file object to csv.writer()
        # and get a writer object    
        writer_object = writer(f)
        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(content)
        #Close the file object
        f.close()

    nuvem('wine_samples_data.csv')
    #return(name_corte, h_hist, s_hist, v_hist, L_hist, a_hist, bb_hist, r_hist, g_hist, b_hist)
    return(name_corte, h_hist, s_hist, v_hist, r_hist, g_hist, b_hist)
