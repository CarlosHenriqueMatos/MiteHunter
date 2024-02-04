#xyz
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ultralytics import YOLO
import cv2
import threading
#import json

#import datetime
#import time
from utils.creation_data import make_json_file
from utils.image_mining import get_image_info
import psutil
import os

model = YOLO('model/best.pt')#load model insert the way to trained model

class ImgProcessor(threading.Thread):
    def __init__(self, image_path):
        threading.Thread.__init__(self)
        self.image_path = image_path#file path image folder
        self.californicus = 0
        self.macropilis = 0
        self.rajado = 0

    def run(self):#remove json creation, this code only will really run the code, start aplication

        image = cv2.imread(self.image_path)#load image
        image = cv2.resize(image, (640, 640))#redim image to neural network size difined in train
        results = model(source=image,show_labels=False,show_conf=False,show_boxes=False)#load each image to show labels,conf and boxes set True
        #initializing json informations
        non_overlapping_boxes = []
        x1=0
        y1=0
        x2=0
        y2=0
        classes = []
        for box, conf, cls in zip(results[0].boxes.xyxy, results[0].boxes.conf, results[0].boxes.cls):# for to get box in the objects, confiance and class
            x1, y1, x2, y2 = box.tolist()#locate of the boxes
            is_overlapping = False
            for existing_box in non_overlapping_boxes:
                existing_x1, existing_y1, existing_x2, existing_y2 = existing_box

                x_overlap = max(0, min(x2, existing_x2) - max(x1, existing_x1))
                y_overlap = max(0, min(y2, existing_y2) - max(y1, existing_y1))
                intersection_area = x_overlap * y_overlap
                union_area = (x2 - x1) * (y2 - y1) + (existing_x2 - existing_x1) * (existing_y2 - existing_y1) - intersection_area
                iou = intersection_area / union_area
                
                if iou > 0.70:#verify if iou metrics is more than X%
                    is_overlapping = False
                    break

            if not is_overlapping:
                non_overlapping_boxes.append(box)

                if cls == 0:
                    self.californicus += 1

                elif cls == 1:
                    self.macropilis += 1

                elif cls == 2:
                    self.rajado += 1

            classes.append((cls.item(),conf.item(),x1,y1,x2,y2))
        image_info = get_image_info(self.image_path)
        
        return {"id":image_info['name'].split("_")[0],
                "cultivo_id":1,
                "img": image_info['name'],
                "img_proc": classes,
                "date_time": image_info['data'],
                "rajado": self.rajado,
                "macropilis": self.macropilis,
                "californicus": self.californicus
                } #This is the paramethers from JSON


class MyHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

        # Calcule o número máximo de threads com base na RAM disponível (adapte conforme sua versão do psutil)
        total_ram = psutil.virtual_memory().total
        max_threads = int(total_ram * 0.5 / psutil.Process().memory_info().rss)  # Adapte caso não tenha rss_per_thread
        self.semaphore = threading.Semaphore(max_threads)  # Crie o semáforo aqui

    def process_image_in_thread(self, image_path, previous_folder):
        img_processor = ImgProcessor(image_path)

        # Perform image processing tasks outside the lock
        data = img_processor.run()

        # Adquira o semáforo antes de acessar o arquivo JSON
        self.semaphore.acquire()

        with self.lock:
            make_json_file("Morango.json", data,image_path)

        # Libere o semáforo
        self.semaphore.release()

    def on_modified(self, event):#event is a return from FileSystemEventHandler class
        if event.event_type == "modified":
            # wait x minutes (implemente a lógica de espera aqui)

            for farmers_path in os.listdir("/home/carlos/Documentos/iniciacao_cientifica/Estudo_Yolo/dataset/agricultores/"):#directory
                full_farmers_path = "/home/carlos/Documentos/iniciacao_cientifica/Estudo_Yolo/dataset/agricultores/" + farmers_path
                print("Full farmers path: ",full_farmers_path)
                for file_path in os.listdir(full_farmers_path):#directory

                    full_image_path = "/home/carlos/Documentos/iniciacao_cientifica/Estudo_Yolo/dataset/agricultores/nome_data_hora/" + file_path
                    previous_folder = os.path.dirname(full_image_path)
                    thread = threading.Thread(target=self.process_image_in_thread, args=(full_image_path, previous_folder))#new thread creation
                    thread.start()
                    thread.join()#if remove infinite threads will be created
                os.rename("/home/carlos/Documentos/iniciacao_cientifica/Estudo_Yolo/dataset/agricultores/" + farmers_path, "/home/carlos/Documentos/iniciacao_cientifica/Estudo_Yolo/dataset/processadas/" + farmers_path)

event_handler = MyHandler()

observer = Observer()
observer.schedule(event_handler, path='/home/carlos/Documentos/iniciacao_cientifica/Estudo_Yolo/dataset/agricultores/', recursive=True)
observer.start()
observer.join()