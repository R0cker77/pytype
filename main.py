import urwid
import logging
import asyncio
from widgets.typing import Typing
from widgets.timer import Timer
from widgets.results import Results
from widgets.boxbutton import BoxButton
from util.textgenerator import get_text

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

palette = [('netural', '', ''),
		   ('wronginput', 'dark red',''),
		   ('rightinput', 'dark green', ''),
		   ('highlight', 'black', 'dark green')
]

# To do:
# add the ability to change timer as user please
# make defualt text if no connection is available
# save user texts
# save user records
# add theme palettes

class Main:
	def __init__(self):
		self.event_manager = asyncio.get_event_loop()

		self.timer_componenet = Timer(timer=10, align='center')
		self.typing_component = Typing(get_text())
		self.container_typing = urwid.LineBox(self.typing_component)
		self.container_timer = urwid.LineBox(self.timer_componenet)

		self.exit_button = BoxButton('Quit', on_press=self.exit_)
		self.reset_test = BoxButton('Reset')
		self.new_test = BoxButton('New Test', on_press=self._new_test)

		self.buttons_col = urwid.Columns([self.exit_button, self.reset_test, self.new_test])
		self.container_buttons_col = urwid.LineBox(self.buttons_col)


		self.main_pile = urwid.Pile([self.container_timer, self.container_typing, self.container_buttons_col])

		self.padding = urwid.Padding(self.main_pile, left=2, right=2)
		self.filler = urwid.Filler(self.padding)

		self.async_loop = urwid.AsyncioEventLoop(loop=self.event_manager)
		self.urwid_loop = urwid.MainLoop(self.filler, palette, event_loop=self.async_loop)
		
		urwid.connect_signal(self.typing_component, 'change', self.type_checking)


	def type_checking(self, _, string_typed):
		typing_status = self.typing_component.check_input(string_typed)
		if(typing_status == True):
			self.reset_test.set_signal(self._reset_test)
			self.timer_task = asyncio.create_task(self.timer_componenet.start_timer())
			self.event_manager.create_task(self.timer_done())

		elif(typing_status == False):
			self.test_done()


	async def timer_done(self):
		await self.timer_task

		self.test_done()

	def _reset_test(self, *user_args):
		urwid.disconnect_signal(self.typing_component, 'change', self.type_checking)
		
		self.timer_task.cancel()
		self.timer_componenet.reset_timer()
		self.typing_component.reset_test()

		urwid.connect_signal(self.typing_component, 'change', self.type_checking)


	def _new_test(self, user_args):
		# Avoiding the exception isnt the best way..

		urwid.disconnect_signal(self.typing_component, 'change', self.type_checking)
		try:
			self.timer_task.cancel()
		except AttributeError:
			pass

		self.timer_componenet.reset_timer()
		self.typing_component.new_test(get_text())
		
		urwid.connect_signal(self.typing_component, 'change', self.type_checking)


	def test_done(self):
		self.timer_task.cancel()
		self.time = self.timer_componenet.cancel_timer()

		self.buttons_col.widget_list = [self.exit_button]

		self.results_widget = urwid.Padding(Results(self.typing_component.get_results(), self.time), left=2, right=2)
		self.container_results = urwid.LineBox(self.results_widget)

		self.main_pile.widget_list = [self.container_results,
									      self.container_buttons_col]

	def exit_(self, *user_args):
		raise urwid.ExitMainLoop()


if __name__ == "__main__":
	Main().urwid_loop.run()