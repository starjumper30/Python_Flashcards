import os
import io
import argparse


class Card:
    def __init__(self, term, definition, mistakes=0):
        self._term = term
        self.definition = definition
        self.mistakes = mistakes

    @property
    def term(self):
        return self._term

    @property
    def definition(self):
        return self._definition

    @definition.setter
    def definition(self, definition):
        self._definition = definition

    @property
    def mistakes(self):
        return self._mistakes

    @mistakes.setter
    def mistakes(self, mistakes):
        self._mistakes = int(mistakes)

    def reset(self):
        self.mistakes = 0

    def add_mistake(self):
        self.mistakes += 1

    def update(self, definition, mistakes):
        self.definition = definition
        self.mistakes = mistakes

    def csv(self):
        return f'{self.term},{self.definition},{self.mistakes}'

    def __str__(self):
        return f'("{self.term}":"{self.definition}")'

    def __repr__(self):
        return f'Card({self.term}, {self.definition}, {self.mistakes})'


class FlashcardProgram:
    def __init__(self):
        self._log = io.StringIO()
        self._cards = {}
        self._cards_by_def = {}

    def main(self, input_file, output_file):
        if input_file:
            self.import_cards(input_file)

        action = self.get_action()
        while action != 'exit':
            if action == 'add':
                self.input_card()
            elif action == 'remove':
                self.remove_card()
            elif action == 'import':
                self.import_cards()
            elif action == 'export':
                self.export_cards()
            elif action == 'ask':
                self.ask()
            elif action == 'log':
                self.save_log()
            elif action == 'hardest card':
                self.hardest_card()
            elif action == 'reset stats':
                self.reset_stats()
            action = self.get_action()

        if output_file:
            self.export_cards(output_file)
        print('Bye bye!')

    def check_answer(self, answer, card):
        if answer == card.definition:
            self.print('Correct!')
        else:
            if answer in self._cards_by_def:
                matching_term = self._cards_by_def[answer]
                self.print(
                    f'Wrong. The right answer is "{card.definition}", but your definition is correct for "{matching_term}".\n')
            else:
                self.print(f'Wrong. The right answer is "{card.definition}".\n')
            card.add_mistake()

    def ask_cards(self, num_to_ask):
        for i, card in enumerate(self._cards.values()):
            if i >= num_to_ask:
                return i
            self.check_answer(self.input(f'Print the definition of "{card.term}"\n'), card)
        return num_to_ask

    def ask(self):
        total_num_to_ask = int(self.input('How many times to ask?\n'))
        num_cards = len(self._cards)
        num_asked = 0
        while num_asked < total_num_to_ask:
            num_to_ask = total_num_to_ask - num_asked
            if num_to_ask > num_cards:
                num_to_ask = num_cards
            num_asked += self.ask_cards(num_to_ask)

    def input_card(self):
        term = self.input(f'The card\n')
        while term in self._cards:
            term = self.input(f'The card "{term}" already exists. Try again:\n')

        definition = self.input(f'The definition of the card\n')
        while definition in self._cards_by_def:
            definition = self.input(f'The definition "{definition}" already exists. Try again:\n')

        card = Card(term, definition)
        self.add_card(card)
        self.print(f'The pair {card} has been added\n')

    def add_card(self, card):
        self._cards[card.term] = card
        self._cards_by_def[card.definition] = card

    def get_action(self):
        return self.input('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):\n')

    def remove_card(self):
        term = self.input(f'Which card?\n')
        if term in self._cards:
            card = self._cards[term]
            del self._cards[term]
            del self._cards_by_def[card.definition]
            self.print('The card has been removed.\n')
        else:
            self.print(f'Can\'t remove "{term}": there is no such card.\n')

    def import_cards(self, input_file=None):
        file_name = input_file if input_file else self.input('File name:\n')
        if os.path.isfile(file_name):
            with open(file_name, 'rt') as fh:
                total_cards = 0
                for line in fh:
                    term, definition, mistakes = line.strip().split(',')
                    if term in self._cards:
                        self._cards[term].update(definition, mistakes)
                    else:
                        card = Card(term, definition, mistakes)
                        self.add_card(card)
                    total_cards += 1
            self.print(f'{total_cards} cards have been loaded.\n')
        else:
            self.print('File not found.\n')

    def input(self, prompt):
        self._log.write(f'{prompt}')
        value = input(prompt)
        self._log.write(f'{value}\n')
        return value

    def print(self, txt):
        self._log.write(f'{txt}\n')
        print(f'{txt}')

    def export_cards(self, output_file=None):
        file_name = output_file if output_file else self.input('File name:\n')
        with open(file_name, 'wt') as fh:
            for card in self._cards.values():
                print(f'{card.csv()}', file=fh)
        self.print(f'{len(self._cards)} cards have been saved.\n')

    def reset_stats(self):
        for card in self._cards.values():
            card.reset()
        self.print('Card statistics have been reset.\n')

    def hardest_card(self):
        the_list = sorted(self._cards.values(), key=lambda c: c.mistakes)
        if len(the_list) == 0 or the_list[-1].mistakes == 0:
            self.print('There are no cards with errors.\n')
        else:
            list_iter = iter(reversed(the_list))
            the_max_card = the_list[-1]
            the_max = the_max_card.mistakes
            max_cards = []
            card = next(list_iter)
            while card.mistakes == the_max:
                max_cards.append(card.term)
                try:
                    card = next(list_iter)
                except StopIteration:
                    break

            if len(max_cards) == 1:
                self.print(f'The hardest card is "{the_max_card.term}". You have {the_max} errors answering it.\n')
            else:
                self.print(f'The hardest cards are "{"".join(max_cards)}"\n')

    def save_log(self):
        file_name = self.input('File name:\n')
        self.print('The log has been saved.\n')
        with open(file_name, 'wt') as fh:
            print(self._log.getvalue(), file=fh)


def parse_args():
    parser = argparse.ArgumentParser(description='Flashcards')
    parser.add_argument('--import_from', help='File to import cards from', default=None)
    parser.add_argument('--export_to', help='File to export cards to', default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    FlashcardProgram().main(args.import_from, args.export_to)
