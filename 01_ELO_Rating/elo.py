# import random
from random import shuffle as random_shuffle, choices as random_choices
from enum import Enum
from typing import List, Tuple
from statistics import mean as stats_mean, stdev as stats_stdev

from utils.logging import logger

class MatchResult(Enum):
    WIN = 1.0
    DRAW = 0.5
    LOSS = 0.0

class Player:
    def __init__(self, name: str, initial_rating: float = 1200):
        self.name = name
        self.rating = initial_rating

    def __str__(self):
        return f"{self.name} (Rating: {self.rating})"

class EloRating:
    def __init__(self, k: int = 32):
        self.k = k

    def expected_score(self, player_rating: float, opponent_rating: float) -> float:
        return 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))

    def update_rating(self, player: Player, opponent: Player, result: MatchResult):
        expected = self.expected_score(player.rating, opponent.rating)
        player.rating += self.k * (result.value - expected)
        player.rating = round(player.rating, 2)

class ChessTournament:
    def __init__(self, players: List[Player], num_rounds: int = 1):
        self.players = players
        self.num_rounds = num_rounds
        self.elo_system = EloRating()
        self.schedule = self.create_schedule()

    def create_schedule(self) -> List[Tuple[int, int]]:
        num_players = len(self.players)
        schedule: List[Tuple[int, int]] = []
        for i in range(num_players):
            for j in range(i + 1, num_players):
                schedule.append((i, j))
                schedule.append((j, i))
        schedule = schedule * self.num_rounds
        logger.debug(schedule)
        random_shuffle(schedule)
        return schedule

    def simulate_match(self, player_one: Player, player_two: Player) -> Tuple[MatchResult, MatchResult]:
        expected_score_player_one = self.elo_system.expected_score(player_one.rating, player_two.rating)
        
        # Determine result based on weighted probabilities
        result = random_choices(
            population=[MatchResult.WIN, MatchResult.DRAW, MatchResult.LOSS],
            weights=[expected_score_player_one, 0.3, 1 - expected_score_player_one],
            k=1
        )[0]
        
        if result == MatchResult.WIN:
            return MatchResult.WIN, MatchResult.LOSS
        elif result == MatchResult.LOSS:
            return MatchResult.LOSS, MatchResult.WIN
        else:
            return MatchResult.DRAW, MatchResult.DRAW

    def play_tournament(self):
        match_number = 1
        while self.schedule:
            logger.debug(f"Match {match_number}")
            random_shuffle(self.schedule)
            match_indices = self.schedule.pop()
            player_one = self.players[match_indices[0]]
            player_two = self.players[match_indices[1]]
            player_one_result, player_two_result = self.simulate_match(player_one, player_two)
            logger.debug(f"Match: {player_one.name} ({player_one.rating}) vs {player_two.name} ({player_two.rating})")
            self.elo_system.update_rating(player_two, player_one, player_two_result)
            self.elo_system.update_rating(player_one, player_two, player_one_result)
            
            
            logger.debug(f"Result: {player_one_result.name} vs {player_two_result.name}")
            logger.debug(f"Updated Ratings: {player_one.name} ({player_one.rating}), {player_two.name} ({player_two.rating})")
            match_number += 1
            logger.debug("\n")

if __name__ == "__main__":
    NUM_PLAYERS = 5
    NUM_ROUNDS = 2
    NUM_GAMES = int(NUM_ROUNDS * NUM_PLAYERS * (NUM_PLAYERS + 1) / 2)

    # Initialize players
    players = [Player(f"Player {i+1}") for i in range(NUM_PLAYERS)]

    # Create and run the tournament
    tournament = ChessTournament(players=players, num_rounds=NUM_ROUNDS)
    tournament.play_tournament()

    ratings = [player.rating for player in players]
    mean = stats_mean(ratings)
    stdev = stats_stdev(ratings)

    # Print final ratings
    print(f"Final Rating after {NUM_GAMES} games:")
    for player in players:
        logger.debug(player)
    logger.info(f"Mean - {mean}; Standard Deviation - {stdev}")