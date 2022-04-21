from add_arrows_to_string import add_arrows_to_string_func

#### ERRORS SECTION ####
class Error:
	def __init__(self, pos_start, pos_end, error_name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details
	
	def as_string(self):
		result  = f'{self.error_name}: {self.details}\n'
		result += f'File {self.pos_start.fileName}, line {self.pos_start.lineNum + 1}'
		result += '\n\n' + add_arrows_to_string_func(self.pos_start.fileText, self.pos_start, self.pos_end)
		return result

class IllegalCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


#### POSITION SECTION ####
class Position:
	def __init__(self, index, lineNum, colNum, fileName, fileText):
		self.index = index
		self.lineNum = lineNum
		self.colNum = colNum
		self.fileName = fileName
		self.fileText = fileText
	
	def advance(self, current_character = None):
		self.index += 1
		self.colNum += 1

		if current_character == "\n":
			self.lineNum += 1
			self.colNum = 0

		return self
	
	def copy(self):
		return Position(self.index, self.lineNum, self.colNum, self.fileName, self.fileText)


#### TOKENS SECTION ####

TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN' #Left Parentheses
TT_RPAREN   = 'RPAREN' #Right Parentheses
TT_EOF		= 'EOF'
DIGITS      = '0123456789'

# Token class, Lexer makes these
class Token:
	def __init__(self, type_, value = None, pos_start = None, pos_end = None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end

	def __repr__(self):
		if self.value: return f'{self.type}:{self.value}'
		return f'{self.type}'


#### LEXER SECTION ####
class Lexer:
	def __init__(self, text, fileName):
		self.text = text
		self.pos = Position(-1, 0, -1, fileName, text)
		self.current_character = None
		self.advance()

	def advance(self):
		self.pos.advance(self.current_character)
		if(self.pos.index < len(self.text)):
			self.current_character = self.text[self.pos.index]
		else:
			self.current_character = None

	def make_tokens(self):      
		tokens = []
		while self.current_character != None:
			if self.current_character in ' \t':
				self.advance()
			elif self.current_character in DIGITS:
				tokens.append(self.make_number())
			elif self.current_character == '+':
				tokens.append(Token(TT_PLUS, pos_start = self.pos))
				self.advance()
			elif self.current_character == '-':
				tokens.append(Token(TT_MINUS, pos_start = self.pos))
				self.advance()
			elif self.current_character == '*':
				tokens.append(Token(TT_MUL, pos_start = self.pos))
				self.advance()
			elif self.current_character == '/':
				tokens.append(Token(TT_DIV, pos_start = self.pos))
				self.advance()
			elif self.current_character == '(':
				tokens.append(Token(TT_LPAREN, pos_start = self.pos))
				self.advance()
			elif self.current_character == ')':
				tokens.append(Token(TT_RPAREN, pos_start = self.pos))
				self.advance()
			else:
				pos_start = self.pos.copy()
				char = self.current_character
				self.advance()
				return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

		tokens.append(Token(TT_EOF, pos_start = self.pos))
		return tokens, None

	def make_number(self):
		num_str = ''
		dot_count = 0
		pos_start = self.pos.copy()

		while self.current_character != None and self.current_character in DIGITS + '.':
			if self.current_character == '.':
				if dot_count == 1: break
				dot_count += 1
				num_str += '.'
			else:
				num_str += self.current_character
			self.advance()

		if dot_count == 0:
			return Token(TT_INT, int(num_str), self.pos)
		else:
			return Token(TT_FLOAT, float(num_str), self.pos)


#### NODES SECTION ####
class NumberNode:
	def __init__(self, tok):
		self.tok = tok

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

#### PARSE RESULTS SECTION ####
class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
	
	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error: 
				self.error = res.error
			return res.node

		return res

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		self.error = error
		return self



#### PARSER SECTION ####
class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.token_index = -1
		self.advance()
	
	def parse(self):
		res = self.expression()
		if not res.error and self.current_token.type != TT_EOF:
			return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '+', '-', '*' or '/'"))

		return res

	def advance(self):
		self.token_index += 1
		if(self.token_index < len(self.tokens)):
			self.current_token = self.tokens[self.token_index]
		return self.current_token
	
	def factor(self):
		res = ParseResult()
		tok = self.current_token

		if tok.type in (TT_PLUS, TT_MINUS):
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error: 
				return res
			return res.success(UnaryOpNode(tok, factor))
		
		elif tok.type in (TT_INT, TT_FLOAT):
			res.register(self.advance())
			return res.success(NumberNode(tok))

		elif tok.type == TT_LPAREN:
			res.register(self.advance())
			expr = res.register(self.expression())
			if res.error: 
				return res
			if self.current_token.type == TT_RPAREN:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_token.pos_start, self.current_token.pos_end,
					"Expected ')'"
				))

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int or float"
		))

	def term(self):
		return self.binary_operation(self.factor, (TT_MUL, TT_DIV))

	def expression(self):
		return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))

	def binary_operation(self, inputFunction, ops):
		res = ParseResult()
		left = res.register(inputFunction())
		if res.error: 
			return res
		
		while self.current_token.type in ops:
			op_tok = self.current_token
			res.register(self.advance())
			right = res.register(inputFunction())
			if res.error: 
				return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)

class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'


#### RUN SECTION ####
def run(fileName, text):
	#Generate Tokens
	lexer = Lexer(text, fileName)
	tokens, error = lexer.make_tokens()
	if error:
		return None, error

	#Generate Abstract Syntax Tree
	parser = Parser(tokens)
	AbstractSyntaxTree = parser.parse()
	
	return AbstractSyntaxTree.node, AbstractSyntaxTree.error