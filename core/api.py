from ninja import NinjaAPI, File, Form
from ninja.files import UploadedFile
from Cryptodome.Cipher import AES
from django.http import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from tempfile import NamedTemporaryFile
import zipfile


api = NinjaAPI()


class PassKey(BaseModel):
    key: str = Field(..., max_length=16, min_length=16)

@api.post('encrypt')
async def encrypt(request, file: UploadedFile = File(...), passkey: PassKey = Form(...)):
    # Read the key and encode it as bytes
    key = passkey.key.encode()

    # Create a Cipher object using the key
    cipher = AES.new(key, AES.MODE_EAX)
    with open(file.name+'.bin', 'wb') as f:
        while True:
            chunk = file.read(1048576)
            if not chunk:
                break
            f.write(cipher.encrypt(chunk))

    with open('key', 'wb') as f:
        [f.write(x) for x in (cipher.nonce, cipher.digest())]

    files = [file.name+'.bin', 'key']
    # Create the ZIP file
    with zipfile.ZipFile(file.name+'.zip', 'w') as myzip:
        for f in files:
            myzip.write(f)

    f = open(file.name+'.zip', 'rb')

    response = FileResponse(f, content_type='application/octet-stream')
    return response


@api.post('decrypt')
async def decrypt(request, file: UploadedFile = File(...), key: str = Form(...), name: str = Form(...)):
    key = key.encode()
    nonce, tag, ciphertext = [ file.read(x) for x in (16, 16, -1) ]

    # Open a new file in binary mode for writing
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    with open(name+'.mp4', 'wb') as f:
        f.write(data)
    # Open the decrypted file and return it with a FileResponse
    f = open(name+'.mp4', 'rb')
    response = FileResponse(f, content_type='application/octet-stream')
    return response
    
