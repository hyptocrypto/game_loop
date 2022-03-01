from bdb import Breakpoint
from ctypes.wintypes import PWIN32_FIND_DATAA
from re import S
import time
import logging
import os

log_file = os.path.join(os.path.join(os.path.abspath(__file__), ".."), "game_loop.log")
handler = logging.FileHandler(log_file)
LOGGER = logging.getLogger()
LOGGER.addHandler(handler)


class Battle:
    def __init__(self, player1, player2, fire_vect_len):
        self.fire_vect_len = fire_vect_len
        self.fire_vect = [0] * fire_vect_len
        self.player1 = player1
        self.player2 = player2

        self.player1_shot_pointer = 0
        self.player2_shot_pointer = len(self.fire_vect)

        self.inital_shot = True

    def proc_fire(self):
        if not self.inital_shot:
            if self.player1.id not in self.fire_vect:
                self.player1.has_been_shot = True
                return
            if self.player2.id not in self.fire_vect:
                self.player2.has_been_shot = True
                return

            p1_first_index = self._first_p1_index(self.fire_vect, self.player1.id)
            p1_new_final_shot_index = (p1_first_index + self.player1.fire()) + 1
            res = self._check_collision(self.player2, p1_first_index)
            if res:
                return

            self.fire_vect[:p1_new_final_shot_index] = [self.player1.id] * (
                len(self.fire_vect[:p1_new_final_shot_index])
            )
            print(self.fire_vect)

            p2_first_index = self._first_p2_index(self.fire_vect, self.player2.id)
            p2_new_final_shot_index = p2_first_index - self.player2.fire()
            res = self._check_collision(self.player1, p2_first_index)
            if res:
                return

            self.fire_vect[p2_new_final_shot_index:] = [self.player2.id] * (
                len(self.fire_vect[p2_new_final_shot_index:])
            )
            print(self.fire_vect)

            self.player1_shot_pointer = p1_new_final_shot_index
            self.player2_shot_pointer = p2_new_final_shot_index
        else:
            p1_new_final_shot_index = self.player1_shot_pointer + self.player1.fire()
            p2_new_final_shot_index = self.player2_shot_pointer - self.player2.fire()

            self.fire_vect[:p1_new_final_shot_index] = [self.player1.id] * (
                len(self.fire_vect[:p1_new_final_shot_index])
            )
            print(self.fire_vect)

            self.fire_vect[p2_new_final_shot_index:] = [self.player2.id] * (
                len(self.fire_vect[p2_new_final_shot_index:])
            )
            print(self.fire_vect)
            self.player1_shot_pointer = p1_new_final_shot_index
            self.player2_shot_pointer = p2_new_final_shot_index

        print("----------------------------------")

        self.inital_shot = False

    def _first_p2_index(self, alist, value):
        try:
            return alist.index(value)
        except ValueError:
            return None

    def _first_p1_index(self, alist, value):
        try:
            return len(alist) - alist[-1::-1].index(value) - 1
        except ValueError:
            return None

    def _check_collision(self, player, p_idx):
        if player == self.player1:
            if player.id not in self.fire_vect:
                return self.player1
            if (p_idx - self.player2.fire()) < 0:
                self.player1.has_been_shot = True
                return self.player1

        if player == self.player2:
            if player.id not in self.fire_vect:
                return self.player2
            if (p_idx + self.player1.fire()) > self.fire_vect_len - 1:
                self.player2.has_been_shot = True
                return self.player2

    def is_game_over(self):
        if self.player1.has_been_shot:
            return self.player2
        if self.player2.has_been_shot:
            return self.player1


class Player:
    def __init__(self, id, fire_rate):
        self.id = id
        self.fire_rate = fire_rate
        self.has_been_shot = False

    def fire(self):
        return self.fire_rate


class GameLoop:
    def __init__(self, player1, player2, battle):
        self.player1 = player1
        self.player2 = player2
        self.battle = battle

    def __enter__(self):
        self._start_time = time.perf_counter_ns()
        self.battle.proc_fire()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        LOGGER.error(f"Time Elapsed: {time.perf_counter_ns() - self._start_time}")


if __name__ == "__main__":
    player1, player2 = Player(id=1, fire_rate=2), Player(id=2, fire_rate=9)
    battle_field = Battle(player1, player2, fire_vect_len=20)
    while True:
        with GameLoop(player1, player1, battle_field) as game:
            res = battle_field.is_game_over()
            if res:
                print(res)
                break
