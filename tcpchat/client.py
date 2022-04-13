import json
import socket
import threading
import uuid

# Размер заголовка
HEADER_LENGTH = 10

# Выбираем никнейм
nickname = input("Choose your nickname: ")

# Подключаемся к серверу
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

"""
Функция для прослушивания сервера и отправка никнейма.
"""
def receive():
    while True:
        try:
            # Получаем сообщение
            message = client.recv(HEADER_LENGTH)

            # Если это строка '_nickname_', то отправляем серверу наш никнейм.
            if message.decode('utf-8') == '_nickname_':
                client.send(nickname.encode('utf-8'))

            else:
                # Если это не строка никнейм, то мы получили сообщение одного из типов: system, message, confirm.
                message_length = int(message.decode('utf-8'))
                message = client.recv(message_length).decode('utf-8')
                decoded_message = json.loads(message)  # dict/json

                # Если это сообщение типа 'message':
                #   Выводим текст сообщения
                #   Формируем сообщение типа 'confirm', чтобы подтвердить доставку. Кодируем его.
                #   В заголовок записываем размер сообщения и кодирем.
                #   Отправляем полное сообщение на сервер.
                if decoded_message['type'] == 'message':
                    print(decoded_message['message'])
                    conf_message = json.dumps(
                        {
                            'type': 'confirm',
                            'uuid': decoded_message['uuid']
                        }).encode('utf-8')
                    conf_message_header = f"{len(conf_message):<{HEADER_LENGTH}}".encode('utf-8')
                    client.send(conf_message_header+conf_message)

                # Если это сообщение типа 'confirm':
                #   Выводим в консоли информацию о том, что сообщение клиента было доставлено.
                elif decoded_message['type'] == 'confirm':
                    print('Message delivered')

                # Если это сообщение типа 'system':
                #   Выводим в консоли текст сообщения.
                elif decoded_message['type'] == 'system':
                    print(decoded_message['message'])

        except:
            # Закрываем соединение, если возникает ошибка.
            print("An error occured!\nConnection closed by the server")
            client.close()
            break


"""
Функция для отправки сообщений на сервер.
"""
def write():
    while True:
        # Записываем сообщение в переменную.
        # Если клиент ничего не написал, не отправляем это сообщение.
        message = '{}: {}'.format(nickname, input(''))
        if message == '{}: '.format(nickname):
            continue
        else:
            # Формируем сообщение типа 'message'.
            # В заголовок записываем размер сообщения и кодируем.
            # Отправляем сообщение на сервер.
            message = json.dumps({'type': 'message', 'uuid': str(uuid.uuid4()), 'message': message}).encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client.send(message_header + message)


# Запускаем отдельные потоки для получения и отправки сообщений.
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
