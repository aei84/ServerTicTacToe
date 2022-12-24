import json
import socket
import select
# from time import sleep
from pygame import time

from player import Player
from player import Id_player
from player import Statistics
from player import TicTacToe

HOST = "192.168.1.245"
# HOST = "192.168.239.181"
# HOST = ""
PORT = 10111
MAX_ERRORS = 1
FPS = 100

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет с параметрами, стандартный адрес,
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,
                       1)  # отключаем алгоритм Нейгла, чтобы отправлять данные сразу, а не собирать большой пакет
main_socket.bind((HOST, PORT))  #
main_socket.setblocking(0)  # 0 - не ждем действия всех клиентов
main_socket.listen(5)  # переходим в режим прослушивания, 5 - могут подключиться одновременно


# def test(socket_test):
#     print("sock =", players_id[socket_test].sock)
#     print("IP =", players_id[socket_test].ip)
#     print("name =", players_id[socket_test].name)
#     print("is_free =", players_id[socket_test].is_free)
#     print("package_out =", players_id[socket_test].package_out)
#     print("package_in =", players_id[socket_test].package_in)
#     print("id =", players_id[socket_test].id)


def handle(sock, addr):
    print("handle")
    try:
        data = sock.recv(1024)  # Should be ready
        print(11111111111)
    except ConnectionError:
        print(f"Client suddenly closed while receiving")
        return False
    print(f"Received {data} from: {addr}")
    if not data:
        print("Disconnected by", addr)
        return False
    data = json.loads(sock.recv(1024).decode())
    print(f"Send: {data} to: {addr}")
    return True


players_id = {}
players_sock = {main_socket: Player(main_socket, 0)}
players_sock[main_socket].name = "Server"
#statistics = Statistics()
id_player = Id_player()  # генератор идентификаторов подключившихся
for_del = set() # надо вспомнить зачем это
# inputs = [main_socket]
# outputs = []
games_pl1 = {} # список активных игр ключ первый игрок
#games_pl2 = {} # список активных игр ключ второй игрок

# вызывается когда новый игрок представляется или кто-то уходит,
# отправляет обновленный список всем
def send_online_players():
    print("LOG start: send_online_players")
    online_players = [(n.id, n.name, n.is_free) for n in players_sock.values()]
    for pl in players_sock.values():
        pl.package_out["list_players"] = online_players
    print("LOG finish: send_online_players")

def send_online_games():
    print("LOG start: send_online_games")
    online_games = [(n.pl_1.name, n.pl_1.id) for n in games_pl1.values() if n.pl_2 == None]
    for pl in players_sock.values():
        pl.package_out["list_games"] = online_games
    print("LOG finish: send_online_games")
def del_game(id: int):
    print("LOG start: del_game")
    games_pl1.pop(id, "Такой игры нет")
    print("LOG finish: del_game")

def start_game(game: TicTacToe):
    print("LOG start: start_game")
    game.who_first()
    game.pl_1.package_out["start_game"] = None
    game.pl_2.package_out["start_game"] = None
    game.step()
    print("LOG finish: start_game")

def message_reader(pl_sock: socket.socket, mess: dict):
    print("LOG start: message_reader")
    if mess.get("set_name"):
        print("LOG message_reader: set_name")
        players_sock[pl_sock].name = mess.get("set_name")
        send_online_players()
    if "get_list_players" in mess:
        print("LOG message_reader: get_list_players")
        players_sock[pl_sock].package_out["list_players"] = [(n.id, n.name, n.is_free) for n in players_sock.values()]
        #print(players_sock[pl_sock].package_out["list_players"])
    if "invitation" in mess:
        print("LOG message_reader: invitation")
        # games_pl1.update({players_sock[pl_sock].id: TicTacToe(pl_sock)})
        # players_id[mess["invitation"]].package_out = {"come on": players_sock[pl_sock].id}
        pass
    if "new_game" in mess:
        print("LOG message_reader: new_game")
        games_pl1.update({players_sock[pl_sock].id: TicTacToe(players_sock[pl_sock])})
        send_online_games()
    if "del_game" in mess:
        print("LOG message_reader: del_game")
        del_game(players_sock[pl_sock].id)
        send_online_games()
    if "join_to_game" in mess:
        print("LOG message_reader: join_to_game")
        games_pl1[players_sock[pl_sock].id] = games_pl1[mess["join_to_game"]] # добовляем играющего. Получается, два игрока ссылаются на одну игру
        games_pl1[players_sock[pl_sock].id].pl_2 = players_sock[pl_sock] # прописываем второго игрока в игре к которой присоединились
        games_pl1[players_sock[pl_sock].id].pl_1.is_free = False
        games_pl1[players_sock[pl_sock].id].pl_2.is_free = False
        send_online_players()
        start_game(games_pl1[players_sock[pl_sock].id])
    if "step" in mess:
        print("LOG message_reader: step")
        games_pl1[players_sock[pl_sock].id].game_table[mess["step"]] = games_pl1[players_sock[pl_sock].id].next_step # записываем в таблицу игры ход игрока
        games_pl1[players_sock[pl_sock].id].step() # передаем ход след. игроку
        #games_pl1[players_sock[pl_sock].id].step =

    print("LOG finish: message_reader")
def messange_writer(pl_sock):
    print("LOG start: messange_writer")
    d = json.dumps(players_sock[pl_sock].package_out)
    try:
        pl_sock.send(d.encode())
        players_sock[pl_sock].package_out = {}
        print("LOG finish: messange_writer", True, f"отправил {players_sock[pl_sock].id} сообщение {d}")
        return True
    except:
        print("LOG finish: messange_writer", False)
        return False


while True:
    print("LOG start: основного цикла", "Активных игр:", len(games_pl1), "Игроки онлайн", players_id.keys())
    clock = time.Clock()
    # print("Сейчас на сервере", len(players_sock) - 1, [n.name for n in players_sock.values()])
    readable, writeable, exceptional = select.select(players_sock,
                                                     [n.sock for n in players_sock.values() if len(n.package_out) > 0],
                                                     players_sock)
    for sock in readable:
        if sock == main_socket:
            sock, addr = main_socket.accept()  # Should be ready
            # inputs.append(sock)
            new_id = id_player.get_id()  # новый id игрока
            players_id[new_id] = Player(sock, new_id)  # создаем игрока в словаре с ключем id
            players_sock[sock] = players_id[
                new_id]  # создаем ссылку в другом словаре с ключами сокетами на этого же игрока (если я все правильно нонял)

        else:
            data = sock.recv(1024).decode()
            print(f'получил от {players_sock[sock].id} сообщение "{data}"')
            if data == "":
                sock.close()
                del_game(players_sock[sock].id)
                del players_id[players_sock[sock].id]
                del players_sock[sock]
                send_online_players()
            else:
                data = json.loads(data)
                message_reader(sock, data)

    for sock in writeable:
        messange_writer(sock)
    clock.tick(FPS)
    print("LOG finish: основного цикла\n\n")
