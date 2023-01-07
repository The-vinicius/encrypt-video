from Cryptodome.Cipher import AES

while True:
    senha = str(input('senha: '))
    if len(senha) == 16:
        key = senha.encode(encoding='UTF-8')
        break
    else:
        print ('Digite um senha com 16 caracteres!')


with open("m.mp4.encrypted", "rb") as f:
    nonce, tag, ciphertext = [ f.read(x) for x in (16, 16, -1) ]

# let's assume that the key is somehow available again
cipher = AES.new(key, AES.MODE_EAX, nonce)
data = cipher.decrypt_and_verify(ciphertext, tag)

with open('test.mp4', 'wb') as f:
    f.write(data)
