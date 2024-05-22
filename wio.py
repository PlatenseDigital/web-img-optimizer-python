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
import threading
import queue

SELECTED = "You selected {n} files to optimize"
COUNT = "processed {n} images"
BADEXTENSION = "{n} files are not images"
SAVED = "Images saved on: {n}"
CANCELED = "You canceled the operation"

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
        update_label(len(invalid_paths), BADEXTENSION)
    else:
        update_label(len(paths), SELECTED)
        if main_frame.winfo_ismapped():
            start_processing(paths)
        else:
            advanced_start_processing(paths)

def load_file():
    filenames = filedialog.askopenfilenames(initialdir="/downloads", title="Select an image", filetypes=[("Images", "*.png;*.apng;*.jpeg;*.jpg;*.webp;*.blp;*.bmp;*.ico;*.j2c;*.j2k;*.jp2;*.jpc;*.jpf;*.jpx;*.tif;*.tiff")])
    paths = list(filenames)
    update_label(len(paths),SELECTED)
    if main_frame.winfo_ismapped():
        start_processing(paths)
    else:
        advanced_start_processing(paths)

def update_label(qty,message):
    if main_frame.winfo_ismapped():
        if (qty != ''):
            pathLabel.configure(text = message.format(n=qty))
        else:
            pathLabel.configure(text = message)
    else:
        if (qty != ''):
            AdvancedPathLabel.configure(text = message.format(n=qty))
        else:
            AdvancedPathLabel.configure(text = message)

def process_images(paths, queue):
    images = []
    for index, path in enumerate(paths):
        queue.put({'s': 'processing', 'v': index + 1})
        image = Image.open(path)
        image = image.convert('RGBA')
        base_name = os.path.splitext(os.path.basename(path))[0]
        new_path = base_name + '.webp'

        from io import BytesIO
        img_bytes = BytesIO()
        image.save(img_bytes, format='WEBP')
        img_bytes.seek(0)
        images.append((new_path, img_bytes))

    save_images(images, queue)

def save_images(images, queue):
    if len(images) == 1:
        default_filename = images[0][0]
        saveLocation = filedialog.asksaveasfilename(
            initialdir="/downloads",
            title="Select a folder",
            defaultextension=".webp",
            initialfile=default_filename,
            filetypes=[("WebP files", "*.webp")]
        )
        if saveLocation:
            with open(saveLocation, 'wb') as f:
                f.write(images[0][1].read())
            queue.put({'s': 'completed', 'v': saveLocation})
        else:
            queue.put({'s': 'cancelled', 'v': ''})
    else:
        default_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".zip"
        saveLocation = filedialog.asksaveasfilename(
            initialdir="/downloads",
            title="Select a folder",
            defaultextension=".zip",
            initialfile=default_filename,
            filetypes=[("Zip files", "*.zip")]
        )
        if saveLocation:
            with ZipFile(saveLocation, 'w') as zipf:
                for img_name, img_bytes in images:
                    zipf.writestr(img_name, img_bytes.read())
            queue.put({'s': 'completed', 'v': saveLocation})
        else:
            queue.put({'s': 'cancelled', 'v': ''})

def start_processing(paths):
    q = queue.Queue()
    processing_thread = threading.Thread(target=process_images, args=(paths, q))
    
    toggle_button.config(state=DISABLED)
    loadButton.config(state=DISABLED, style='TButtonDisabled.TButton')
    original_text = loadButton.cget('text')
    loadButton.config(text=f"Processing {len(paths)} elements")

    processing_thread.start()
    
    def check_queue(q):
        try:
            while not q.empty():
                msg = q.get_nowait()
                if msg['s'] == "completed":
                    update_label(msg['v'], SAVED)
                elif msg['s'] == "cancelled":
                    update_label('', CANCELED)
                else: 
                    update_label(msg['v'], COUNT)
        except queue.Empty:
            pass
        finally:
            if processing_thread.is_alive():
                root.after(100, check_queue, q)
            else:
                loadButton.config(state=NORMAL, text=original_text, style='TButton')
                toggle_button.config(state=NORMAL)

    root.after(100, check_queue, q)

def advanced_process_images(paths, queue):
    images = []
    for index, path in enumerate(paths):
        queue.put({'s': 'processing', 'v': index + 1})
        image = Image.open(path)
        image = image.convert('RGBA')
        resize = resize_var.get()
        max_width = int(max_width_entry.get()) if max_width_entry.get().isdigit() else 0

        if resize and max_width > 0:
            # Resize image if it's larger than the max_width
            width_percent = (max_width / float(image.size[0]))
            height_size = int((float(image.size[1]) * float(width_percent)))
            image = image.resize((max_width, height_size), Image.LANCZOS)
        
        base_name = os.path.splitext(os.path.basename(path))[0]
        new_path = base_name + '.webp'

        from io import BytesIO
        img_bytes = BytesIO()
        image.save(img_bytes, format='WEBP')
        img_bytes.seek(0)
        images.append((new_path, img_bytes))

    save_images(images, queue)

