# -*- coding: utf-8 -*-

###
 # This file is part of the AliceConsole package.
 #
 # (c) Jierka <https://github.com/jr-k>
 #
 # For the full copyright and license information, please view the LICENSE
 # file that was distributed with this source code.
###

from terminaltables import DoubleTable

from console.Command import Command
from console.input.InputArgument import InputArgument
from console.input.InputOption import InputOption

#
# ListCommand lists all commands
#
class ListCommand(Command):

	def create(self):
		self.setName('list')
		self.setDescription('List all commands')
		self.setDefinition()
		self.setHelp('> The %command.name% command lists all commands:\n  %command.full_name%')

	def execute(self, input):
		commands = self.getApplication().getCommands()
		sortedCommandKeys = sorted(commands)

		self.nl()
		self.write('Options :')
		TABLE_DATA = [['Option', 'Description'],]
		table_instance = DoubleTable(TABLE_DATA)
		table_instance.justify_columns[2] = 'right'

		for k,option in self.getApplication().getDefaultInputDefinition().getOptions().items():
			TABLE_DATA.append(['--{} [{}]'.format(option.getName(), option.getShortcut()), option.getDescription()])

		self.write(table_instance.table)

		self.nl()
		self.write('Commands :')
		TABLE_DATA = [['Command name', 'Description']]
		table_instance = DoubleTable(TABLE_DATA)
		table_instance.justify_columns[2] = 'right'

		limit = 55

		for name in sortedCommandKeys:
			command = commands[name]

			if len(command.getDescription()) > limit:
				desc = '{}...'.format(command.getDescription()[0:limit])
			else:
				desc = command.getDescription()
			TABLE_DATA.append([name,desc])

		self.write(table_instance.table)



