import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import yt_dlp
import os
import requests
from io import BytesIO
import time
from pathlib import Path


def obtener_id_video(url):
    # Obtener el ID del video de la URL
    if "youtube.com" in url:
        return url.split("v=")[-1].split('&')[0]  # Manejar posibles parámetros adicionales
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return None


def mostrar_miniatura():
    url = entry_url.get()
    video_id = obtener_id_video(url)
    if not video_id:
        messagebox.showerror("Error", "Por favor, ingrese una URL de YouTube válida.")
        return

    # Construir la URL de la miniatura
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"

    try:
        # Obtener el título del video usando yt-dlp
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Título no encontrado')

        # Mostrar el título del video
        label_title.config(text=f"Título del video: {video_title}")

        # Descargar y mostrar la miniatura
        response = requests.get(thumbnail_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img.thumbnail((200, 200))  # Redimensionar la imagen para que se ajuste a la interfaz
        img_tk = ImageTk.PhotoImage(img)

        # Mostrar la imagen en la etiqueta
        label_thumbnail.config(image=img_tk)
        label_thumbnail.image = img_tk  # Mantener una referencia de la imagen
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la información del video: {e}")


def progreso_hook(d):
    if d['status'] == 'downloading':
        porcentaje = float(d['_percent_str'].strip('%'))
        progress_var.set(porcentaje)
        label_status.config(text=f"Descargando... {d['_percent_str']} completado")
    elif d['status'] == 'finished':
        progress_var.set(100)
        label_status.config(text="Descarga completada!")
        modificar_fechas(d['filename'])


def download_video():
    url = entry_url.get()
    download_audio = var_audio.get()
    calidad_seleccionada = calidad_var.get()

    # Mapeo de texto visible a valores internos de yt-dlp
    calidad_valores = {
        'Mejor calidad': 'best',
        '1080p': 'bestvideo[height<=1080]',
        '720p': 'bestvideo[height<=720]',
        '480p': 'bestvideo[height<=480]',
        '144p': 'worst'
    }
    quality = calidad_valores[calidad_seleccionada]

    # Obtener la carpeta de descargas del usuario
    download_folder = str(Path.home() / "Downloads")  # Carpeta de descargas del usuario

    # Configuración de opciones de yt-dlp con el hook de progreso
    ydl_opts = {
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        # Especifica la carpeta de descargas y el nombre del archivo
        'progress_hooks': [progreso_hook],  # Agregar el hook de progreso
    }

    if download_audio:
        # Opciones para descargar solo el audio
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        # Opciones para descargar video con calidad seleccionada
        ydl_opts.update({
            'format': quality
        })

    try:
        # Ejecuta la descarga con yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")
        label_status.config(text=f"Ocurrió un error: {e}")


def modificar_fechas(ruta_archivo):
    # Obtener la fecha y hora actual en formato timestamp
    tiempo_actual = time.time()

    # Cambiar las fechas de modificación y acceso
    os.utime(ruta_archivo, (tiempo_actual, tiempo_actual))


# Crear la ventana principal
root = tk.Tk()
root.title("Aplicación de Descarga de Videos de YouTube")

# Frame para la entrada de URL y el botón de mostrar miniatura
frame_url = tk.Frame(root)
frame_url.pack(pady=5)

# Etiqueta y entrada para la URL
label_url = tk.Label(frame_url, text="Ingrese la URL del video de YouTube:")
label_url.pack(side=tk.LEFT, padx=5)
entry_url = tk.Entry(frame_url, width=40)
entry_url.pack(side=tk.LEFT, padx=5)

# Botón para mostrar miniatura
button_preview = tk.Button(frame_url, text="Mostrar información", command=mostrar_miniatura)
button_preview.pack(side=tk.LEFT)

# Etiqueta para mostrar el título del video
label_title = tk.Label(root, text="")
label_title.pack(pady=5)

# Etiqueta para la miniatura del video
label_thumbnail = tk.Label(root)
label_thumbnail.pack(pady=5)

# Botón para elegir descargar solo audio
var_audio = tk.BooleanVar()
check_audio = tk.Checkbutton(root, text="Descargar solo el audio", variable=var_audio)
check_audio.pack(pady=5)

# Menú desplegable para seleccionar la calidad del video con texto más amigable
label_quality = tk.Label(root, text="Seleccione la calidad del video:")
label_quality.pack(pady=5)
calidad_var = tk.StringVar(value="Mejor calidad")  # Valor por defecto
calidad_opciones = ['Mejor calidad', '1080p', '720p', '480p', '144p']
calidad_menu = tk.OptionMenu(root, calidad_var, *calidad_opciones)
calidad_menu.pack(pady=5)

# Barra de progreso
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=progress_var)
progress_bar.pack(pady=10)

# Botón de descarga
button_download = tk.Button(root, text="Descargar", command=download_video)
button_download.pack(pady=10)

# Etiqueta de estado
label_status = tk.Label(root, text="")
label_status.pack(pady=5)

# Iniciar el bucle de la GUI
root.mainloop()
