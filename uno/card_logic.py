from __future__ import annotations
from utils import UIDObj, ComponentManager
from collections import OrderedDict
from enum import Enum
import random

try:
    from game_logic import Player
except ImportError:
    pass

class CardType(Enum):
    NUMBER = "number"
    JOKER = "joker"

class CardColor(Enum):
    NO_COLOR = "no_color"
    RED = "red"
    GRENN = "green"
    BLUE = "blue"
    YELLOW = "yellow"

class Card(UIDObj):
    def __init__(self, card_type:CardType):
        super().__init__()
        self.card_type = card_type
        self.owner = None

    def get_stack_based_on_owner(self, owner_uid:str):
        for uid, stack_obj in ComponentManager.iterate_uid_objects(Stack):
            if stack_obj.owner == owner_uid:
                return stack_obj
        raise ValueError(f"No stack found for owner UID: {owner_uid}")

    def transfer_owner(self, owner_uid:str, other_uid:str, *, forced=False):
        if self.owner is None:
            raise ValueError(f"Card cannot be transferred to {other_uid} because it has no previous owner")
        if self.owner != owner_uid and not forced:
            raise ValueError(f"Card {self.uid} does not belong to {owner_uid}")

        owner_stack = self.get_stack_based_on_owner(owner_uid)
        other_stack = self.get_stack_based_on_owner(other_uid)

        owner_stack.remove_card(self)
        other_stack.add_card(self)
        self.owner = other_uid

    def __str__(self):
        return f"{self.card_type} {self.owner}"

class NumberCard(Card):
    def __init__(self, number:int, color:CardColor):
        super().__init__(CardType.number)
        self.__number = number
        self.__color = color

    @property
    def number(self):
        return self.__number

    @property
    def color(self):
        return self.__color

    def __str__(self):
        return f"{self.color.value} {self.number}"

class JokerCard(Card):
    def __init__(self, color:CardColor, title:str):
        super().__init__(CardType.joker)
        self.__color = color
        self.__title = title

    def make_action(self, next_player):
        if self.title.startswith("draw"):
            _, count = self.title.split(" ")
            global_cards = ComponentManager.get_component("draw")

            for _ in range(int(count)):
                random_card_uid = random.choice(list(global_cards.cards))
                random_card_obj = ComponentManager.get_uid_object(random_card_uid)
                random_card_obj.transfer_owner("draw", next_player.uid, forced=True)

    @property
    def color(self):
        return self.__color

    @property
    def title(self):
        return self.__title

    def __str__(self):
        return f"{self.color.value} {self.title}" if self.color != CardColor.NO_COLOR else f"{self.title}"

class Stack(UIDObj):
    def __init__(self, owner:str, cards:dict[str, Card]):
        super().__init__()
        self.cards = OrderedDict(sorted(cards.items(), key=lambda item: item[1].color.value))
        self.owner = owner
        self.last_added_card = None

    def get_card_per_index(self, index:int):
        try:
            return list(self.cards.values())[index]
        except IndexError:
            raise ValueError(f"No card at index: {index}")

    def add_card(self, card_obj:Card):
        self.cards[card_obj.uid] = card_obj
        self.last_added_card = card_obj
        self.cards = OrderedDict(sorted(self.cards.items(), key=lambda item: item[1].color.value))

    def remove_card(self, card_obj:Card):
        if card_obj.uid in self.cards:
            del self.cards[card_obj.uid]
        else:
            raise ValueError(f"Card with UID {card_obj.uid} not found in stack")

    def __str__(self):
        return "\n".join(f"{index + 1}: {card}" for index, card in enumerate(self.cards.values()))
