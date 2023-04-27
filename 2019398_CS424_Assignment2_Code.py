import collections

class Grammar:
    def __init__(self, productions):
        self.productions = productions
        self.non_terminals = set(p[0] for p in productions)
        self.terminals = set(token for p in productions for token in p[1]) - self.non_terminals
        self.terminals.add('$')  

    def get_production(self, index):
        return self.productions[index]

    def closure(self, item_set):
        closure_set = set(item_set)
        added = True
        while added:
            added = False
            for item in list(closure_set):
                after_dot = item.production[1][item.dot_pos] if item.dot_pos < len(item.production[1]) else None
                if after_dot in self.non_terminals:
                    for prod_index, prod in enumerate(self.productions):
                        if prod[0] == after_dot:
                            new_item = Item(prod_index, 0, item.lookahead)
                            if new_item not in closure_set:
                                closure_set.add(new_item)
                                added = True
        return closure_set

    def goto(self, item_set, symbol):
        new_item_set = set(item.advance() for item in item_set if item.dot_pos < len(item.production[1]) and item.production[1][item.dot_pos] == symbol)
        return self.closure(new_item_set) if new_item_set and symbol in self.non_terminals else new_item_set

class Item:
    def __init__(self, production_index, dot_pos, lookahead):
        self.production_index = production_index
        self.dot_pos = dot_pos
        self.lookahead = lookahead

    def advance(self):
        return Item(self.production_index, self.dot_pos + 1, self.lookahead)

    @property
    def production(self):
        return grammar.get_production(self.production_index)

    def __eq__(self, other):
        return (
            self.production_index == other.production_index
            and self.dot_pos == other.dot_pos
            and self.lookahead == other.lookahead
        )

    def __hash__(self):
        return hash((self.production_index, self.dot_pos, self.lookahead))

    def __repr__(self):
        return f"({self.production_index}, {self.dot_pos}, {self.lookahead})"

def build_lr1_table(grammar):
    canonical_collection = [grammar.closure({Item(0, 0, '$')})]
    lr1_table = collections.defaultdict(dict)
    for i, item_set in enumerate(canonical_collection):
        for symbol in grammar.terminals | grammar.non_terminals:
            goto_set = grammar.goto(item_set, symbol)
            if goto_set and goto_set not in canonical_collection:
                canonical_collection.append(goto_set)
            if goto_set:
                action = 'S' if symbol in grammar.terminals else 'G'
                lr1_table[i][symbol] = f"{action}{canonical_collection.index(goto_set)}"
        for item in item_set:
            if item.dot_pos == len(item.production[1]):
                if item.production[0] == 'S' and item.lookahead == '$':
                    lr1_table[i]['$'] = 'ACCEPT'
                else:
                    lr1_table[i][item.lookahead] = f"R{item.production_index}"
    return lr1_table

def parse(lr1_table, grammar, input_string):
    stack = [0]
    input_string = input_string + ' $'
    cursor = 0

    while True:
        current_state = stack[-1]
        current_symbol = input_string[cursor]
        action = lr1_table[current_state].get(current_symbol)

        if not action:
            return False

        print(f"Stack: {stack}, Input: {input_string[cursor:]}, Action: {action}")

        if action == 'ACCEPT':
            return True

        action_type, arg = action[0], int(action[1:])

        if action_type == 'S':
            stack.append(current_symbol)
            stack.append(arg)
            cursor += 1
        elif action_type == 'R':
            production = grammar.get_production(arg)
            stack = stack[:-2 * len(production[1])]
            current_state = stack[-1]
            non_terminal = production[0]
            goto_action = lr1_table[current_state].get(non_terminal)
            if not goto_action:
                return False
            goto_state = int(goto_action[1:])
            stack.append(non_terminal)
            stack.append(goto_state)
        elif action_type == 'G':
            stack.append(arg)
            stack.append(lr1_table[stack[-2]][stack[-1]][1:])

grammar = Grammar([
    ('E', 'T+E'),
    ('E', 'T'),
    ('T', 'F*T'),
    ('T', 'F'),
    ('F', 'id'),
])

lr1_table = build_lr1_table(grammar)
print(lr1_table)
input_string = "id+id*id"
print(parse(lr1_table, grammar, input_string))