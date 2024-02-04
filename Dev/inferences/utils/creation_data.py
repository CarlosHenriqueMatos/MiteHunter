import json
import os
from utils.image_mining import get_image_info

def make_json_file(arq_file, new_data, image_path):
    print(arq_file,new_data,image_path)
    try:
        with open(arq_file, "r+") as arq_open:
            try:
                arq_load = json.load(arq_open)
            except json.JSONDecodeError:
                arq_load = []

            found = False
            if not found:
                arq_load.append(new_data)
                arq_open.seek(0)  # Move to the beginning of the file
                json.dump(arq_load, arq_open, indent=4)

    except FileNotFoundError:
        print("Arquivo não encontrado. Criando um novo arquivo com os dados existentes...")
        with open(arq_file, "w") as f:
            json.dump([new_data], f, indent=4)

    except Exception as e:
        raise Exception(f"Erro ao criar o arquivo JSON: {e}")
