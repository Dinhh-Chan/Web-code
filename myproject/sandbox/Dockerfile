#Sử dụng image Python chính thức từ Docker Hub
FROM python:3.9-slim

# Đặt thư mục làm việc
WORKDIR /usr/src/app

# Sao chép script vào thư mục làm việc
COPY run_code.py .

# Cài đặt các phụ thuộc cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Chạy script
ENTRYPOINT ["python", "run_code.py"]