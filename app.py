# -*- coding: utf-8 -*-

import os
import sys
import game
import data
import sqlite3
import traceback

app_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        try:
            os.remove(os.path.join(app_path, "data", "monopoly.db"))
        except Exception:
            print("Data base not exist => creating")
        match_id = 1
    else:
        match_id = sys.argv[1]
try:
    connetion = sqlite3.connect(os.path.join(app_path, "data", "monopoly.db"))
    cursor = connetion.cursor()

    cursor.execute(
        """ 
    CREATE TABLE if not exists "game"  (
    	"id"	INTEGER,
        "match_id" INTEGER,
    	"perfil"	TEXT,
    	"saldo"	NUMERIC,
    	"propriedades"	TEXT,
    	"posicao_atual"	INTEGER,
    	"rodada"	INTEGER,
    	"ativo"	TEXT,
    	PRIMARY KEY("id"))
    """
    )

    game_simulation = game.monopoly.Monopoly(
        jogadores=data.database.jogadores,
        propriedades=data.database.propriedades,
    ).run()

    for player_id in game_simulation.keys():
        cursor.execute(
            """
            insert into game
                (id, match_id, perfil, saldo, propriedades, posicao_atual, rodada, ativo)
            values
                (null, ?, ?, ?, ?, ?, ?, ?)""",
            [
                match_id,
                game_simulation.get(player_id).get("perfil"),
                game_simulation.get(player_id).get("saldo"),
                str(game_simulation.get(player_id).get("propriedades")),
                game_simulation.get(player_id).get("posicao_atual"),
                game_simulation.get(player_id).get("rodada"),
                game_simulation.get(player_id).get("ativo"),
            ],
        )
    connetion.commit()
    connetion.close()

except Exception:
    traceback.print_exc()
