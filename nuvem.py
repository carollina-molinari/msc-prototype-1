import dropbox, sys
import os
from datetime import date

def nuvem(name_of_file):
    dbx=dropbox.Dropbox('adicionar aqui o seu access token do dropbox')
    try:
        user=dbx.users_get_current_account()
    except:
       sys.exit()
    else:
        # Be careful and always change the path bellow
        with open("./"+name_of_file,"rb") as f: # alterar caminho para pendrive
            #print("[Dropbox] Uploading ", name_of_file)
            data_medicao = str(date.today().day)+'_'+str(date.today().month)+'_'+str(date.today().year)
            dbx.files_upload(f.read(),'/caminho/'+ str(data_medicao) + '/' + name_of_file, mode=dropbox.files.WriteMode.overwrite)
            f.close()
        return print("[Dropbox]: ", name_of_file, "- upload completo")

# Criação de pastas

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


