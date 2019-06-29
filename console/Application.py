# -*- coding: utf-8 -*-

###
 # This file is part of the AliceConsole package.
 #
 # (c) Jierka <https://github.com/jr-k>
 #
 # For the full copyright and license information, please view the LICENSE
 # file that was distributed with this source code.
###

from console.ConsoleApplication import ConsoleApplication

#
# Application is the main entry point of a ConsoleApplication
#
class Application(ConsoleApplication):


	def __init__(self):
		self.commandsRegistered = False
		super(Application, self).__init__('AliceConsole', 1)


	def run(self, input = None):
		self.container = {}

		if not self.commandsRegistered:
			self.registerCommands()
			self.commandsRegistered = True

		for k,command in self.commands.items():
			command.setContainer(self.container)

		return super(Application, self).run(input)

	def registerCommands(self):
		from console.command.ModuleGenerateCommand import ModuleGenerateCommand
		self.add(ModuleGenerateCommand())
		return True
		# bundles = self.container.get('Application').getBundles()
		#
		# for bundleName,bundle in bundles.items():
		# 	if bundle instanceof Bundle:
		# 		bundle.registerCommands(self)


