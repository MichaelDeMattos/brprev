# -*- coding: utf-8 -*-

import os
import time
import sqlite3
import traceback
import subprocess

if __name__ == "__main__":
    try:
        app_path = os.path.dirname(os.path.abspath(__file__))
        os.truncate(os.path.join(app_path, "players_result.json"), 0)
        os.remove(os.path.join(app_path, "data", "monopoly.db"))
    except Exception:
        print("Data base not exist => creating")

    print(f"Processando simulação\nAguarde...")
    for simulation in range(1, 301):
        subprocess.call(
            ["python3", f"{os.path.join(app_path, 'app.py')}", str(simulation)]
        )

    try:
        connetion = sqlite3.connect(os.path.join(app_path, "data", "monopoly.db"))
        cursor = connetion.cursor()

        # 1 - Quantas partidas terminam por time out (1000 rodadas)
        sqlquery = """
            select count(*) 
            from game
            where rodada = 1000
        """
        data = cursor.execute(sqlquery).fetchone()
        print("#" * 50)
        print("Partidas terminam por timeout (1000 rodadas):", data[0] if data else 0)

        # 2 - Quantos turnos em média demora uma partida
        sqlquery = """
            select sum(rodada)
                from game
            where ativo = 'S'
        """
        data = cursor.execute(sqlquery).fetchone()
        print(
            "Qtd. de Turnos em média por partida:",
            round(data[0] / 300) if data else 0,
        )

        # 3 - Qual a porcentagem de vitórias por comportamento dos jogadores
        sqlquery = """
            select perfil, count(*) 
                from game
            where ativo = 'S' 
            group by perfil
        """
        aleatorio, cauteloso, exigente, impulsivo = cursor.execute(sqlquery).fetchall()
        print(
            "% Vitórias por comportamento dos jogadores:\n",
            f"Aleatorio: {round((aleatorio[1]/300)*100, 2)} %\n",
            f"Cauteloso: {round((cauteloso[1]/300)*100, 2)} %\n",
            f"Exigente: {round((exigente[1]/300)*100, 2)} %\n",
            f"Impulsivo: {round((impulsivo[1]/300)*100, 2)}%",
        )

        # 4 - Qual o comportamento que mais vence
        print(f"""Comportamento que mais venceu: {str(max([aleatorio, cauteloso, exigente, impulsivo], key=lambda item: item[1])[0]).capitalize()}\n{'#' * 50}""")

    except Exception:
        traceback.print_exc()
