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
    ciphertext = b''
    while True:
        chunk = file.read(1048576)
        if not chunk:
            break
        ciphertext += cipher.encrypt(chunk)
    # Encrypt the file and write the encrypted data to a new file
    #ciphertext, tag = cipher.encrypt_and_digest(file.read()) 
    with open(file.name+'.encrypted', 'wb') as f:
        [f.write(x) for x in (cipher.nonce, cipher.digest(), ciphertext)]
    # Open the encrypted file and return it with a FileResponse
    f = open(file.name + '.encrypted', 'rb')
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
    
