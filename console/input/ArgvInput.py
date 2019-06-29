# -*- coding: utf-8 -*-

###
 # This file is part of the AliceConsole package.
 #
 # (c) Jierka <https://github.com/jr-k>
 #
 # For the full copyright and license information, please view the LICENSE
 # file that was distributed with this source code.
###

import re
import sys

from console.input.Input import Input
from console.Tools import indexOf

#
# ArgvInput is a set of inputs as a argv command line
#
class ArgvInput(Input):


	def __init__(self, argv = None, definition = None, command = None, standalone = False):
		self.tokens = None
		self.parsed = None
		self.standalone = standalone

		if not argv:
			argv = sys.argv[1:]

		# Unshift the command name:
		# if len(argv) != 0:
		# 	argv.pop(0)

		self.tokens = argv

		super(ArgvInput, self).__init__(definition=definition)

	def setTokens(self, tokens):
		self.tokens = tokens

	def parse(self):
		parseOptions = True
		self.parsed = self.tokens.copy()

		token = None

		if len(self.parsed) != 0:
			token = self.parsed.pop(0)

		while token is not None:
			if parseOptions and token == '':
				self.parseArgument(token)
			elif parseOptions and token == '--':
				parseOptions = False
			elif parseOptions and indexOf('--', token) == 0:
				self.parseLongOption(token)
			elif parseOptions and '-' == token[0] and '-' != token:
				self.parseShortOption(token)
			else:
				self.parseArgument(token)

			try:
				token = self.parsed.pop(0)
			except:
				break

	def parseShortOption(self, token):
		name = token[1:]

		if len(name) > 1:
			if self.definition.hasShortcut(name[0]) and self.definition.getOptionForShortcut(name[0]).acceptValue():
				self.addShortOption(name[0], name[1:])
			else:
				self.parseShortOptionSet(name)
				
		else:
			self.addShortOption(name, None)

	def parseShortOptionSet(self, name):
		length = len(name)

		for i in range(0, length):
			if not self.definition.hasShortcut(name[i]):
				raise ValueError('The -{} option does not exist.'.format(str(name[i])))

			option = self.definition.getOptionForShortcut(name[i])

			if option.acceptValue():
				self.addLongOption(option.getName(), None if i == length - 1 else name[i+1:])
				break
			else:
				self.addLongOption(option.getName(), None)

	def parseLongOption(self, token):
		name = token[2:]
		pos = indexOf('=', name)

		if pos >= 0:
			self.addLongOption( name[0:pos], name[pos+1:])
		else:
			self.addLongOption(name, None)

	def parseArgument(self, token):
		c = len(self.arguments)

		if self.definition.hasArgument(c):
			arg = self.definition.getArgument(c)

			if arg.isArray():
				self.arguments[arg.getName()] = [token]
			else:
				self.arguments[arg.getName()] = token

		elif self.definition.hasArgument(c - 1) and self.definition.getArgument(c - 1).isArray():
			arg = self.definition.getArgument(c - 1)

			if arg.getName() not in self.arguments or self.arguments[arg.getName()] is None:
				self.arguments[arg.getName()] = []

			self.arguments[arg.getName()].append(token)
		else:
			if not self.standalone:
				raise ValueError('Too many arguments.')

	def addShortOption(self, shortcut, value):

		if not self.definition.hasShortcut(shortcut):
			raise ValueError('The -{} option does not exist.'.format(str(shortcut)))

		self.addLongOption(self.definition.getOptionForShortcut(shortcut).getName(), value)

	def addLongOption(self, name, value):

		if not self.definition.hasOption(name):
			raise ValueError('The --{} option does not exist.'.format(str(name)))

		option = self.definition.getOption(name)

		if value is not None and not option.acceptValue():
			raise ValueError('The --{} option does not accept a value : {}'.format(str(name),str(value)))


		if value is None and option.acceptValue() and len(self.parsed):
			next = None

			if len(self.parsed) != 0:
				next = self.parsed.pop(0)

			if next[0] is not None and '-' != next[0]:
				value = next
			elif next == '':
				value = ''
			else:
				self.parsed.insert(0, next)

		if value is None:
			if option.isValueRequired():
				raise ValueError('The --{} option requires a value.'.format(str(name)))

			if not option.isArray():
				if option.isValueOptional():
					value = option.getDefault()
				else:
					value = True

		if option.isArray():
			if name not in self.options or self.options[name] is None:
				self.options[name] = []

			self.options[name].append(value)
		else:
			self.options[name] = value

	def getFirstArgument(self):
		for token in self.tokens:
			if '-' == token[0]:
				continue

			return token

	def hasParameterOption(self, values):

		for token in self.tokens:
			for value in values:
				if token == value or 0 == indexOf(value+'=', token):
					return True

		return False

	def getParameterOption(self, values, definition):

		tokens = self.tokens.copy()
		token = None

		if len(tokens) != 0:
			token = tokens.pop(0)

		while token:
			for value in values:
				if token == value or 0 == indexOf(value+'=', token):
					pos = indexOf('=', token)

					if False != pos:
						return token[pos+1:]

			# weird
			# if len(tokens) != 0:
			# 	token = tokens.pop(0)

			return tokens.pop(0)

		return definition

	def __str__(self):
		tokens = []

		for token in self.tokens:

			reg = re.compile(r'^(-[^=]+=)(.+)')
			match = reg.match(token)

			if match:
				return match[1] + self.escapeToken(match[2])

			if token and token[0] != '-':
				return self.escapeToken(token)

			tokens.append(token)

		return ' '.join(tokens)


