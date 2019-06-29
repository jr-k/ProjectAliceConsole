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
import re
from terminaltables import AsciiTable, DoubleTable

from console.Command import Command
from console.input.InputArgument import InputArgument
from console.input.InputOption import InputOption

#
# ModuleGenerateCommand generates an empty module based on a hardcoded template
#
# Here are some examples, you can use InputArgument (just word separated by space) or InputOption (key-value)
# You can mix Argument with Option but in this way (Arguments first, then Options)

# InputArgument(name='moduleName', mode=InputArgument.REQUIRED, description='Name for the module you\'re creating'),
# InputOption(name='--githubUsername', 	shortcut='-u', mode=InputOption.VALUE_REQUIRED, description='Your GitHub username'),
# InputOption(name='--moduleName', 		shortcut='-n', mode=InputOption.VALUE_REQUIRED, description='Name for the module you\'re creating'),
# InputOption(name='--moduleDescription', shortcut='-d', mode=InputOption.VALUE_OPTIONAL, description='Description for that module'),
#
# Options shortcuts '-h(help) -v(verbose) -V(Version) -n(no-interaction)' are prohibited
#
class ModuleGenerateCommand(Command):

	def create(self):
		self.setName('module:generate')
		self.setDescription('Generate an Alice module')
		self.setDefinition([
			InputOption(name='--githubUsername', 	shortcut='-u', mode=InputOption.VALUE_REQUIRED, description='Your GitHub username'),
			InputOption(name='--moduleName', 		shortcut='-m', mode=InputOption.VALUE_REQUIRED, description='Name for the module you\'re creating'),
			InputOption(name='--moduleDescription', shortcut='-d', mode=InputOption.VALUE_REQUIRED, description='Description for that module')
		])
		self.setHelp('<fg:yellow> - The command %command.name% generates an empty module based on a hardcoded template.<fg:reset>\n '
			 ' Example:\n\t%command.full_name% --githubUsername="jr-k" --moduleName="Timer" -d "Alice sets a timer with customizable duration"\n\n'
		)

	def interact(self, input):
		TABLE_DATA = [['Alice Module Generator']]
		table_instance = DoubleTable(TABLE_DATA)
		table_instance.justify_columns[2] = 'right'
		self.write('\n' + table_instance.table + '\n', 'yellow')

		self.write("""Welcome in this basic module generator tool. All modules shared by the official Project Alice repository must have english!
You can now start creating your module. Remember to edit the dialogTemplate/en.json and remove dummy data!""")

		fields = []
		fieldTypeAvailable = ['en', 'fr', 'de', 'it', 'es', 'ru', 'jp', 'kr']
		_loop = True

		while _loop:
			entity = self.ask('\nEntity name : ', fgColor='yellow')

			if entity == 'exit' or entity == 'quit' or entity == '!q':
				_loop = False
				sys.exit(0)
			_loop = False


		fieldList = ''

		for fieldItem in fieldTypeAvailable:
			fieldList += fieldItem + ', '

		fieldList = fieldList[0:len(fieldList)- 1]

		TABLE_DATA = [['Available languages']]
		table_instance = AsciiTable(TABLE_DATA)
		table_instance.justify_columns[2] = 'right'
		self.write('\n' + table_instance.table + '\n', 'yellow')

		self.write(fieldList)

		while True:
			field = self.ask('\nNew language name (press <return> to stop adding fields): ', fgColor='yellow')

			reg = re.compile(r'^([a-zA-Z0-9_]+)$')
			match = reg.match(field)

			if len(field) == 0:
				break
			elif match.group(0) == None or len(match.group(0)) <= 0:
				self.write('  The language name contains invalid characters.')
				continue
			else:
				while True:
					type = self.askCombo('Dummy type <fg:reset>[en]<fg:yellow>: ', 'en', fieldTypeAvailable, fgColor='yellow')
					fields.append({"name": field, "type": type})
					break


		print(fields)

		return 0


	def execute(self, input):
		print(input.getOption("githubUsername"))
		print(input.getOption("moduleName"))
		print(input.getOption("moduleDescription"))
		self.nl()
		sys.exit(0)