def advanced_start_processing(paths):
    q = queue.Queue()
    processing_thread = threading.Thread(target=advanced_process_images, args=(paths, q))
    
    toggle_button.config(state=DISABLED)
    AdvancedLoadButton.config(state=DISABLED, style='TButtonDisabled.TButton')
    original_text = AdvancedLoadButton.cget('text')
    AdvancedLoadButton.config(text=f"Processing {len(paths)} elements")

    processing_thread.start()
    
    def check_queue(q):
        try:
            while not q.empty():
                msg = q.get_nowait()
                if msg['s'] == "completed":
                    update_label(msg['v'], SAVED)
                elif msg['s'] == "cancelled":
                    update_label('', CANCELED)
                else: 
                    update_label(msg['v'], COUNT)
        except queue.Empty:
            pass
        finally:
            if processing_thread.is_alive():
                root.after(100, check_queue, q)
            else:
                AdvancedLoadButton.config(state=NORMAL, text=original_text, style='TButton')
                toggle_button.config(state=NORMAL)

    root.after(100, check_queue, q)

def toggle_view():
    if main_frame.winfo_ismapped():
        main_frame.place_forget()
        advanced_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        toggle_button.configure(text="-")
    else:
        advanced_frame.place_forget()
        main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        toggle_button.configure(text="+")

def toggle_max_width_entry():
    if resize_var.get():
        max_width_label.place(relx=0.6, rely=0.7, anchor=E)
        max_width_entry.place(relx=0.6, rely=0.7, anchor=W)
    else:
        max_width_label.place_forget()
        max_width_entry.place_forget()


root = Tk()
root.title('Web Image Optimizator by Platense Digital')
root.configure(bg = '#A1EEBD')
main_frame = Frame(root, bg='#A1EEBD')
advanced_frame = Frame(root, bg='#A1EEBD')
main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
windowSize= math.ceil(root.winfo_screenwidth()/100*30)
root.geometry(str(windowSize)+'x'+str(windowSize))
root.minsize(windowSize, windowSize)
root.iconphoto(True, PhotoImage(file="favicon.png"))

style = ttk.Style()
style.theme_use('alt')
style.configure('TButtonDisabled.TButton', background='#1D9089')
style.configure('TButton', background = '#29C9BF', foreground = 'black', width = 20, borderwidth=0, focusthickness=0, focuscolor='#24AEA5',font=('Helvetica', math.ceil(windowSize/100*2), 'bold'))
style.map('TButton', background=[('active','#1D9089')])

logo = Image.open("logo.png")
logo = logo.resize((math.ceil(windowSize/100*15),math.ceil(windowSize/100*15)), Image.LANCZOS)
logotk = ImageTk.PhotoImage(logo)
logo_label = Label(root, image=logotk, bg='#A1EEBD')
logo_label.image = logotk
logo_label.place(relx=1, rely=0.99, anchor=SE)

toggle_button = ttk.Button(root, text="+", command=toggle_view, cursor="hand2")
toggle_button.place(x=10, y=10, height=30, width=30)

# Add content to the main_frame
loadButton = ttk.Button(main_frame, text="Click here to search your images\n          or drag and drop here", command=load_file, cursor="hand2")
buttonSize = windowSize/100*50
loadButton.place(relx=0.5, rely=0.5, anchor=CENTER, height=buttonSize, width=buttonSize)
loadButton.drop_target_register(DND_ALL)
loadButton.dnd_bind("<<Drop>>", get_path)

pathLabel = Label(main_frame, text="Drag and drop file in the entry box", fg='black', bg="#29C9BF", padx=5, pady=5)
pathLabel.place(relx=0.5, rely=0.9, anchor=CENTER)

# Add content to the advanced_frame
other_label = Label(advanced_frame, text="Advanced mode", bg='#A1EEBD', font=('Helvetica', 16))
other_label.pack(pady=20)

AdvancedLoadButton = ttk.Button(advanced_frame, text="Click here to search your images\n          or drag and drop here", command=load_file, cursor="hand2")
AdvancedLoadButton.place(relx=0.5, rely=0.25, anchor=CENTER, height=math.ceil(buttonSize/2), width=buttonSize)
AdvancedLoadButton.drop_target_register(DND_ALL)
AdvancedLoadButton.dnd_bind("<<Drop>>", get_path)

AdvancedPathLabel = Label(advanced_frame, text="Drag and drop file in the entry box", fg='black', bg="#29C9BF", padx=5, pady=5)
AdvancedPathLabel.place(relx=0.5, rely=0.9, anchor=CENTER)

resize_var = BooleanVar()
resize_check = Checkbutton(advanced_frame, text="Resize", variable=resize_var, bg='#A1EEBD', command=toggle_max_width_entry)
resize_check.place(relx=0.3, rely=0.7, anchor=CENTER)

max_width_label = Label(advanced_frame, text="Max Width (px):", bg='#A1EEBD')

max_width_entry = Entry(advanced_frame)

root.mainloop()