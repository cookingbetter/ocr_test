import os
from fastapi import FastAPI, UploadFile, File
import easyocr
from pdf2image import convert_from_path
import os
import re

app = FastAPI()

# Получаем абсолютный путь к текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1]  # Получаем расширение файла

    # Сохраняем файл на сервере
    file_path = os.path.join(current_dir, "uploads", file.filename)
    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    reader = easyocr.Reader(["ru", "en"])

    if file_path[-4:] == '.pdf':
        path = 'page0.jpg'
        images = convert_from_path(file_path, 150, poppler_path=r'C:\Program Files\poppler-23.05.0\Library\bin')

        if os.path.isfile(path):
            os.remove(path)

        for i in range(len(images)):
            images[i].save('page' + str(i) + '.jpg', 'JPEG')

        file_path = path
        result = reader.readtext(file_path, detail=0, paragraph=True)

    elif file_path[-4:] == '.png' or file_path[-4:] == '.jpg':
        result = reader.readtext(file_path, detail=0, paragraph=True)

    else:
        print('Unsupported format')

    operation = {"sender": "",
                 "receiver": "",
                 "amount": 0,
                 "datetime": 0}

    if result[0] == 'СБЕР БАНК':
        for line_num in range(len(result)):
            if line_num == 2:
                operation['datetime'] = result[line_num]
            if line_num == 3:
                string = result[line_num]
                start_word = "ФИО"
                end_word = "Телефон"

                pattern = re.compile(re.escape(start_word) + r"(.*?)" + re.escape(end_word))
                match = re.search(pattern, string)

                operation['receiver'] = match.group(1).strip()

            if line_num == 4:
                string = result[line_num]
                start_word = "ФИО"
                end_word = "Счёт"

                pattern = re.compile(re.escape(start_word) + r"(.*?)" + re.escape(end_word))
                match = re.search(pattern, string)

                operation['sender'] = match.group(1).strip()

                start_word = "перевода"
                end_word = "Комиссия"

                pattern = re.compile(re.escape(start_word) + r"(.*?)" + re.escape(end_word))
                match = re.search(pattern, string)

                operation['amount'] = match.group(1).strip()



    elif result[0] == 'тинькоФФ':
        for line_num in range(len(result)):
            if line_num == 1:
                operation['datetime'] = result[line_num]
            if line_num == 3:
                operation['amount'] = result[line_num]
            if line_num == 11:
                operation['sender'] = result[line_num]
            if line_num == 14:
                operation['receiver'] = result[line_num]

    # Возвращаем информацию о сохраненном файле
    return operation
