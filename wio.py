from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinterdnd2 import *
import math
import re
from PIL import Image, ImageTk
import os
import datetime
from zipfile import ZipFile

SELECTED = "You selected {n} files to optimize"
COUNT = "processed {n} images"
BADEXTENSION = "{n} files are not images"
SAVED = "Images saved on: {n}"
CANCELED = "You canceled the operation"
#def get_path(event):
#    print(f"Event data: {event.data}")  # Imprime el contenido del evento
#    print(type(event.data))
#    paths = re.findall(r'\{([^}]+)\}', event.data)
#    print(f"Extracted paths: {paths}")  # Imprime los paths extraídos
#    #check if data are images
#    updateLabel(len(paths),SELECTED)
#    processImages(paths)

def get_path(event):
    paths_in_braces = re.findall(r'\{([^}]+)\}', event.data)
    
    remaining_data = event.data
    for path in paths_in_braces:
        remaining_data = remaining_data.replace(f'{{{path}}}', '')
    remaining_paths = remaining_data.split()
    paths = paths_in_braces + remaining_paths
    
    valid_extensions = {'.png', '.apng', '.jpeg', '.jpg', '.webp', '.blp', '.bmp', '.ico', '.j2c', '.j2k', '.jp2', '.jpc', '.jpf', '.jpx', '.tif', '.tiff'}
    invalid_paths = [path for path in paths if os.path.splitext(path.lower())[1] not in valid_extensions]
    
    if invalid_paths:
        updateLabel(len(invalid_paths), BADEXTENSION)
    else:
        updateLabel(len(paths), SELECTED)
        processImages(paths)

def loadfile():
    filenames = filedialog.askopenfilenames(initialdir="/downloads", title="Select an image", filetypes=[("Images", "*.png;*.apng;*.jpeg;*.jpg;*.webp;*.blp;*.bmp;*.ico;*.j2c;*.j2k;*.jp2;*.jpc;*.jpf;*.jpx;*.tif;*.tiff")])
    paths = list(filenames)
    updateLabel(len(paths),SELECTED)
    processImages(paths)

def updateLabel(qty,message):
    if (qty != ''):
        pathLabel.configure(text = message.format(n=qty))
    else:
        pathLabel.configure(text = message)

def processImages(paths):
    images = []
    for index, path in enumerate(paths):
        updateLabel(f"{index + 1} of {len(paths)}", COUNT)

        image = Image.open(path)
        image = image.convert('RGBA')
        base_name = os.path.splitext(os.path.basename(path))[0]
        new_path = base_name + '.webp'
        
        from io import BytesIO
        img_bytes = BytesIO()
        image.save(img_bytes, format='WEBP')
        img_bytes.seek(0)
        images.append((new_path, img_bytes))
        
    default_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".zip"
    saveLocation = filedialog.asksaveasfilename(initialdir="/downloads", title="Select a folder", defaultextension=".zip", initialfile=default_filename, filetypes=[("Zip files", "*.zip")])    
    
    if saveLocation:
        with ZipFile(saveLocation, 'w') as zipf:
            for img_name, img_bytes in images:
                zipf.writestr(img_name, img_bytes.read())
        
        updateLabel(saveLocation,SAVED)
    else:
        updateLabel('',CANCELED)


root = Tk()
root.title('Web Image Optimizator by Platense Digital')
root.configure(bg = '#A1EEBD')
windowSize= math.ceil(root.winfo_screenwidth()/100*30)
root.geometry(str(windowSize)+'x'+str(windowSize))
root.minsize(windowSize, windowSize)
root.iconphoto(True, PhotoImage(file="favicon.png"))

loadButton = ttk.Button(root, text="Click here to search your images\n          or drag and drop here", command=loadfile, cursor="hand2")
buttonSize = windowSize/100*50
loadButton.place(relx=0.5, rely=0.5, anchor=CENTER, height=buttonSize, width=buttonSize)
style = ttk.Style()
style.theme_use('alt')
style.configure('TButton', background = '#29C9BF', foreground = 'black', width = 20, borderwidth=0, focusthickness=0, focuscolor='#24AEA5',font=('Helvetica', math.ceil(windowSize/100*2), 'bold'))
style.map('TButton', background=[('active','#1D9089')])

loadButton.drop_target_register(DND_ALL)
loadButton.dnd_bind("<<Drop>>", get_path)

pathLabel = Label(root, text="Drag and drop file in the entry box", fg='black', bg="#29C9BF", padx=5, pady=5)
pathLabel.place(relx=0.5, rely=0.9, anchor=CENTER)

logo = Image.open("logo.png")
logo = logo.resize((math.ceil(windowSize/100*15),math.ceil(windowSize/100*15)), Image.LANCZOS)
logotk = ImageTk.PhotoImage(logo)
logo_label = Label(root, image=logotk, bg='#A1EEBD')
logo_label.image = logotk

logo_label.place(relx=1, rely=0.99, anchor=SE)

root.mainloop()

