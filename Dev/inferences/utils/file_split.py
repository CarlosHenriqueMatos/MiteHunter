import os

path = "Amostra/"
dirs = os.listdir(path)

for file in dirs:
    # file name with extension
    file_name = os.path.basename(file)
    l = file_name.split("_")
    email = l[0]

    cultivo_id = l[1]

    #
    dateTime = f"{l[2][:4]}-{l[2][4:6]}-{l[2][6:8]}"
