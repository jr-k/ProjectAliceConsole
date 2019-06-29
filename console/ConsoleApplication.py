# -*- coding: utf-8 -*-

###
 # This file is part of the AliceConsole package.
 #
 # (c) Jierka <https://github.com/jr-k>
 #
 # For the full copyright and license information, please view the LICENSE
 # file that was distributed with this source code.
###

import sys
import traceback
from colorama import init
from colorama import Fore, Back, Style
init()

from console.input.ArgvInput import ArgvInput
from console.input.ArrayInput import ArrayInput
from console.command.HelpCommand import HelpCommand
from console.command.ListCommand import ListCommand
from console.input.InputArgument import InputArgument
from console.input.InputDefinition import InputDefinition
from console.input.InputOption import InputOption

#
# ConsoleApplication
#
class ConsoleApplication:


	def __init__(self, name, version):
		self.name = name
		self.version = version
		self.verbose = 0
		self.commands = {}
		self.running = None
		self.needHelp = False
		self.definition = self.getDefaultInputDefinition()

		for command in self.getDefaultCommands():
			self.add(command)

	def getDefinition(self):
		return self.definition

	def getDefaultInputDefinition(self):
		return InputDefinition([
			InputArgument(name='command', mode=InputArgument.REQUIRED, description='The command to execute'),
			InputOption(name='--help',      	shortcut='-h', mode=InputOption.VALUE_NONE, description='Display this help message.'),
			InputOption(name='--verbose',       shortcut='-v', mode=InputOption.VALUE_NONE, description='Increase the verbosity of messages'),
			InputOption(name='--version',       shortcut='-V', mode=InputOption.VALUE_NONE, description='Display this application version.'),
			InputOption(name='--no-interaction',shortcut='-n', mode=InputOption.VALUE_NONE, description='Do not ask any interactive question.')
		])

	def getDefaultCommands(self):
		return [ListCommand(), HelpCommand()]

	def getCommands(self):
		return self.commands

	def add(self, command):
		command.setApplication(self)

		if not command.isEnabled():
			command.setApplication(None)
			return

		if command.getDefinition() is None:
			raise ValueError('Command class {} is not correctly initialized. You probably forgot to call the parent constructor.'.format(str(command.__class__.__name__)))

		self.commands[command.getName()] = command

		return command

	def addCommands(self, commands):
		for command in commands:
			self.add(command)

	def has(self, name):
		return name in self.commands

	def setVerbose(self, level):
		self.verbose = level

	def getCommandName(self, input):
		return input.getFirstArgument()

	def getName(self):
		return self.name

	def getVersion(self):
		return self.version

	def setName(self, name):
		self.name = name

		return self

	def setVersion(self, version):
		self.version = version

		return self

	def getLongVersion(self):
		versionMessage = 'AliceConsole'

		if self.getName() is not None:
			versionMessage = self.getName()

		if self.getVersion() is not None:
			versionMessage +=' version ' + str(self.getVersion())

		return versionMessage

	def run(self, input = None):
		if input is None:
			input = ArgvInput()

		self.configureIO(input)
		exitCode = -1

		try:
			exitCode = self.doRun(input)
		except ValueError as ve:
			exitCode = 400
			print(Fore.YELLOW + '[Error]' + Fore.RESET + ' Error with code {}'.format(exitCode))
			print(Fore.YELLOW + '[Error]' + Fore.RESET + ' Message {}'.format(str(ve)))

			if self.verbose > 0:
				print(traceback.format_exc())
				sys.exit(exitCode)
			else:
				sys.exit(exitCode)

		except Exception as e:
			exitCode = 500
			print(Fore.RED + '[Exception]' + Fore.RESET + ' Error with code {}'.format(exitCode))
			print(Fore.RED + '[Exception]' + Fore.RESET + ' Message {}'.format(str(e)))
			# print('\n Message: ' + str(self.running.getSynopsis()))

			if self.verbose > 0:
				print(traceback.format_exc())
				sys.exit(exitCode)
			else:
				sys.exit(exitCode)

		# return exitCode

	def configureIO(self, input):
		if input.hasParameterOption(['--no-interaction', '-n']):
			input.setInteractive(False)

		if input.hasParameterOption(['--verbose', '-v']):
			self.setVerbose(1)

	def doRun(self, input):
		if input.hasParameterOption(['--version', '-V']):
			print(self.getLongVersion())
			return 0

		name = self.getCommandName(input)

		if input.hasParameterOption(['--help', '-h']):
			if name is None:
				name = 'help'
				input = ArrayInput(parameters={"command":'help'})
			else:
				self.needHelp = True

		if name is None:
			name = 'list'
			input = ArrayInput(parameters={"command":name})

		command = self.find(name)
		self.running = command
		exitCode = self.doRunCommand(command=command, input=input)
		self.running = None

		return exitCode

	def doRunCommand(self, command, input):
		return command.run(input)

	def find(self, name):
		return self.get(name)

	def get(self, name):
		if name not in self.commands or self.commands[name] is None:
			raise ValueError('The command \'{}\' does not exist.'.format(str(name)))

		command = self.commands[name]

		if self.needHelp:
			self.needHelp = False
			helpCommand = self.get('help')
			helpCommand.setCommand(command)
			return helpCommand

		return command




