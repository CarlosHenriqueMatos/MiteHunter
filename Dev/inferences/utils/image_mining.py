from PIL import Image
import os

def get_image_info(image_path):
   print(image_path)
   l = image_path.split("/")
   image_metadata = l[len(l)-2]
   email = image_metadata.split("_")[0]
   cultivo_id = image_metadata.split("_")[1]
   image_data = image_metadata.split("_")[2]
   day = image_data[0:2]
   month = image_data[2:4]
   year = image_data[4:9]
   date = f'{day}-{month}-{year}'
   
   return {"date_amos": date,'cultivo_id':cultivo_id ,"name": email}

if __name__ == "__main__":
   image_info = get_image_info("/home/carlos/Imagens/carlos@gmail.com_123_04022024/123465.png")
   print(image_info)