import sys
import json
import subprocess
import tempfile

def run_code(code, input_data):
    # Tạo một file tạm thời cho mã nguồn của người dùng
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_code_file:
        temp_code_file.write(code.encode('utf-8'))
        temp_code_file.flush()
    
        try:
            # Chạy mã nguồn của người dùng với dữ liệu đầu vào được cung cấp
            result = subprocess.run(
                [sys.executable, temp_code_file.name],
                input=input_data.encode('utf-8'),
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout
            error = result.stderr
        except subprocess.TimeoutExpired:
            output = ''
            error = 'Error: Code execution timed out.'

        return output, error

if __name__ == "__main__":
    # Đọc mã nguồn và dữ liệu đầu vào từ file JSON (giả lập payload của POST request)
    with open('payload.json', 'r') as f:
        payload = json.load(f)
    
    code = payload['code']
    input_data = payload['input']

    output, error = run_code(code, input_data)

    # In kết quả dưới dạng đối tượng JSON
    result = {
        'output': output,
        'error': error
    }
    print(json.dumps(result))
