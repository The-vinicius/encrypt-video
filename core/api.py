from ninja import NinjaAPI, File, Form
from ninja.files import UploadedFile
from Cryptodome.Cipher import AES
from django.http import FileResponse


api = NinjaAPI()


@api.post('encrypt')
async def encrypt(request, file: UploadedFile = File(...), key: str = Form(...)):
    # Read the key and encode it as bytes
    key = key.encode()

    # Create a Cipher object using the key
    cipher = AES.new(key, AES.MODE_EAX)

    # Encrypt the file and write the encrypted data to a new file
    with open(file.name + '.encrypted', 'wb') as out_file:
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            out_file.write(cipher.encrypt(chunk))
    # Open the encrypted file and return it with a FileResponse
    f = open(file.name + '.encrypted', 'rb')
    response = FileResponse(f, content_type='application/octet-stream')
    return response


@api.post('decrypt')
async def decrypt(request, file: UploadedFile = File(...), key: str = Form(...), name: str = Form(...)):
    key = key.encode()

    cipher = AES.new(key, AES.MODE_EAX)

    # Open a new file in binary mode for writing
    with open(name+'.mp4', 'wb') as out_file:
        # Read and decrypt the data in chunks
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            out_file.write(cipher.decrypt(chunk))

    # Open the decrypted file and return it with a FileResponse
    f = open(name+'.mp4', 'rb')
    response = FileResponse(f, content_type='application/octet-stream')
    breakpoint()
    return response
    
