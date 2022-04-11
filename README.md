# Simple chatroom on Python using TCP

# Описание:

Серверная и клиентская сторона чат-комнаты.
Сервер принимает TCP соединение и обрабатывает/перенаправляет сообщения от клиентов.

В основном сервер и клиенты обмениваются тремя типами сообщений:
* system - системные сообщения вида `{'type': 'system', 'message': message}`. Они содержат в себе сообщение о том, что клиент с таким-то никнеймом подключился/отключился.
* message - сообщения формируемые клиентом, имеют вид `{'type': 'message', 'uuid': uuid, 'message': message}`. Они содержат в себе уникальный идентификатор, сгенерированный библиотекой uuid, и само сообщение от клиента, которое он напечатал.
* confirm - cообщения формируемые клиентом, имеют вид `{'type': 'confirm', 'uuid': uuid}`. Они необходимы для подтверждения доставки сообщения. После получения клиентом сообщения типа message, он формирует сообщение типа confirm и отправляет обратно.

####UUID генерируются только для сообщений типа message.
####Данная реализация работает только если сервер и клиента находятся на одной машине. Это без проблем можно исправить в следующих версиях.


######Реализованные функции:
* Каждый клиент выбирает себе никнейм, который будет отображаться в сообщениях от него.
* Клиенты получают подтверждение о доставке сообщения (если клиент не получил подтверждение значит сообщение не доставлено).
* Клиенты получают системные сообщения от сервера с информацией о присоединении или отключении другого клиента.
* Сервер принимает запросы от клиентов и устанавливает TCP соединение.
* Сервер поддерживает большое количество клиентов одновременно.
* Сервер логирует системные сообщения и сообщения от клиентов в syslog.


# Запуск

1 способ:
* Скачиваем/копируем файлы server.py и client.py из репозитория https://github.com/Minigamy/TCPchat/tree/master/tcpchat.
* Запускаем как python скрипты, сначала `server`, а потом подкючаем `client`.

2 способ:
* Через терминал зайдите в удобную для Вас папку, создайте виртуальное окружение, активируйте его.
* Скачайте и установите пакет с помощью команды: `pip install git+https://github.com/Minigamy/TCPchat.git`
* Создайте в папке файл `client.py`
* В файле напишите строчку `import tcpchat.client`, сохраните.
* Теперь через терминал можно запустить python командой `python3`.
* И прописать `import tcpchat.server`. У Вас запустится сервер, что подтвердит надпись в терминале "Server is listening"
* Находясь в папке с файлом `client.py` остается запустить клиента в отдельном терминате, но в том же виртуальном окружении, командой `python3 client.py`. Подключите таким образом необходимо количество клиентов и можно начинать общаться.


![Скриншот](https://github.com/Minigamy/TCPchat/tree/master/img/chat.jpeg)  
<p align="center">Чат</p>  
