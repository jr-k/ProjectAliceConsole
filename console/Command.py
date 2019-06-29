# -*- coding: utf-8 -*-

###
 # This file is part of the AliceConsole package.
 #
 # (c) Jierka <https://github.com/jr-k>
 #
 # For the full copyright and license information, please view the LICENSE
 # file that was distributed with this source code.
###

import os
import sys
import re
import getpass
from prompt_toolkit import prompt
from colorama import Fore, Back, Style

from console.input.InputArgument import InputArgument
from console.input.InputDefinition import InputDefinition
from console.input.InputOption import InputOption
from console.Tools import indexOf

REGEX_COLOR = re.compile(r'<(fg|bg):([a-z]+)>')

#
# Command provides an architecture for bundle's commands
#
class Command:

	BLACK = 'black'
	RED = 'red'
	GREEN = 'green'
	YELLOW = 'yellow'
	BLUE = 'blue'
	MAGENTA = 'magenta'
	CYAN = 'cyan'
	WHITE = 'white'
	RESET = 'reset'

	def __init__(self, name = ''):
		self.synopsis = None
		self.application = None
		self.aliases = []
		self.description = 'No description'
		self.definition = None
		self.help = 'No help'
		self.applicationDefinitionMerged = False
		self.applicationDefinitionMergedWithArgs = False
		self.ignoreValidationErrors = False
		self.definition = InputDefinition()
		self.chars = {}

		if name:
			self.setName(name)

		try:
			self.create()
		except AttributeError:
			raise ValueError('Command \'{}\' does not override create method'.format(str(self.name)))

		if not self.name:
			raise ValueError('The command name cannot be empty')

	def execute(self, input):
		raise ValueError('You must override the execute() method in the concrete command class.')

	def setContainer(self, container):
		self.container = container

		return self

	def getContainer(self):
		return self.container

	def setApplication(self, application):
		self.application = application

		return self

	def getApplication(self):
		return self.application

	def setName(self, name):
		self.validateName(name)
		self.name = name

		return self

	def setDescription(self, description):
		self.description = description

		return self

	def setHelp(self, help):
		self.help = help

		return self

	def getName(self):
		return self.name

	def getHelp(self):
		return self.help

	def getDefinition(self):
		return self.definition

	def getDescription(self):
		return self.description

	def getAliases(self):
		return self.aliases

	def ignoreValidationErrors(self):
		self.ignoreValidationErrors = True

	def isEnabled(self):
		return True

	def getArrayChars(self):
		if len(self.chars) != 0:
			return self.chars

		self.chars = { 'top': '═' , 'top-mid': '╤' , 'top-left': '╔' , 'top-right': '╗'
		, 'bottom': '═' , 'bottom-mid': '╧' , 'bottom-left': '╚' , 'bottom-right': '╝'
		, 'left': '║', 'left-mid': '╟' , 'mid': '─' , 'mid-mid': '┼'
		, 'right': '║' , 'right-mid': '╢' , 'middle': '│' }

		return self.chars

	def setArrayChars(self, chars):
		self.chars = chars

	def getProcessedHelp(self):
		name = self.name
		executeCommand = '{} {}'.format(sys.argv[0], os.path.basename(sys.argv[1]))

		replaced = self.getHelp()
		reg = re.compile(r'%command.name%')
		replaced = re.sub(reg, name, replaced)
		reg2 = re.compile(r'%command.full_name%')
		replaced = re.sub(reg2, '{} {}'.format(executeCommand, name), replaced)

		return replaced

	def setSynopsis(self, synopsis):
		if self.synopsis is None:
			self.synopsis = '{} {}'.format(self.name, synopsis)

		return self

	def run(self, inputInstance):
		self.getSynopsis()
		self.mergeApplicationDefinition()

		try:
			inputInstance.bind(self.definition)
		except ValueError as e:
			if not self.ignoreValidationErrors:
				raise ValueError(e)

		hasInteract = True

		try:
			self.interact(inputInstance)
		except AttributeError:
			hasInteract = False

		inputInstance.validate()

		return self.execute(inputInstance)

	def addOption(self, name, shortcut, mode, description, definition):
		self.definition.addOption(InputOption(name, shortcut, mode, description, definition))
		return self

	def addArgument(self, name, mode, description, definition):
		self.definition.addArgument(InputArgument(name, mode, description, definition))
		return self

	def validateName(self, name):
		reg = re.compile(r'^[^\:]+(\:[^\:]+)*$')

		if name is None or not reg.match(name):
			raise ValueError('Command name \'{}\' is invalid.'.format(str(name)))

	def getSynopsis(self):
		if self.synopsis is None:
			self.synopsis = self.name

			if self.definition:
				self.synopsis += ' ' + str(self.definition.getSynopsis())
			else:
				self.synopsis += ' [no arguments|no options]'

		return self.synopsis

	def setDefinition(self, definition = None):

		if definition is None:
			self.definition.setDefinition(definition)
		elif definition.__class__.__name__ == 'InputDefinition':
			self.definition = definition
		else:
			self.definition.setDefinition(definition)

		self.applicationDefinitionMerged = False

	def mergeApplicationDefinition(self, mergeArgs = None):
		if mergeArgs is None:
			mergeArgs = True

		if self.application is None or (self.applicationDefinitionMerged is True and (self.applicationDefinitionMergedWithArgs or not mergeArgs)):
			return

		if mergeArgs:
			currentArguments = self.definition.getArguments()
			self.definition.setArguments(self.application.getDefinition().getArguments())
			self.definition.addArguments(currentArguments)

		self.definition.addOptions(self.application.getDefinition().getOptions())
		self.applicationDefinitionMerged = True

		if mergeArgs:
			self.applicationDefinitionMergedWithArgs = True

	def ask(self, question = '', definition = None, hidden = False, fgColor='reset', bgColor='reset'):
		inputValue = ''

		try:
			questionStyled = self.stringToColored(question, fgColor, bgColor)

			if hidden:
				inputValue = getpass.getpass(questionStyled)
			else:
				inputValue = input(questionStyled)
		except KeyboardInterrupt:
			sys.exit(0)

		if definition:
			if inputValue == '':
				return definition

		return inputValue

	def askCombo(self, question, definition, choices, caseSensitive = False, fgColor='reset', bgColor='reset'):
		while True:
			inputValue = self.ask(question, definition, fgColor=fgColor, bgColor=bgColor)

			if indexOf(inputValue, choices) < 0:
				continue

			if not caseSensitive:
				inputValue = inputValue.lower()

			break

		return inputValue

	def askHidden(self, question, definition, fgColor='reset', bgColor='reset'):
		return self.askAndValidate(question=question, definition=definition, fgColor=fgColor, bgColor=bgColor)

	def askAndValidate(self, question = '', definition = None, callback = None, hidden = False, fgColor='reset', bgColor='reset'):
		inputValue = self.ask(question, definition, hidden, fgColor, bgColor)

		if inputValue == '' and definition:
			inputValue = definition

		if callback:
			return callback(inputValue)
		else:
			return inputValue

	def askHiddenAndValidate(self, question, definition, callback, fgColor='reset', bgColor='reset'):
		return self.askAndValidate(question, definition, callback, True, fgColor, bgColor)

	def askConfirmation(self, question, definition, caseSensitive = False, fgColor='reset', bgColor='reset'):
		return self.askCombo(question, definition,['y', 'n', 'yes', 'no'], caseSensitive, fgColor, bgColor)

	def _getForegroundColor(self, color = 'reset'):
		if color == 'black': return Fore.BLACK
		if color == 'red': return Fore.RED
		if color == 'green': return Fore.GREEN
		if color == 'yellow': return Fore.YELLOW
		if color == 'blue': return Fore.BLUE
		if color == 'magenta': return Fore.MAGENTA
		if color == 'cyan': return Fore.CYAN
		if color == 'white': return Fore.WHITE
		return Fore.RESET

	def _getBackgroundColor(self, color = 'reset'):
		if color == 'black': return Back.BLACK
		if color == 'red': return Back.RED
		if color == 'green': return Back.GREEN
		if color == 'yellow': return Back.YELLOW
		if color == 'blue': return Back.BLUE
		if color == 'magenta': return Back.MAGENTA
		if color == 'cyan': return Back.CYAN
		if color == 'white': return Back.WHITE
		return Back.RESET

	def stringToColored(self, string, fgColor='reset', bgColor='reset'):
		fgColor = self._getForegroundColor(color=fgColor)
		bgColor = self._getBackgroundColor(color=bgColor)

		colorsPairs = REGEX_COLOR.findall(string)

		for colorPair in colorsPairs:
			(type, color) = colorPair
			string = string.replace('<{}:{}>'.format(type, color), self._getBackgroundColor(color) if type == 'bg' else self._getForegroundColor(color))

		return bgColor + fgColor + string + Fore.RESET + Back.RESET

	def write(self, data, fgColor='reset', bgColor='reset'):
		print(self.stringToColored(data, fgColor, bgColor))

	def nl(self):
		print('')


