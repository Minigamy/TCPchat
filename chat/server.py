import socket
import threading
import json
import syslog


# Размер заголовка
HEADER_LENGTH = 10

# Данные сервера
host = '127.0.0.1'
port = 55555

# Запускаем сервер
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()
print("Server is listening")


# clients - список сокетов клиентов,
# nicknames - список никнеймов клиентов,
# conf_list - список сообщений, которые требуют подтверждения о доставке.
clients = []
nicknames = []
conf_list = []


"""
Функция для отправки сообщений всем подключенным клиентам.
В нее мы передаем сообщение, которое необходимо отправить и можем указать сокет отправителя, если нам надо, чтобы 
сообщение у него не дублировалось.
"""
def broadcast(message, sender=None):
    for client in clients:
        if client != sender:
            client.send(message)


"""
Функция для обработки сообщений полученных от клиента.
Тут реализована обработка трех типов сообщений: system, message, confirm.
Полное сообщение состоит из заголовка и данных - [[header][data]]. [header] - содержит информацию о размере [data].
Информация, которая хранится в [data] зависит от типа сообщения.
"""
def handle(client):
    while True:
        message_header = client.recv(HEADER_LENGTH)  # Получаем заголовок, которые содержит информацию о размере сообщения.

        #  Если мы не получили никаких данных, это означает, что клиент закрыл соединение. Поэтому удаляем сокет клиента
        #  из списка клиентов, закрываем соединение со стороны сервера, записываем информацию об отключении клиента
        #  в syslog.
        if not len(message_header):
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            syslog.syslog('{} left!'.format(nickname))

            #  Формируем сообщение типа 'system' и кодирем его.
            #  В заголовок записываем размер сообщения и кодирем.
            #  Уведомляем всех оставшихся клиентов. Удаляем никнейм из списка nicknames.
            sys_message = json.dumps(
                {
                    'type': 'system',
                    'message': '{} left!'.format(nickname)
                }).encode('utf-8')
            sys_message_header = f"{len(sys_message):<{HEADER_LENGTH}}".encode('utf-8')
            broadcast(sys_message_header + sys_message)
            nicknames.remove(nickname)
            break

        #  Если данные были получены, то извлекаем из заголовка размер основного сообщения.
        #  Получаем основное сообщение, то есть часть [data].
        #  Раскодируем сообщение. Теперь оно у нас в виде словаря.
        message_length = int(message_header.decode('utf-8').strip())
        message = client.recv(message_length)
        decoded_message = json.loads(message.decode('utf-8'))

        #  Если сообщение типа 'message':
        #    Добавляем инфо о клиенте и id сообщения в conf_list.
        #    Отправляем данное сообщение всем подключенным клиентам, кроме отправителя.
        #    Добавляем сообщение в syslog.
        if decoded_message['type'] == 'message':
            conf_list.append({'client': client, 'uuid': decoded_message['uuid']})
            broadcast(message_header+message, client)
            syslog.syslog(decoded_message['message'])

        #  Если сообщение типа 'confirm':
        #    В цикле проходим по всему списку conf_list.
        #    Если находим там id указанное в сообщении, то удаляем запись об этом сообщении из conf_list и
        #    перенаправляем полное сообщение нужному клиенту (который ждет подтверждение о доставке сообщения).
        elif decoded_message['type'] == 'confirm':
            for conf_message in conf_list:
                if conf_message['uuid'] == decoded_message['uuid']:
                    try:
                        conf_list.remove(conf_message)
                        conf_message['client'].send(message_header+message)
                    except ValueError:  # На случай, если будем удалять запись в conf_list, которой уже нет.
                        pass
                    break


""" 
Функция для прослушивания и подключения клиентов. 
"""
def receive():
    while True:
        # Принимаем подключение
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Отправляем клиенту строку '_nickname_', в ответ получаем никнейм клиента.
        # Добавялем никнейм в список nicknames.
        # Добавляем клиента в список clients.
        # Выводим никнейм в консоль сервера.
        # Добавляем сообщение в syslog.
        client.send('_nickname_'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        print("Nickname is {}".format(nickname))
        syslog.syslog('{} joined!'.format(nickname))

        # Формируем сообщение типа 'system'.
        sys_message = json.dumps(
            {
                'type': 'system',
                'message': '{} joined!'.format(nickname)
            }).encode('utf-8')
        sys_message_header = f"{len(sys_message):<{HEADER_LENGTH}}".encode('utf-8')

        # Уведомляем всех подключенных клиентов, что подключился еще один.
        broadcast(sys_message_header+sys_message)

        # Запускаем новый поток, который запускает ранее реализованную функцию handle для этого конкретного клиента.
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive()
