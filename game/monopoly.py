# -*- coding: utf-8 -*-

import os
import uuid
import time
import json
import random
import logging
import traceback

DEBUG = False


class Monopoly(object):
    def __init__(self, *args: None, propriedades: dict, jogadores: dict) -> None:
        self.propriedades = propriedades
        self.jogadores = jogadores
        self.round = 1
        self.loop = True
        if DEBUG:
            logging.basicConfig(
                filename=os.path.join("logs", str(uuid.uuid1()) + "_log.log"),
                encoding="utf-8",
                level=logging.DEBUG,
            )

    def verify_only_winner(self) -> bool:
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

    def total_rounds_when_finish(self) -> int:
        players = []
        max_rounds = 0
        for i in range(1, 5):
            player = self.jogadores.get(i)
            if player.get("ativo") == "S":
                players.append(i)
        for player in players:
            if self.jogadores.get(player).get("rodada") > max_rounds:
                max_rounds = self.jogadores.get(player).get("rodada")
        return max_rounds

    def player_loser(self, id_jogador: int) -> None:
        """REMOVE AS PROPRIEDADES DO JOGADOR"""
        for state in self.jogadores.get(id_jogador).get("propriedades"):
            self.propriedades.get(state).update({"proprietario": 0})
        self.jogadores.get(id_jogador).update({"propriedades": []})

    def roll_the_dice(self) -> int:
        """GERA UM NUMERO ALEATÓRIO ENTRE 1 E 6"""
        return random.randint(1, 6)

    def run_tiebreaker(self) -> None:
        """APLICA A REGRA DO DESEMPATE"""
        players_active = {}
        for key in self.jogadores.keys():
            if self.jogadores.get(key).get("ativo") == "S":
                players_active.update(
                    {
                        self.jogadores.get(key).get("posicao_atual"): [
                            key,
                            self.jogadores.get(key).get("saldo"),
                        ]
                    }
                )
        list_position = sorted(players_active.keys(), reverse=True)
        key_win = None
        amount = -1
        for i in list_position:
            if players_active.get(i)[1] > amount:
                amount = players_active.get(i)[1]
                key_win = players_active.get(i)[0]
        for key in self.jogadores.keys():
            if key != key_win:
                self.jogadores.get(key).update({"ativo": "N"})
        key_win = None
        amount = -1

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

    def run(self) -> json.dumps:
        """INICIA A SIMULAÇÃO DO JOGO"""
        try:
            while self.loop == True:
                stop = self.verify_only_winner()
                if stop or self.round > 1000:
                    if DEBUG:
                        logging.warning("Jogo acabou...")

                    if self.round > 1000:
                        self.run_tiebreaker()
                    with open(
                        os.path.join(os.path.curdir, "players_result.json"), "w"
                    ) as file:
                        file.write(json.dumps(self.jogadores, indent=3))

                        return self.jogadores

                for id_jogador in self.jogadores.keys():
                    current_amount = float(self.jogadores.get(id_jogador).get("saldo"))
                    current_position = self.jogadores.get(id_jogador).get(
                        "posicao_atual"
                    )
                    player_active = self.jogadores.get(id_jogador).get("ativo")
                    player_estates = self.jogadores.get(id_jogador).get("propriedades")

                    if player_active == "S":
                        self.jogadores.get(id_jogador).update(
                            {
                                "posicao_atual": self.board_position(
                                    current_position=current_position,
                                    step=self.roll_the_dice(),
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
                        if DEBUG:
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
                            self.propriedades.get(current_position).get("proprietario")
                            == 0
                            and current_amount >= price_sale
                        ):  # buy
                            if DEBUG:
                                logging.warning("Comprou...")
                            self.propriedades.get(current_position).update(
                                {"proprietario": id_jogador}
                            )
                            self.jogadores.get(id_jogador).update(
                                {
                                    "propriedades": player_estates + [current_position],
                                    "saldo": current_amount - price_sale,
                                }
                            )

                        if (
                            self.propriedades.get(current_position).get("proprietario")
                            in (2, 3, 4)
                            and current_amount >= price_rent
                        ):  # rent
                            if DEBUG:
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
                                {"saldo": current_amount_player_pay_rent + price_rent}
                            )
                            pay_rent_in_round = "S"

                        if (
                            self.propriedades.get(current_position).get("proprietario")
                            != 1
                            and current_amount < price_rent
                            and pay_rent_in_round == "N"
                        ):  # rent
                            if DEBUG:
                                logging.warning("Se ferrou...")
                            self.jogadores.get(id_jogador).update({"ativo": "N"})
                            self.player_loser(id_jogador=id_jogador)

                        if DEBUG:
                            logging.info("# # # # # # # # # # # #\n")

                    if (
                        self.jogadores.get(id_jogador).get("perfil") == "exigente"
                        and player_active == "S"
                    ):
                        if DEBUG:
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
                            self.propriedades.get(current_position).get("proprietario")
                            == 0
                            and current_amount >= price_sale
                            and price_rent > 50.0
                        ):  # buy
                            if DEBUG:
                                logging.warning("Comprou...")
                            self.propriedades.get(current_position).update(
                                {"proprietario": id_jogador}
                            )
                            self.jogadores.get(id_jogador).update(
                                {
                                    "propriedades": player_estates + [current_position],
                                    "saldo": current_amount - price_sale,
                                }
                            )

                        if (
                            self.propriedades.get(current_position).get("proprietario")
                            in (1, 3, 4)
                            and current_amount >= price_rent
                        ):  # rent
                            if DEBUG:
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
                                {"saldo": current_amount_player_pay_rent + price_rent}
                            )

                        if (
                            self.propriedades.get(current_position).get("proprietario")
                            != 2
                            and current_amount < price_rent
                            and pay_rent_in_round == "N"
                        ):
                            if DEBUG:
                                logging.warning("Se ferrou...")
                            self.jogadores.get(id_jogador).update({"ativo": "N"})
                            self.player_loser(id_jogador=id_jogador)

                        if DEBUG:
                            logging.info("# # # # # # # # # # # #\n")

                    if (
                        self.jogadores.get(id_jogador).get("perfil") == "cauteloso"
                        and player_active == "S"
                    ):

                        if DEBUG:
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
                            self.propriedades.get(current_position).get("proprietario")
                            == 0
                            and (current_amount - price_sale) >= 80
                        ):  # buy
                            if DEBUG:
                                logging.warning("Comprou...")
                            self.propriedades.get(current_position).update(
                                {"proprietario": id_jogador}
                            )
                            self.jogadores.get(id_jogador).update(
                                {
                                    "propriedades": player_estates + [current_position],
                                    "saldo": current_amount - price_sale,
                                }
                            )

                        if (
                            self.propriedades.get(current_position).get("proprietario")
                            in (1, 2, 4)
                            and current_amount >= price_rent
                        ):  # rent
                            if DEBUG:
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
                                {"saldo": current_amount_player_pay_rent + price_rent}
                            )

                        if (
                            self.propriedades.get(current_position).get("proprietario")
                            != 3
                            and current_amount < price_rent
                            and pay_rent_in_round == "N"
                        ):
                            if DEBUG:
                                logging.warning("Jogador perdeu o jogo...")
                            self.jogadores.get(id_jogador).update({"ativo": "N"})
                            self.player_loser(id_jogador=id_jogador)

                        if DEBUG:
                            logging.info("# # # # # # # # # # # #\n")

                    if (
                        self.jogadores.get(id_jogador).get("perfil") == "aleatorio"
                        and player_active == "S"
                    ):
                        if DEBUG:
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
                            self.propriedades.get(current_position).get("proprietario")
                            == 0
                            and random.randint(0, 1) == 1
                            and current_amount > price_sale
                        ):  # buy
                            if DEBUG:
                                logging.warning("Comprou...")
                            self.propriedades.get(current_position).update(
                                {"proprietario": id_jogador}
                            )
                            self.jogadores.get(id_jogador).update(
                                {
                                    "propriedades": player_estates + [current_position],
                                    "saldo": current_amount - price_sale,
                                }
                            )

                        if (
                            self.propriedades.get(current_position).get("proprietario")
                            in (1, 2, 3)
                            and current_amount >= price_rent
                        ):  # rent
                            if DEBUG:
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
                                {"saldo": current_amount_player_pay_rent + price_rent}
                            )

                        if (
                            self.propriedades.get(current_position).get("proprietario")
                            != 4
                            and current_amount < price_rent
                            and pay_rent_in_round == "N"
                        ):
                            if DEBUG:
                                logging.warning("Jogador perdeu o jogo...")
                            self.jogadores.get(id_jogador).update({"ativo": "N"})
                            self.player_loser(id_jogador=id_jogador)

                        if DEBUG:
                            logging.info("# # # # # # # # # # # #\n")

                self.round += 1

        except Exception:
            self.loop = False
            traceback.print_exc()
