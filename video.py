from Cryptodome.Cipher import AES

with open('fjhf.mp4', 'rb') as f:
    video = f.read()

while True:
    senha = str(input('senha: '))
    if len(senha) == 16:
        key = senha.encode(encoding='UTF-8')
        break
    else:
        print ('Digite um senha com 16 caracteres!')

cipher = AES.new(key, AES.MODE_EAX)
ciphertext, tag = cipher.encrypt_and_digest(video)


with open('m.mp4.encrypted', 'wb') as f:
    [f.write(x) for x in (cipher.nonce, tag, ciphertext)]
