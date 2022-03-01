from .game_loop import Player, Battle, GameLoop


def test_game_loop():
    player1, player2 = Player(id=1, fire_rate=2), Player(id=2, fire_rate=4)
    battle_field = Battle(player1, player2, fire_vect_len=20)
    while True:
        with GameLoop(player1, player1, battle_field) as game:
            res = battle_field.is_game_over()
            if res:
                assert res == player2
                break
