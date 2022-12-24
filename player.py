import random


class Id_player():
    def __init__(self):
        self.last_id = 0

    def get_id(self):
        self.last_id += 1
        return self.last_id


class Player():
    def __init__(self, sock, id_player):
        self.sock = sock
        # self.ip = ip
        self.name = None
        self.is_free = True
        self.package_out = {}
        self.package_in = {}
        self.id = id_player
        self.errors = 0
    
    def update_package_out(self, id_message, data_messang):
        self.package_out[id_message] = data_messang

    def reset_package_out(self):
        self.package_out = {}
    
    def update_package_in(self, data):
        self.package_in = data
    def reset_package_in(self):
        self.package_in = {}

    def set_name(self, st):
        self.name = st

class TicTacToe():
    def __init__(self, pl_1: Player, pl_2: Player=None):
        self.pl_1 = pl_1
        self.pl_2 = pl_2
        # self.next_step = random.randint(1, 2)
        self.next_step = 2
        self.count_step_1 = 0
        self.count_step_2 = 0
        self.game_table = [0, 0, 0,
                           0, 0, 0,
                           0, 0, 0]
                            # 0 - хода не было
                            # 2 - нолик
                            # 1 - крестик
                            # 3 - закрыть клетку для хода игроку
    def who_first(self):
        print("LOG stsrt: who_first", "первым был", self.pl_1.name)
        if random.randint(0, 1):
            self.pl_1, self.pl_2 = self.pl_2, self.pl_1
        print("LOG finish: who_first", "первым стал", self.pl_1.name)

    def step(self):
        print("LOG start: step")
        game_table_close = []
        for n in self.game_table:
            if n == 0:
                game_table_close.append(3)
            else:
                game_table_close.append(n)
        if self.next_step == 1:
            self.next_step = 2
            self.pl_2.package_out["open_table"] = self.game_table
            self.pl_1.package_out["open_table"] = game_table_close
            self.count_step_2 += 1
        elif self.next_step == 2:
            self.next_step = 1
            self.pl_1.package_out["open_table"] = self.game_table
            self.pl_2.package_out["open_table"] = game_table_close
            self.count_step_1 += 1
        if self.count_step_1 > 2 or self.count_step_2 > 2:
            winner = self.check_win()
            if winner == 1:
                self.pl_1.package_out["winner"] = f"Победил {self.pl_1.name}"
                self.pl_2.package_out["winner"] = f"Победил {self.pl_1.name}"
                self.pl_1.package_out["open_table"] = game_table_close
                self.pl_2.package_out["open_table"] = game_table_close
            if winner == 2:
                self.pl_1.package_out["winner"] = f"Победил {self.pl_2.name}"
                self.pl_2.package_out["winner"] = f"Победил {self.pl_2.name}"
                self.pl_1.package_out["open_table"] = game_table_close
                self.pl_2.package_out["open_table"] = game_table_close
        if self.count_step_1 + self.count_step_2 > 9:
            self.pl_1.package_out["winner"] = f"Победила дружба"
            self.pl_2.package_out["winner"] = f"Победила дружба"
            self.pl_1.package_out["open_table"] = game_table_close
            self.pl_2.package_out["open_table"] = game_table_close
        print("LOG finish: step")

    def check_win(self):
        print("LOG start: step")
        win_coord = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
        board = self.game_table
        for each in win_coord:
            if board[each[0]] == board[each[1]] == board[each[2]] != 0:
                print("LOG finish: check_win: Определил победителя")
                return board[each[0]]
        print("LOG finish: check_win: False")
        return False
class Statistics():
    def __init__(self):
        self.free_players = 0
        self.busy_players = 0

    def plus_free(self):
        self.free_players += 1



#class connection_monitoring():
#    def __init__(self):
#        self.connections = {}

#    def add_error(self, err):
#        self.connections[err] = setdefault(err, 0) += 1



#class Game_World():
#    def __init__(self):
#        self.last_id = 0
#        self.players = {}

#    def get_id():
#        last_id += 1
#        return last_id
