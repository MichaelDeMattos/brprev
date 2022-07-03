# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    app.py                                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: michael.ortiz <michael.ortiz@dotpyc.com    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2022/07/01 20:37:27 by michael.ort       #+#    #+#              #
#    Updated: 2022/07/03 07:22:25 by michael.ort      ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

# -*- coding: utf-8 -*-

import os
import time
import json
import random
import logging
import traceback
from database import jogadores, propriedades

DEBUG = True


class Monopoly(object):
    def __init__(self, *args: None, propriedades: dict, jogadores: dict) -> None:
        self.propriedades = propriedades
        self.jogadores = jogadores
        self.round = 1
        self.buy_now = "S"
        self.loop = True
        os.truncate(os.path.join(os.path.curdir, "log.log"), 0)
        logging.basicConfig(filename="log.log", encoding="utf-8", level=logging.DEBUG)

    def verify_winner(self) -> bool:
        """VERIFICA SE EXISTE SOMENTE UM JOGADOR ATIVO"""
        active = 0
        for i in range(1, 5):
            player = self.jogadores.get(i)
            if player.get("ativo") == "S":
                active += 1
        if active == 1:
            return True
        else:
            return False

    def player_loser(self, id_jogador: int) -> None:
        """REMOVE AS PROPRIEDADES DO JOGADOR"""
        for state in self.jogadores.get(id_jogador).get("propriedades"):
            self.propriedades.get(state).update({"proprietario": 0})
        self.jogadores.get(id_jogador).update({"propriedades": []})

    def roll_the_dice(self) -> int:
        """GERA UM NUMERO ALEATÓRIO ENTRE 1 E 6"""
        return random.randint(1, 6)

    def board_position(
        self,
        current_position: int,
        step: int,
        max_position: int,
        id_jogador: int,
        current_amount: float,
    ) -> int:
        """DEFINE A POSIÇÃO DO JOGADOR NO TABULEIRO"""
        new_position = current_position + step
        if new_position > 20:
            self.jogadores.get(id_jogador).update({"saldo": current_amount + 100})
            new_position = new_position - max_position
            return new_position
        else:
            return new_position

    def run(self, simulations: int) -> json.dumps:
        """INICIA A SIMULAÇÃO DO JOGO"""
        try:
            timeout = 0
            med_round = 0
            for simulation in range(0, simulations):
                while self.loop == True:
                    stop = self.verify_winner()
                    if stop or self.round > 1000:
                        logging.warning("Jogo acabou...")
                        with open(os.path.join(os.path.curdir, "players_result.json") , "w") as file:
                            file.write(json.dumps(self.jogadores, indent=3))
                            if self.round > 1000:
                                timeout += 1
                        
                        with open(os.path.join(os.path.curdir, "players_result.json") , "r") as file:
                            totals = file.read()
                            print(totals)
                        
                        break

                    for id_jogador in self.jogadores.keys():
                        step = self.roll_the_dice()
                        current_amount = float(jogadores.get(id_jogador).get("saldo"))
                        current_position = self.jogadores.get(id_jogador).get(
                            "posicao_atual"
                        )
                        player_active = self.jogadores.get(id_jogador).get("ativo")
                        player_estates = self.jogadores.get(id_jogador).get(
                            "propriedades"
                        )

                        if player_active == "S":
                            self.jogadores.get(id_jogador).update(
                                {
                                    "posicao_atual": self.board_position(
                                        current_position=current_position,
                                        step=step,
                                        max_position=20,
                                        id_jogador=id_jogador,
                                        current_amount=current_amount,
                                    ),
                                    "rodada": self.round,
                                }
                            )

                        current_position = self.jogadores.get(id_jogador).get(
                            "posicao_atual"
                        )

                        price_sale = float(
                            self.propriedades.get(current_position).get("venda")
                        )
                        price_rent = float(
                            self.propriedades.get(current_position).get("aluguel")
                        )

                        if current_amount <= 0.0 and player_active != "N":
                            self.jogadores.get(id_jogador).update({"ativo": "N"})
                            self.player_loser(id_jogador=id_jogador)

                        if (
                            self.jogadores.get(id_jogador).get("perfil") == "impulsivo"
                            and player_active == "S"
                        ):
                            logging.info("# # # # # # # # # # # #")
                            logging.info("Perfil Impulsivo")
                            logging.info(f"Rodada: {self.round}")
                            logging.info(
                                f"Proprietario: {self.propriedades.get(current_position).get('proprietario')}"
                            )
                            logging.info(f"Preço de venda do imovel: {price_sale}")
                            logging.info(f"Preço do aluguel do imovel: {price_rent}")
                            logging.info(f"Saldo na conta {current_amount}")
                            pay_rent_in_round = "N"

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                == 0
                                and current_amount >= price_sale
                            ):  # buy
                                logging.warning("Comprou...")
                                self.propriedades.get(current_position).update(
                                    {"proprietario": id_jogador}
                                )
                                self.jogadores.get(id_jogador).update(
                                    {
                                        "propriedades": player_estates
                                        + [current_position],
                                        "saldo": current_amount - price_sale,
                                    }
                                )

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                in (2, 3, 4)
                                and current_amount >= price_rent
                            ):  # rent
                                logging.warning("Pagou aluguel...")
                                logging.info(
                                    f"Para o proprietário: {self.propriedades.get(current_position).get('proprietario')}"
                                )
                                logging.info(f"Saldo {current_amount}")
                                logging.info(f"Preço do aluguel {price_rent}")
                                self.jogadores.get(id_jogador).update(
                                    {"saldo": current_amount - price_rent}
                                )
                                id_player_pay_rent = self.propriedades.get(
                                    current_position
                                ).get("proprietario")
                                current_amount_player_pay_rent = float(
                                    self.jogadores.get(id_jogador).get("saldo")
                                )
                                self.jogadores.get(id_player_pay_rent).update(
                                    {
                                        "saldo": current_amount_player_pay_rent
                                        + price_rent
                                    }
                                )
                                pay_rent_in_round = "S"

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                != 1
                                and current_amount < price_rent
                                and pay_rent_in_round == "N"
                            ):  # rent
                                logging.warning("Se ferrou...")
                                self.jogadores.get(id_jogador).update({"ativo": "N"})
                                self.player_loser(id_jogador=id_jogador)

                            logging.info("# # # # # # # # # # # #\n")

                        if (
                            self.jogadores.get(id_jogador).get("perfil") == "exigente"
                            and player_active == "S"
                        ):
                            logging.info("# # # # # # # # # # # #")
                            logging.info("Perfil exigente")
                            logging.info(f"Rodada: {self.round}")
                            logging.info(
                                f"Proprietario: {self.propriedades.get(current_position).get('proprietario')}"
                            )
                            logging.info(f"Preço de venda do imovel: {price_sale}")
                            logging.info(f"Preço do aluguel do imovel: {price_rent}")
                            logging.info(f"Saldo na conta {current_amount}")
                            pay_rent_in_round = "N"

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                == 0
                                and current_amount >= price_sale
                                and price_rent > 50.0
                            ):  # buy
                                logging.warning("Comprou...")
                                self.propriedades.get(current_position).update(
                                    {"proprietario": id_jogador}
                                )
                                self.jogadores.get(id_jogador).update(
                                    {
                                        "propriedades": player_estates
                                        + [current_position],
                                        "saldo": current_amount - price_sale,
                                    }
                                )

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                in (1, 3, 4)
                                and current_amount >= price_rent
                            ):  # rent
                                logging.warning("Pagou aluguel...")
                                logging.info(
                                    f"Para o proprietário: {self.propriedades.get(current_position).get('proprietario')}"
                                )
                                logging.info(f"Saldo {current_amount}")
                                logging.info(f"Preço do aluguel {price_rent}")
                                pay_rent_in_round = "S"
                                self.jogadores.get(id_jogador).update(
                                    {"saldo": current_amount - price_rent}
                                )
                                id_player_pay_rent = self.propriedades.get(
                                    current_position
                                ).get("proprietario")
                                current_amount_player_pay_rent = self.jogadores.get(
                                    id_jogador
                                ).get("saldo")
                                self.jogadores.get(id_player_pay_rent).update(
                                    {
                                        "saldo": current_amount_player_pay_rent
                                        + price_rent
                                    }
                                )

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                != 2
                                and current_amount < price_rent
                                and pay_rent_in_round == "N"
                            ):
                                logging.warning("Se ferrou...")
                                self.jogadores.get(id_jogador).update({"ativo": "N"})
                                self.player_loser(id_jogador=id_jogador)

                            logging.info("# # # # # # # # # # # #\n")

                        if (
                            self.jogadores.get(id_jogador).get("perfil") == "cauteloso"
                            and player_active == "S"
                        ):
                            logging.info("# # # # # # # # # # # #")
                            logging.info("Perfil cauteloso")
                            logging.info(f"Rodada: {self.round}")
                            logging.info(
                                f"Proprietario: {self.propriedades.get(current_position).get('proprietario')}"
                            )
                            logging.info(f"Preço de venda do imovel: {price_sale}")
                            logging.info(f"Preço do aluguel do imovel: {price_rent}")
                            logging.info(f"Saldo na conta {current_amount}")
                            pay_rent_in_round = "N"

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                == 0
                                and (current_amount - price_sale) >= 80
                            ):  # buy
                                logging.warning("Comprou...")
                                self.propriedades.get(current_position).update(
                                    {"proprietario": id_jogador}
                                )
                                self.jogadores.get(id_jogador).update(
                                    {
                                        "propriedades": player_estates
                                        + [current_position],
                                        "saldo": current_amount - price_sale,
                                    }
                                )

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                in (1, 2, 4)
                                and current_amount >= price_rent
                            ):  # rent
                                logging.warning("Pagou aluguel...")
                                logging.info(
                                    f"Para o proprietário: {self.propriedades.get(current_position).get('proprietario')}"
                                )
                                logging.info(f"Saldo {current_amount}")
                                logging.info(f"Preço do aluguel {price_rent}")
                                pay_rent_in_round = "S"
                                self.jogadores.get(id_jogador).update(
                                    {"saldo": current_amount - price_rent}
                                )
                                id_player_pay_rent = self.propriedades.get(
                                    current_position
                                ).get("proprietario")
                                current_amount_player_pay_rent = self.jogadores.get(
                                    id_jogador
                                ).get("saldo")
                                self.jogadores.get(id_player_pay_rent).update(
                                    {
                                        "saldo": current_amount_player_pay_rent
                                        + price_rent
                                    }
                                )

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                != 3
                                and current_amount < price_rent
                                and pay_rent_in_round == "N"
                            ):
                                logging.warning("Jogador perdeu o jogo...")
                                self.jogadores.get(id_jogador).update({"ativo": "N"})
                                self.player_loser(id_jogador=id_jogador)

                            logging.info("# # # # # # # # # # # #\n")

                        if (
                            self.jogadores.get(id_jogador).get("perfil") == "aleatorio"
                            and player_active == "S"
                        ):
                            logging.info("# # # # # # # # # # # #")
                            logging.info("Perfil aleatorio")
                            logging.info(f"Rodada: {self.round}")
                            logging.info(
                                f"Proprietario: {self.propriedades.get(current_position).get('proprietario')}"
                            )
                            logging.info(f"Preço de venda do imovel: {price_sale}")
                            logging.info(f"Preço do aluguel do imovel: {price_rent}")
                            logging.info(f"Saldo na conta: {current_amount}")
                            pay_rent_in_round = "N"

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                == 0
                                and random.randint(0, 1) == 1
                                and current_amount > price_sale
                            ):  # buy
                                logging.warning("Comprou...")
                                self.propriedades.get(current_position).update(
                                    {"proprietario": id_jogador}
                                )
                                self.jogadores.get(id_jogador).update(
                                    {
                                        "propriedades": player_estates
                                        + [current_position],
                                        "saldo": current_amount - price_sale,
                                    }
                                )

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                in (1, 2, 3)
                                and current_amount >= price_rent
                            ):  # rent
                                logging.warning("Pagou aluguel...")
                                logging.info(
                                    f"Para o proprietário: {self.propriedades.get(current_position).get('proprietario')}"
                                )
                                logging.info(f"Saldo {current_amount}")
                                logging.info(f"Preço do aluguel {price_rent}\n")
                                pay_rent_in_round = "S"
                                self.jogadores.get(id_jogador).update(
                                    {"saldo": current_amount - price_rent}
                                )
                                id_player_pay_rent = self.propriedades.get(
                                    current_position
                                ).get("proprietario")
                                current_amount_player_pay_rent = self.jogadores.get(
                                    id_jogador
                                ).get("saldo")
                                self.jogadores.get(id_player_pay_rent).update(
                                    {
                                        "saldo": current_amount_player_pay_rent
                                        + price_rent
                                    }
                                )

                            if (
                                self.propriedades.get(current_position).get(
                                    "proprietario"
                                )
                                != 4
                                and current_amount < price_rent
                                and pay_rent_in_round == "N"
                            ):
                                logging.warning("Jogador perdeu o jogo...")
                                self.jogadores.get(id_jogador).update({"ativo": "N"})
                                self.player_loser(id_jogador=id_jogador)

                            logging.info("# # # # # # # # # # # #\n")

                    self.round += 1
                
            print(timeout)
            
            

        except Exception:
            traceback.print_exc()


Monopoly(jogadores=jogadores, propriedades=propriedades).run(simulations=300)
