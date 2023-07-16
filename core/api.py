from ninja import NinjaAPI, File, Form
from ninja.files import UploadedFile
from Cryptodome.Cipher import AES
from django.http import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from tempfile import NamedTemporaryFile
from ninja.security import django_auth, HttpBearer
from decouple import config
import tempfile


api = NinjaAPI()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == config('KEY'):
            return token


class PassKey(BaseModel):
    key: str = Field(..., max_length=16, min_length=16)


class NameKey(PassKey):
    name: str


@api.post('encrypt', auth=AuthBearer())
async def encrypt(request, file: UploadedFile = File(...), passkey: PassKey = Form(...)):
    # Read the key and encode it as bytes
    key = passkey.key.encode()
    # name files
    vname = file.name+'.bin'

    ciphertext_chunks = []

    # Create a Cipher object using the key
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce

    # encrypt video in chunks of bytes
    while True:
        chunk = file.read(1048576)
        if not chunk:
            break
        ciphertext_chunks.append(cipher.encrypt(chunk))

    with tempfile.NamedTemporaryFile() as file_out:
        file_out.write(nonce)
        file_out.write(cipher.digest())
        for chunk in ciphertext_chunks:
            file_out.write(chunk)

        f = open(file_out.name, 'rb')
        response = FileResponse(f, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{vname}"'
        return response



@api.post('decrypt', auth=AuthBearer())
async def decrypt(request, file: UploadedFile = File(...), namekey: NameKey = Form(...)):
    key = namekey.key.encode()
    # name file video decrypt
    nvideo = namekey.name+'.mp4'

    nonce = file.read(16)
    tag = file.read(16)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext_chunks = []

    while True:
        chunk = file.read(1048576)
        if not chunk:
            break
        plaintext_chunks.append(cipher.decrypt(chunk))

    try:
        cipher.verify(tag)
    except ValueError:
        return {'error': 'incorrect key'}

    with tempfile.NamedTemporaryFile() as file_out:
        for chunk in plaintext_chunks:
            file_out.write(chunk)

        f = open(file_out.name, 'rb')
        response = FileResponse(f, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{nvideo}"'
        return response
