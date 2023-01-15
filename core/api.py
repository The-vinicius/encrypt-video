from ninja import NinjaAPI, File, Form
from ninja.files import UploadedFile
from Cryptodome.Cipher import AES
from django.http import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from tempfile import NamedTemporaryFile
import zipfile


api = NinjaAPI()


class PassKey(BaseModel):
    key: str = Field(..., max_length=16, min_length=16)

@api.post('encrypt')
async def encrypt(request, file: UploadedFile = File(...), passkey: PassKey = Form(...)):
    # Read the key and encode it as bytes
    key = passkey.key.encode()
    # name files
    vname = './encrypt/'+file.name+'.bin'
    kname = './encrypt/key.bin'
    zname = './zips/'+file.name+'.zip'

    # Create a Cipher object using the key
    cipher = AES.new(key, AES.MODE_EAX)
    with open(vname, 'wb') as f:
        while True:
            chunk = file.read(1048576)
            if not chunk:
                break
            f.write(cipher.encrypt(chunk))

    with open(kname, 'wb') as f:
        [f.write(x) for x in (cipher.nonce, cipher.digest())]

    files = [vname, kname]
    # Create the ZIP file
    with zipfile.ZipFile(zname, 'w') as myzip:
        for f in files:
            myzip.write(f)

    f = open(zname, 'rb')

    response = FileResponse(f, content_type='application/octet-stream')
    return response


@api.post('decrypt')
async def decrypt(request, files: List[UploadedFile] = File(...), passkey: str = Form(...), name: str = Form(...)):
    key = passkey.encode()
    nonce, tag = [ files[1].read(x) for x in (16, 16) ]

    # Open a new file in binary mode for writing
    cipher = AES.new(key, AES.MODE_EAX, nonce)

    with open(name+'.mp4', 'wb') as f:
        while True:
            chunk = files[0].read(1048576)
            if not chunk:
                break
            f.write(cipher.decrypt(chunk))
    cipher.verify(tag)

    """data = cipher.decrypt_and_verify(ciphertext, tag)
    with open(name+'.mp4', 'wb') as f:
        f.write(data) """
    # Open the decrypted file and return it with a FileResponse
    f = open(name+'.mp4', 'rb')
    response = FileResponse(f, content_type='application/octet-stream')
    return response
