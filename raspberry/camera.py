import subprocess
import sys
import termios
import tty
import os
import requests
import cv2
from urllib.parse import urljoin
import socket

def get_char():
    """ Hàm này sẽ chờ và trả về ký tự được nhấn từ bàn phím. """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def capture_image(counter, directory):
    filename = f"captured_images/image{counter}.jpg"  # Đặt tên file
    command = ["fswebcam", "-r", "640x480", filename]  # Điều chỉnh độ phân giải nếu muốn
    subprocess.run(command)
    print(f"Ảnh đã được chụp: {filename}")

def get_server_ip(suffix):
    """Hàm này sẽ lấy địa chỉ IP của máy chủ từ số cuối được nhập."""
    try:
        # Lấy địa chỉ IP từ số cuối
        server_ip = f'192.168.237.{suffix}'
        socket.inet_aton(server_ip)  # Kiểm tra địa chỉ IP có hợp lệ không
        return server_ip
    except socket.error:
        print("Địa chỉ IP không hợp lệ.")
        return None

def send_images_to_server(directory, server_suffix, server_path='/detectObject'):
    """Hàm này sẽ gửi ảnh đến server Flask."""
    # Lấy địa chỉ IP của máy chủ tự động
    server_ip = get_server_ip(server_suffix)

    if server_ip:
        server_url = f'http://{server_ip}:5000{server_path}'  # Giả sử cổng là 5000, bạn có thể thay đổi tùy thuộc vào cấu hình server
        print(f'Server URL: {server_url}')

        files = [('image', (filename, open(os.path.join(directory, filename), 'rb'))) 
                for filename in os.listdir(directory) if filename.endswith('.jpg')]

        response = requests.post(server_url, files=files)
        if response.status_code == 200:
            print("Ảnh đã được gửi thành công:", response.json())
        else:
            print("Có lỗi xảy ra:", response.status_code)
    else:
        print("Không thể lấy địa chỉ IP của máy chủ.")

def show_and_capture(camera_index=0):
    cap = cv2.VideoCapture(camera_index)

    while True:
        ret, frame = cap.read()
        cv2.imshow('Camera', frame)

        char = cv2.waitKey(1)
        if char == ord('k'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    server_suffix = 156
    directory = "captured_images"
    if not os.path.exists(directory):
        os.makedirs(directory)

    print("Nhấn 'k' để chụp ảnh. Nhấn 'q' để thoát.")

    counter = 1
    while counter <= 6:
        show_and_capture()
        capture_image(counter, directory)
        counter += 1

    print("Đã chụp đủ 6 hình, chuẩn bị gửi ảnh.")
    send_images_to_server(directory, server_suffix)

if __name__ == '__main__':
    main()
