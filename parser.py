import plex

class ParseError(Exception):
	pass

class MyParser:
	
	def __init__(self):
		letter = plex.Range('azAZ')
		digit = plex.Range('01')
		num = plex.Range('09')
		name = letter + plex.Rep(letter|num)
		space = plex.Any(' \n\t')
		Keyword = plex.Str('print','PRINT')
		bin = plex.Rep1(digit)
		ando = plex.Str('and')
		oro = plex.Str('or')
		xoro = plex.Str('xor')
		equals = plex.Str('=')
		
		parethensys1 = plex.Str('(')
		parethensys2 = plex.Str(')')
		
		self.st = {}

		self.lexicon = plex.Lexicon([   
			(Keyword, 'PRINT_TOKEN'),
			(ando, plex.TEXT),
			(oro, plex.TEXT),
			(xoro, plex.TEXT),
			(name, 'ID_TOKEN'),             #name = letter + plex.Rep(letter|digit)
	        (bin, 'BIN_NUM'),
	        (equals, '='),
			(parethensys1, '('),
			(parethensys2, ')'),
			(space, plex.IGNORE)			
		])
			
	def createScanner(self,fp):
		self.scanner = plex.Scanner(self.lexicon,fp)
		self.la , self.text = self.next_token()

	def next_token(self):
		return self.scanner.read()
	
	def match(self,token):
		if self.la == token:
			self.la, self.text=self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
			
	def parse(self,fp):
		self.createScanner(fp)
		self.stmt_list()
		
	def stmt_list(self):
		if self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN':
			self.stmt()
			self.stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError("Expected id or print")
			
	def stmt(self):
		if self.la == 'ID_TOKEN':
			varname = self.text
			self.match('ID_TOKEN')
			self.match('=')
			e = self.expr()
			self.st[varname] = e
		elif self.la == 'PRINT_TOKEN':
			self.match('PRINT_TOKEN')
			self.expr()
		else:
			raise ParseError("Expected id or print")
			
	def expr(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BIN_NUM':
			self.term()
			self.term_tail()
		elif self.la == ')' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN':
			return self.term()
		else:
			raise ParseError("Expected ( or id or num or )")
			
	def term_tail(self):
		if self.la == 'xor':		
			self.match('xor')
			self.term()
			self.term_tail()
		elif self.la == ')' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
			return
		else:
			raise ParseError("Expected xor ") 
			
	def term(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BIN_NUM':		
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("Expected ( or num or )") 

	def factor_tail(self):
		if self.la == 'or':
			self.match('or')
			self.factor()
			self.factor_tail()
		elif self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError("Expected or") 

	def factor(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BIN_NUM':
			self.atom()
			self.atom_tail()
		else:
			raise ParseError("Expecting ( or id or num.")
		
	def atom_tail(self):
		if self.la == 'and':
			self.match('and')
			self.atom()
			self.atom_tail()
		elif self.la == ')' or self.la == 'or' or self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
			return
		else:
			raise ParseError("Expected and")		
		
	def atom(self):
		if self.la == '(':
			self.match('(')
			self.expr()
			self.match(')')
			return self.expr()
		elif self.la == 'ID_TOKEN':
			varname = self.text
			self.match('ID_TOKEN')
			if varname in self.st:
				return self.st[varname]
		elif self.la == 'BIN_NUM':
			self.text
			self.match('BIN_NUM')
			return self.text
		else:
			raise ParseError("Expected id or num or (")
			
parser = MyParser()

with open('inp.txt', 'r') as fp:
	parser.parse(fp)
