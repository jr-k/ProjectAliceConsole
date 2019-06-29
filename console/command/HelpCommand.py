# -*- coding: utf-8 -*-

###
 # This file is part of the AliceConsole package.
 #
 # (c) Jierka <https://github.com/jr-k>
 #
 # For the full copyright and license information, please view the LICENSE
 # file that was distributed with this source code.
###

from console.Command import Command
from console.input.InputArgument import InputArgument
from console.input.InputOption import InputOption

#
# HelpCommand provides help for a given command
#
class HelpCommand(Command):

	def create(self):
		self.setName('help')
		self.setDescription('Displays help for a command')
		self.setDefinition([InputArgument(name='command_name', mode=InputArgument.OPTIONAL, description='The command name', default='help')])
		self.setHelp('> The %command.name% command displays help for a given command:\n  %command.full_name% list\n\n  To display the list of available commands, please use the list command.')

	def setCommand(self, command):
		self.command = command

		return self

	def execute(self, input):
		if self.command is None:
			self.command = self.getApplication().find(input.getArgument('command_name'))

		self.nl()
		self.write(self.command.getProcessedHelp())
		self.command = None


