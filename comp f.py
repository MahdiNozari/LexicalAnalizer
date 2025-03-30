import re

class Lexer:
    def __init__(self, input_code):
        self.input_code = input_code
        self.tokens = []
        self.delimiter_pattern = r'[\(\)\{\};]'
        self.operator_pattern = r'(\+\+|\-\-|==|\+=|\-=|\*=|/=|<=|>=|[\+\-\*\/=<>])'
        self.keyword_pattern = r'\b(if|else|for|get|print|int|double)\b'
        self.identifier_pattern = r'[a-zA-Z_][a-zA-Z0-9_]*'
        self.int_pattern = r'^[1-9]\d*$'
        self.double_pattern = r'^[1-9]\d*\.\d+$'
        self.valid_characters_pattern = r'[a-zA-Z0-9\s\(\)\{\};\+\-\*\/=<>!\".\\\\]'
        self.error_occurred = False

    def is_valid_identifier(self,token):
        return re.match(self.identifier_pattern, token) is not None

    def add_current_token(self, current_token):
        if current_token:
            if current_token.startswith('_') and not current_token.startswith('__'):
                self.handle_error()
            elif re.match(self.keyword_pattern, current_token):
                self.tokens.append(('Keyword', current_token))
            elif re.match(self.int_pattern, current_token):
                self.tokens.append(('IntToken', current_token))
            elif re.match(self.double_pattern, current_token):
                self.tokens.append(('DoubleToken', current_token))
            elif self.is_valid_identifier(current_token):
                self.tokens.append(('IdentifierToken', current_token))
            else:
                self.handle_error()

    def handle_error(self):
        self.error_occurred = True

    def tokenize(self):
        current_token = ''
        inside_comment = False
        i = 0
        while i < len(self.input_code):
            char = self.input_code[i]
            i += 1

            if not re.match(self.valid_characters_pattern, char):
                self.handle_error()
                return self

            if char == '\\' and not inside_comment:
                lookahead = self.input_code[i] if i < len(self.input_code) else None
                if lookahead == '*':
                    inside_comment = True
                    i += 1
                    continue
                elif lookahead == '\\':
                    while char != '\n' and i < len(self.input_code):
                        char = self.input_code[i]
                        i += 1
                    continue
            elif char == '*' and inside_comment:
                lookahead = self.input_code[i] if i < len(self.input_code) else None
                if lookahead == '\\':
                    inside_comment = False
                    i += 1
                    continue
            if inside_comment:
                continue

            if char.isspace():
                self.add_current_token(current_token)
                current_token = ''
                continue

            if re.match(self.delimiter_pattern, char):
                self.add_current_token(current_token)
                current_token = ''
                self.tokens.append(('DelimiterToken', char))
                continue

            if re.match(self.operator_pattern, char):
                next_char = self.input_code[i] if i < len(self.input_code) else None
                double_char_operator = char + next_char if next_char and char + next_char in ('++','<=','>=','==','!=') else None
                if double_char_operator:
                    self.add_current_token(current_token)
                    current_token = ''
                    self.tokens.append(('OperatorToken', double_char_operator))
                    i += 1
                else:
                    self.add_current_token(current_token)
                    current_token = ''
                    self.tokens.append(('OperatorToken', char))
                continue

            if char.isdigit():
                if current_token and self.is_valid_identifier(current_token + char):
                    current_token += char
                    continue
                else:
                    self.add_current_token(current_token)
                    current_token = ''
                    number = char
                    while i < len(self.input_code):
                        lookahead = self.input_code[i]
                        if lookahead.isdigit() or (lookahead == '.' and '.' not in number):
                            number += lookahead
                            i += 1
                        else:
                            break
                    self.add_current_token(number)
                    continue

            elif char == '"':
                self.add_current_token(current_token)
                current_token = ''
                string_constant = ''
                while True:
                    try:
                        char = self.input_code[i]
                        i += 1
                        if char == '"':
                            break
                        string_constant += char
                    except IndexError:
                        self.handle_error()
                        return self
                self.tokens.append(('StringConstantToken', string_constant))
                continue

            if self.is_valid_identifier(current_token + char):
                current_token += char
            else:
                self.add_current_token(current_token)
                current_token = char

        self.add_current_token(current_token)
        return self

def read_input_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_output_to_file(file_path, output):
    with open(file_path, 'w') as file:
        file.write(output)

input_file = 'input.txt'
output_file = 'output.txt'

input_code = read_input_from_file(input_file)
lexer = Lexer(input_code)
tokens = lexer.tokenize()

if lexer.error_occurred:
    write_output_to_file(output_file, "error")
else:
    output = '\n'.join([f"{token[0]}: {token[1]}" for token in lexer.tokens])
    write_output_to_file(output_file, output)
