import requests
import os

def send_images_to_server(directory):
    url = 'http://localhost:5000/detectObject'  # Địa chỉ của server Flask
    files = [('image', (filename, open(os.path.join(directory, filename), 'rb'))) 
             for filename in os.listdir(directory) if filename.endswith('.jpg')]

    if len(files) != 6:
        print("Thư mục phải chứa đúng 6 ảnh")
        return

    response = requests.post(url, files=files)
    if response.status_code == 200:
        
        print(response.json())
        print("Ảnh đã được gửi thành công")
    else:
        print("Có lỗi xảy ra:", response.status_code)

# Thay thế 'path_to_your_images' bằng đường dẫn thực tế của bạn
send_images_to_server('D:\Learning\ContainerFault\images')
