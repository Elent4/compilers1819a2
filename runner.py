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
			return {'type' : '=', 'text' : varname, 'expr' : e}
		elif self.la == 'PRINT_TOKEN':
			self.match('PRINT_TOKEN')
			e = self.expr()
			print('={:b}' .format(e))
			return {'type' : 'print', 'expr' : e}
		else:
			raise ParseError("Expected id or print")
			
	def expr(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BIN_NUM':
			t = self.term()
			while self.la == 'xor':
				self.match('xor')
				t2 = self.term()
				print ('{:b} xor {:b}' .format(t,t2))
				t = t^t2
			if self.la == ')' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
				return t
			raise ParseError("Expected xor ")
		else:
			raise ParseError("Expected ( or id or num or )")
			
	def term(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BIN_NUM':		
			w = self.factor()
			while self.la == 'or':
				self.match('or')
				w2 = self.factor()
				print ('{:b} or {:b}' .format(w,w2))
				w = w|w2 
			if self.la == ')' or self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
				return w
			raise ParseError("Expected or ")
		else:
			raise ParseError("Expected ( or id or )") 

	def factor(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BIN_NUM':
			a = self.atom()
			while self.la == 'and':
				self.match('and')
				a2 = self.atom()
				print ('{:b} and {:b}' .format(a,a2))
				a = a&a2 
			if self.la == ')' or self.la == 'or' or self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
				return a
			raise ParseError("Expected and ")
		else:
			raise ParseError("Expecting ( or id or num.")
		
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
			bnum = int(self.text,2)
			self.match('BIN_NUM')
			return (bnum)
		else:
			raise ParseError("Expected id or num or (")
			
parser = MyParser()

with open('inr.txt', 'r') as fp:
	parser.parse(fp)
