#!/usr/bin/python
import pygame
import sys
import time
from pathlib import Path
from pygame.locals import *
import numpy as np
from wordentry import *

here = Path(__file__).parent
vocabulary = load_session(here / 'game_data' / 'vocabulary.obj')
master_session = load_session(here / 'game_data' / 'master_session.obj')

pygame.init()
fps = 30
fpsClock = pygame.time.Clock()


# Constants --------------------------------------------------------------
title_font           = pygame.font.Font(str(here / "assets" / 'GoodUnicornRegular-Rxev.ttf'), 72)
main_game_font       = pygame.font.Font(str(here / "assets" / 'Elementary_Gothic_Scaled.ttf'), 24)
session_display_font = pygame.font.Font(str(here / "assets" / 'Elementary_Gothic_Scaled.ttf'), 12)
correct_font         = pygame.font.Font(str(here / "assets" / 'Elementary_Gothic_Scaled.ttf'), 50)
meaning_font         = pygame.font.Font(str(here / "assets" / 'Helvetica-Normal.ttf'), 26)
example_font         = pygame.font.Font(str(here / "assets" / 'Helvetica-Normal.ttf'), 18)

screen_width = 1200
screen_height = 675
screen_rect = Rect(0, 0, screen_width, screen_height)

# Colors -----------------------------------------------------------------
white      = (255,255,255)
black      = (0,0,0)
yellow     = (250,250,5)
gray       = (15,15,15)
blue       = (5,5,250)
green      = (5,255,5)
khaki      = (45, 150, 5)
red        = (255,5,5)
darkred    = (150,20,5)
background = black

# Classes ----------------------------------------------------------------

class WordCard(pygame.sprite.Sprite):
	"""Sprite class for a card, with its rectangle and containing a vocab. word entry"""
	def __init__(self, entry, rect = (0.1*screen_width, 0.1*screen_height, 
			screen_width//3, 3*screen_height//5), validity = True, *groups):
		super().__init__(*groups)
		self.entry = entry
		self.rect = pygame.Rect(rect)
		#self.image = pygame.Surface(self.rect.size)
		self.validity = validity
		self.showing_example = False
		self.showing_letter = False

		self.entry.example = self.entry.example.replace(self.entry.word, 
								str('*'*len(self.entry.word)) )

	def update(self):
		pass

	def check_validity(self):
		if len(self.entry.word) > 3 and len(self.entry.meaning) > 5:
			self.validity = True
			return True
		else:
			self.validity =  False
			return False

	def calculate_layout(self):
		#n_lines = 20*len(str(self.entry.meaning + self.entry.example))//self.rect.w
		#chars_per_line = len(self.entry.meaning)//n_lines
		width_limit = 0.65*self.rect.w

		meaning_words = self.entry.meaning.split(' ')
		m_line_surfs = []
		current_line = ''
		current_width = 0
		for word in meaning_words:
			word_surf = meaning_font.render(word, True, white)
			current_width += word_surf.get_width()
			if current_width < width_limit:
				current_line += str(word + ' ')
			else:
				m_line_surfs.append(meaning_font.render(current_line.rstrip(), True, white))
				current_width = 0
				current_line = word + ' '
		m_line_surfs.append(meaning_font.render(current_line.rstrip(), True, white))

		example_words = self.entry.example.split(' ')
		ex_line_surfs = []
		current_line = ''
		current_width = 0
		for word in example_words:
			word_surf = example_font.render(word, True, white)
			current_width += word_surf.get_width()
			if current_width < width_limit:
				current_line += str(word + ' ')
			else:
				ex_line_surfs.append(example_font.render(current_line.rstrip(), True, white))
				current_width = 0
				current_line = word + ' '
		ex_line_surfs.append(example_font.render(current_line.rstrip(), True, white))

		return {'meaning':m_line_surfs, 'example':ex_line_surfs}

	def draw(self, surface):
		"""Draw lines indicating letters and meaning underneath"""

		#self.image.fill(black)
		surface.fill(black, self.rect)

		# Letter tiles
		tiles = str('_ '*len(self.entry.word))
		tiles_surf = main_game_font.render(tiles, True, white)
		surface.blit(tiles_surf, 
			( (self.rect.x, 10), tiles_surf.get_size() ))

		if self.showing_letter:
			first_letter = main_game_font.render(self.entry.word[0], True, white)
			surface.blit(first_letter, 
				( (self.rect.x, 10), first_letter.get_size() ))


		linesurfs = self.calculate_layout()
		
		# Meaning
		y_offset = 5
		for i in range(len(linesurfs['meaning'])):

			curr_line_surf = linesurfs['meaning'][i]
			curr_line_width, curr_line_heigth = curr_line_surf.get_size()

			#self.image.blit(curr_line_surf, 
			#	(5, y_offset, curr_line_width, curr_line_heigth))

			surface.blit(curr_line_surf,
				(self.rect.x+5, self.rect.top+y_offset, curr_line_width, curr_line_heigth))
			
			y_offset += curr_line_heigth + 5

		# Example
		if self.showing_example:
			y_offset += 15
			if len(self.entry.example) > 5:
				for i in range(len(linesurfs['example'])):

					curr_line_surf = linesurfs['example'][i]
					curr_line_width, curr_line_heigth = curr_line_surf.get_size()

					surface.blit(curr_line_surf,
						(self.rect.x+5, self.rect.top+y_offset, curr_line_width, curr_line_heigth))

					y_offset += curr_line_heigth + 5
			else:
				no_example_surf = example_font.render('No example available', True, white)
				no_ex_w, no_ex_h = no_example_surf.get_size()
				surface.blit(no_example_surf,
						(self.rect.x+5, self.rect.top+y_offset, no_ex_w, no_ex_h))

		pygame.draw.rect(surface, white, self.rect, 5)
		#surface.blit(self.image, self.rect)

	def reveal(self, surface):
		"""Render the word with the letters on the tiles"""

		solution = '  '.join(list(self.entry.word))
		solution_surf = main_game_font.render(solution, True, white)

		surface.blit(solution_surf, 
			( (self.rect.x, 7), solution_surf.get_size() ))
	
class SessionDisplay(pygame.sprite.Sprite):
	"""Meant for Stack Gallery: Display session summary (card number, n_correct,
	n_wrong, color depending on completion) and expand to show individual
	WordEntries as EntryDisplay sprites when clicked"""
	def __init__(self, session, rect=(0,0,75,75), *groups):
		super().__init__(*groups)
		self.rect = pygame.Rect(rect)
		self.image = pygame.Surface(self.rect.size)
		self.session = session
		self.completed = self.session.completed
		self.expanded = False
		self.color = green if self.completed else yellow
		self.stats = {
		'total':session_display_font.render(str(len(self.session.stack)), True, black),
		'active':session_display_font.render(str(len(self.session.active_stack)), True, black),
		'known':session_display_font.render(str(len(self.session.known)), True, khaki),
		'unknown':session_display_font.render(str(len(self.session.unknown)), True, darkred)}
		
		# Create image
		self.image.fill(self.color)
		self.rel_rect = self.image.get_rect() # Relative coordinates of image
		self.image.blit(self.stats['total'], self.rel_rect.topleft)
		self.image.blit(self.stats['active'], self.rel_rect.midtop)
		self.image.blit(self.stats['known'], self.rel_rect.midleft)
		self.image.blit(self.stats['unknown'], self.rel_rect.center)
		
		
	def update(self, event, surface):
		if event.type == MOUSEBUTTONDOWN:
			if self.rect.collidepoint(event.pos):
				self.expand(surface)

	def expand(self, surface, nrows=5, ncols=5):
		page = 1
		new_page = {1:2, 2:1}
		margin = 10
		y_grid = [(1.25*screen_height//margin)+i*screen_height//nrows for i in range(nrows)]
		x_grid = [(screen_width//margin)+i*screen_width//nrows for i in range(nrows)]
		grid = [(x,y) for x in x_grid for y in y_grid]

		# Gather all WordEntries and instance EntryDisplays out of them
		# Divide stack in two and display one half at a time
		entry_displays_1 = pygame.sprite.RenderUpdates()
		for entry in self.session.stack[:int(len(self.session.stack)/2)]:
			entrydisp = EntryDisplay(entry)
			entry_displays_1.add(entrydisp)
		entry_displays_2 = pygame.sprite.RenderUpdates()
		for entry in self.session.stack[int(len(self.session.stack)/2):]:
			entrydisp = EntryDisplay(entry)
			entry_displays_2.add(entrydisp)

		# Assign coordinates in grid to each WordDisplay
		first_wordcards = entry_displays_1.sprites()
		for i in range(len(first_wordcards)):
			first_wordcards[i].center = grid[i]
		second_wordcards = entry_displays_2.sprites()
		for i in range(len(second_wordcards)):
			second_wordcards[i].center = grid[i]

		# Collapse button
		collapse_button = pygame.Rect(0,0,screen_height//15,screen_height//15)
		collapse_surf = pygame.Surface(collapse_button.size)
		collapse_surf.fill(yellow)
		pygame.draw.line(collapse_surf, black, (collapse_button.w//10, collapse_button.h//2),
					(9*collapse_button.w//10, collapse_button.h//2), 7)
		pygame.draw.lines(collapse_surf, black, False,
					[(collapse_button.w//2, collapse_button.h//5),
					(collapse_button.w//10, collapse_button.h//2),
					(collapse_button.w//2, 4*collapse_button.h//5)], 7)
		pygame.draw.rect(collapse_surf, black, collapse_button, 4)
		
		# Change pages button
		arrow_width = 4
		switch_button = pygame.Rect(screen_width-(screen_height//7),0,
									screen_height//7, screen_height//18)
		switch_right_surf = pygame.Surface(switch_button.size)
		switch_right_surf.fill(yellow)
		pygame.draw.line(switch_right_surf, black, (switch_button.w//10, switch_button.h//2),
					(9*switch_button.w//10, switch_button.h//2), arrow_width)
		pygame.draw.lines(switch_right_surf, black, False,
					[(switch_button.w//2, switch_button.h//5),
					(9*switch_button.w//10, switch_button.h//2),
					(switch_button.w//2, 4*switch_button.h//5)], arrow_width)
		switch_left_surf = pygame.Surface(switch_button.size)
		switch_left_surf.fill(yellow)
		pygame.draw.line(switch_left_surf, black, (switch_button.w//10, switch_button.h//2),
					(9*switch_button.w//10, switch_button.h//2), arrow_width)
		pygame.draw.lines(switch_left_surf, black, False,
					[(switch_button.w//2, switch_button.h//5),
					(switch_button.w//10, switch_button.h//2),
					(switch_button.w//2, 4*switch_button.h//5)], arrow_width)

		surface.fill(yellow)
		pygame.display.update()

		self.expanded = True
		while self.expanded:

			surface.fill(yellow)
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == MOUSEBUTTONUP:
					if collapse_button.collidepoint(event.pos):
						self.expanded = False
					elif switch_button.collidepoint(event.pos):
						surface.fill(yellow)
						pygame.display.update()
						page = new_page[page]

				entry_displays_1.update(event)
				entry_displays_2.update(event)


			if page == 1:
				rects_to_refresh = entry_displays_1.draw(surface)
				expanded_display = [disp for disp in entry_displays_1.sprites() if disp.face == 'back']
				if expanded_display:
					surface.blit(expanded_display[0].image, expanded_display[0].rect)
					rects_to_refresh.append(expanded_display[0].rect)
				surface.blit(switch_right_surf, switch_button)
			elif page == 2:
				rects_to_refresh = entry_displays_2.draw(surface)
				expanded_display = [disp for disp in entry_displays_2.sprites() if disp.face == 'back']
				if expanded_display:
					surface.blit(expanded_display[0].image, expanded_display[0].rect)
					rects_to_refresh.append(expanded_display[0].rect)
				surface.blit(switch_left_surf, switch_button)

			surface.blit(collapse_surf, collapse_button)
			rects_to_refresh += [collapse_button, switch_button]
			pygame.display.update(rects_to_refresh)
			fpsClock.tick(fps)

			if not self.expanded:
				surface.fill(black)

class EntryDisplay(pygame.sprite.Sprite):
	"""Sprite wrapper of WorEntry objects, used in Stack Gallery when a Session
	Display is expanded to show words with details.

	An EntryDisplay has two sides: front (word + category) and 
	back (meaning + example). Each side has its own image (Surface)
	and depending on the status of the sprite (if it has been clicked),
	the sprite's reference image is chosen as one of the two sides."""
	def __init__(self, entry, rect=(0,0,25,25), *groups):
		super().__init__(*groups)
		self.center = (0,0)
		self.rect = pygame.Rect(rect)
		self.image = pygame.Surface(self.rect.size)
		self.entry = entry
		self.face = 'front'

		# Adapt image dimensions to word
		word = main_game_font.render(self.entry.word, True, black)
		category = session_display_font.render(self.entry.category, True, black)
		dim = (max(self.image.get_width(), 1.05*word.get_width(), 1.2*category.get_width()),
			max(self.image.get_height(), 1.05*(word.get_height() + category.get_height()) ))

		self.front_image = pygame.Surface(dim)
		self.front_image.fill(yellow)
		# Blit word and category onto front_image
		word_rect = word.get_rect(); word_rect.midtop = self.front_image.get_rect().midtop
		categ_rect = category.get_rect(); categ_rect.midbottom = self.front_image.get_rect().midbottom
		self.front_image.blit(word, word_rect); self.front_image.blit(category, categ_rect)

		self.back_image = self.draw_back_image()

	def calculate_linebreaks(self, limit):
		width_limit = limit

		meaning_words = self.entry.meaning.split(' ')
		m_line_surfs = []
		current_line = ''
		current_width = 0
		for word in meaning_words:
			word_surf = meaning_font.render(word, True, white)
			current_width += word_surf.get_width()
			if current_width < width_limit:
				current_line += str(word + ' ')
			else:
				m_line_surfs.append(meaning_font.render(current_line.rstrip(), True, black))
				current_width = 0
				current_line = word + ' '
		m_line_surfs.append(meaning_font.render(current_line.rstrip(), True, black))

		example_words = self.entry.example.split(' ')
		ex_line_surfs = []
		current_line = ''
		current_width = 0
		for word in example_words:
			word_surf = example_font.render(word, True, white)
			current_width += word_surf.get_width()
			if current_width < width_limit:
				current_line += str(word + ' ')
			else:
				ex_line_surfs.append(example_font.render(current_line.rstrip(), True, black))
				current_width = 0
				current_line = word + ' '
		ex_line_surfs.append(example_font.render(current_line.rstrip(), True, black))

		return {'meaning':m_line_surfs, 'example':ex_line_surfs}

	def draw_back_image(self):
		lines = self.calculate_linebreaks(limit=0.2*screen_width)
		all_lines = lines['meaning'] + lines['example']
		back_image_size = (1.05*max([line.get_width() for line in all_lines]),
						1.05*sum([10+line.get_height() for line in all_lines]) )
		back_image = pygame.Surface(back_image_size)
		back_image.fill(yellow)

		# Meaning
		y_offset = 5
		for i in range(len(lines['meaning'])):
			curr_line_surf = lines['meaning'][i]
			curr_line_width, curr_line_heigth = curr_line_surf.get_size()

			back_image.blit(curr_line_surf, 
				(5, y_offset, curr_line_width, curr_line_heigth))
			y_offset += curr_line_heigth + 5

		# Example
		y_offset += 15
		if len(self.entry.example) > 5:
			for i in range(len(lines['example'])):
				curr_line_surf = lines['example'][i]
				curr_line_width, curr_line_heigth = curr_line_surf.get_size()

				back_image.blit(curr_line_surf, 
					(5, y_offset, curr_line_width, curr_line_heigth))
				y_offset += curr_line_heigth + 5
		else:
			no_example_surf = example_font.render('No example available', True, white)
			no_ex_w, no_ex_h = no_example_surf.get_size()
			back_image.blit(no_example_surf,
					(5, y_offset, no_ex_w, no_ex_h))

		pygame.draw.rect(back_image, white, back_image.get_rect(), 5)

		return back_image
		
	def update(self, event):

		if self.face == 'front':
			self.image = self.front_image
			self.rect = self.image.get_rect()
			self.rect.center = self.center
		elif self.face == 'back':
			self.image = self.back_image
			self.rect = self.image.get_rect()
			self.rect.center = self.center
			self.correct_pos()

		if event.type == MOUSEBUTTONUP:
			if self.rect.collidepoint(event.pos):
				self.face = 'back'
			else:
				self.face = 'front'

	def correct_pos(self):
		"""If back image goes beyond screen limit, relocate rect"""
		if self.rect.top < 0:
			self.rect.top = 0.05*screen_height
		if self.rect.bottom > screen_height:
			self.rect.bottom = 0.95*screen_height
		if self.rect.left < 0:
			self.rect.left = 0.02*screen_width
		if self.rect.right > screen_width:
			self.rect.right = 0.98*screen_width

class Hangman:

	def __init__(self, step=0):
		self.image = pygame.Surface((0.8*screen_width//2, 0.85*screen_height)).convert()
		self.rect = self.image.get_rect()
		self.rect.center = (3*screen_width//4, screen_height//2)
		self.rect.top = 0.1*screen_height
		self.step = step

	def update(self, newstep):
		self.step = newstep

	def draw(self, surface):
		wood_width = 5
		person_width = 2
		if self.step == 0:
			# Background + Frame
			self.image.fill(gray)
			pygame.draw.rect(self.image, white, ((0,0), self.image.get_size()), 3)

			surface.blit(self.image, self.rect)

		elif self.step == 1:
			# Background + Frame
			self.image.fill(gray)
			pygame.draw.rect(self.image, white, ((0,0), self.image.get_size()), 3)
			# Horizontal Base
			pygame.draw.line(self.image, white, (0, 0.95*self.rect.h),
							(self.rect.w, 0.95*self.rect.h), wood_width)

			surface.blit(self.image, self.rect)

		elif self.step == 2:
			# Background + Frame
			self.image.fill(gray)
			pygame.draw.rect(self.image, white, ((0,0), self.image.get_size()), 3)
			# Horizontal Base
			pygame.draw.line(self.image, white, (0, 0.95*self.rect.h),
							(self.rect.w, 0.95*self.rect.h), wood_width)
			# Vertical Base
			pygame.draw.line(self.image, white, (20, 0.95*self.rect.h), 
							(20, 20), wood_width)

			surface.blit(self.image, self.rect)

		elif self.step == 3:
			# Background + Frame
			self.image.fill(gray)
			pygame.draw.rect(self.image, white, ((0,0), self.image.get_size()), 3)
			# Horizontal Base
			pygame.draw.line(self.image, white, (0, 0.95*self.rect.h),
							(self.rect.w, 0.95*self.rect.h), wood_width)
			# Vertical Base
			pygame.draw.line(self.image, white, (20, 0.95*self.rect.h), 
							(20, 20), wood_width)
			# Horizontal upper stick + rope
			pygame.draw.lines(self.image, white, False,
					[(20,20), (self.rect.w//2, 20), (self.rect.w//2, self.rect.h//8)], 
					wood_width)

			surface.blit(self.image, self.rect)

		elif self.step == 4:
			# Background + Frame
			self.image.fill(gray)
			pygame.draw.rect(self.image, white, ((0,0), self.image.get_size()), 3)
			# Horizontal Base
			pygame.draw.line(self.image, white, (0, 0.95*self.rect.h),
							(self.rect.w, 0.95*self.rect.h), wood_width)
			# Vertical Base
			pygame.draw.line(self.image, white, (20, 0.95*self.rect.h), 
							(20, 20), wood_width)
			# Horizontal upper stick + rope
			pygame.draw.lines(self.image, white, False,
					[(20,20), (self.rect.w//2, 20), (self.rect.w//2, self.rect.h//8)], 
					wood_width)
			# Head
			circle_center = (self.rect.w//2, 2*self.rect.h//8)
			circle_radius = self.rect.h//8
			pygame.draw.circle(self.image, white, circle_center, circle_radius, person_width)

			surface.blit(self.image, self.rect)

		elif self.step == 5:
			# Background + Frame
			self.image.fill(gray)
			pygame.draw.rect(self.image, white, ((0,0), self.image.get_size()), 3)
			# Horizontal Base
			pygame.draw.line(self.image, white, (0, 0.95*self.rect.h),
							(self.rect.w, 0.95*self.rect.h), wood_width)
			# Vertical Base
			pygame.draw.line(self.image, white, (20, 0.95*self.rect.h), 
							(20, 20), wood_width)
			# Horizontal upper stick + rope
			pygame.draw.lines(self.image, white, False,
					[(20,20), (self.rect.w//2, 20), (self.rect.w//2, self.rect.h//8)], 
					wood_width)
			# Head
			circle_center = (self.rect.w//2, 2*self.rect.h//8)
			circle_radius = self.rect.h//8
			pygame.draw.circle(self.image, white, circle_center, circle_radius, person_width)
			# Body
			pygame.draw.line(self.image, white, 
				(self.rect.w//2, circle_center[1]+circle_radius),
				(self.rect.w//2, 3*self.rect.h//5), person_width)

			surface.blit(self.image, self.rect)

		elif self.step == 6:
			# Background + Frame
			self.image.fill(gray)
			pygame.draw.rect(self.image, white, ((0,0), self.image.get_size()), 3)
			# Horizontal Base
			pygame.draw.line(self.image, white, (0, 0.95*self.rect.h),
							(self.rect.w, 0.95*self.rect.h), wood_width)
			# Vertical Base
			pygame.draw.line(self.image, white, (20, 0.95*self.rect.h), 
							(20, 20), wood_width)
			# Horizontal upper stick + rope
			pygame.draw.lines(self.image, white, False,
					[(20,20), (self.rect.w//2, 20), (self.rect.w//2, self.rect.h//8)], 
					wood_width)
			# Head
			circle_center = (self.rect.w//2, 2*self.rect.h//8)
			circle_radius = self.rect.h//8
			pygame.draw.circle(self.image, white, circle_center, circle_radius, person_width)
			# Body
			pygame.draw.line(self.image, white, 
				(self.rect.w//2, circle_center[1]+circle_radius),
				(self.rect.w//2, 3*self.rect.h//5), person_width)
			# Legs
			pygame.draw.lines(self.image, white, False,
					[(self.rect.w//3, 7*self.rect.h//8),
					(self.rect.w//2, 3*self.rect.h//5),
					(2*self.rect.w//3, 7*self.rect.h//8)], person_width)

			surface.blit(self.image, self.rect)

		elif self.step == 7:
			# Background + Frame
			self.image.fill(gray)
			pygame.draw.rect(self.image, white, ((0,0), self.image.get_size()), 3)
			# Horizontal Base
			pygame.draw.line(self.image, white, (0, 0.95*self.rect.h),
							(self.rect.w, 0.95*self.rect.h), wood_width)
			# Vertical Base
			pygame.draw.line(self.image, white, (20, 0.95*self.rect.h), 
							(20, 20), wood_width)
			# Horizontal upper stick + rope
			pygame.draw.lines(self.image, white, False,
					[(20,20), (self.rect.w//2, 20), (self.rect.w//2, self.rect.h//8)], 
					wood_width)
			# Head
			circle_center = (self.rect.w//2, 2*self.rect.h//8)
			circle_radius = self.rect.h//8
			pygame.draw.circle(self.image, white, circle_center, circle_radius, person_width)
			# Body
			pygame.draw.line(self.image, white, 
				(self.rect.w//2, circle_center[1]+circle_radius),
				(self.rect.w//2, 3*self.rect.h//5), person_width)
			# Legs
			pygame.draw.lines(self.image, white, False,
					[(self.rect.w//3, 7*self.rect.h//8),
					(self.rect.w//2, 3*self.rect.h//5),
					(2*self.rect.w//3, 7*self.rect.h//8)], person_width)
			# Arms
			pygame.draw.lines(self.image, white, False,
					[(2*self.rect.w//8, 1.2*circle_center[1]+circle_radius),
					(self.rect.w//2, self.rect.h//2),
					(6*self.rect.w//8, 1.2*circle_center[1]+circle_radius)], person_width)
			# Dead eyes
			eye_sep = 15; eye_width = 5; eye_height = 5
			pygame.draw.line(self.image, white,
					(circle_center[0]-eye_sep-eye_width, circle_center[1]-eye_height),
					(circle_center[0]-eye_sep+eye_width, circle_center[1]+eye_height),
					person_width)
			pygame.draw.line(self.image, white,
					(circle_center[0]-eye_sep-eye_width, circle_center[1]+eye_height),
					(circle_center[0]-eye_sep+eye_width, circle_center[1]-eye_height),
					person_width)
			pygame.draw.line(self.image, white,
					(circle_center[0]+eye_sep-eye_width, circle_center[1]-eye_height),
					(circle_center[0]+eye_sep+eye_width, circle_center[1]+eye_height),
					person_width)
			pygame.draw.line(self.image, white,
					(circle_center[0]+eye_sep-eye_width, circle_center[1]+eye_height),
					(circle_center[0]+eye_sep+eye_width, circle_center[1]-eye_height),
					person_width)
			surface.blit(self.image, self.rect)

class MenuButton(pygame.sprite.Sprite):
	"""Class for generic menu buttons, both for main and pause screens"""

	def __init__(self, text='Some button', subtext = None, fontObj=main_game_font, 
	font_color=black, bg_color=yellow, highlight_bg_color=white,
	bg_rect=(0,0,60,20), *groups, **args):

		# Initialize parent class
		super().__init__(*groups)
		# Font-related attributes
		self.font = fontObj
		self.text = text
		self.subtext = subtext
		self.font_color = font_color
		self.font_surface = self.font.render(self.text, True, self.font_color)
		self.font_rect = self.font_surface.get_rect()
		
		# Background rect attributes
		self.button_pos = pygame.Rect(bg_rect)
		self.bg_color = bg_color
		self.highlight_bg_color = highlight_bg_color

		self.image = pygame.Surface(bg_rect[2:]).convert()
		self.rect = pygame.draw.rect(self.image, bg_color, ((0,0), bg_rect[2:]), 0)
		self.rect.center = self.button_pos.center
		#self.bg_rectangle = pygame.draw.rect(self.image, yellow, bg_rect_dimensions, 0)
		self.font_rect.center = self.button_pos.center
		
		# Boolean parameters for behaviour
		self.is_on_screen = True
		self.is_clicked = False
		
	def update(self, mainsurf):
		if not self.subtext and self.is_on_screen:	
			if self.is_clicked:
				self.rect = pygame.draw.rect(self.image, self.highlight_bg_color,
							((0,0), self.button_pos[2:]), 0)
				self.rect.center = self.button_pos.center
			else:
				self.rect = pygame.draw.rect(self.image, self.bg_color,
							((0,0), self.button_pos[2:]), 0)
				self.rect.center = self.button_pos.center

		elif self.subtext and self.is_on_screen:
			pass

		elif not self.is_on_screen:
			self.rect = pygame.draw.rect(self.image, self.font_color,
							((0,0), self.button_pos[2:]), 0)
			self.rect.center = self.button_pos.center


		mainsurf.blit(self.image, self.button_pos)
		mainsurf.blit(self.font_surface, self.font_rect)
		
	def die(self):
		self.is_on_screen = False

	def resurrect(self):
		self.is_on_screen = True

class InputBox():
	"""Source: https://stackoverflow.com/a/46390412/11568784"""
	def __init__(self, x, y, w, h, text=''):
		self.rect = pygame.Rect(x, y, w, h)
		self.original_w = self.rect.w
		self.color = blue
		self.text = text
		self.txt_surface = main_game_font.render(text, True, self.color)
		self.active = False

	def handle_event(self, event):
		if event.type == MOUSEBUTTONDOWN:
			# If the user clicked on the input_box rect.
			if self.rect.collidepoint(event.pos):
				# Toggle the active variable.
				self.active = not self.active
			else:
				self.active = False
			# Change the current color of the input box.
			self.color = yellow if self.active else blue
		if event.type == KEYDOWN:
			if self.active:
				if event.key == K_RETURN:			
					answer = self.text
					self.text = ''
					self.txt_surface = main_game_font.render(self.text, True, self.color)
					return answer
			
				elif event.key == K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.text += event.unicode
				# Re-render the text.
				self.txt_surface = main_game_font.render(self.text, True, self.color)
			else:
				# NOTE
				# This line here "fixes" the bug that makes the game quit when 
				# pressing Enter and the input box is inactive. Not really the 
				# best solution, try to come up with something cleverer
				return ''

	def update(self):
		# Resize the box if the text is too long.
		width = max(self.original_w, self.txt_surface.get_width()+10)
		self.rect.w = width

	def draw(self, screen):
		# Blit the text.
		screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
		# Blit the rect.
		pygame.draw.rect(screen, self.color, self.rect, 2)


# Functions --------------------------------------------------------------
def main():
	# pygame.init()
	# load and set the logo
	# logo = pygame.image.load("logo32x32.png")
	# pygame.display.set_icon(logo)

	global mainsurface
 
	mainsurface = pygame.display.set_mode((screen_width, screen_height))
	pygame.display.set_caption("Valebulary")

	show_start_screen(surface=mainsurface)


def show_start_screen(surface):
	"""Show main menu: initial animation + buttons: 
	new game, load game, options, exit"""

	surface.fill(black)
	showing_main_menu = True
	
	# Calculate layout grid
	# TODO: abstract as function?
	left_grid_x = screen_width//3
	mayor_grid_y = [i*(screen_height/3) for i in (1,2,3)]
	midcenter, bottomcenter = np.mean(mayor_grid_y[:2]), np.mean(mayor_grid_y[1:])
	n_buttons = 3
	space_for_buttons = (bottomcenter - midcenter)/n_buttons
	starts = [midcenter + i*space_for_buttons for i in range(n_buttons)]

	# Draw title
	# TODO: abstract as function?
	title_surf = title_font.render('GRE Vocabulary', True, yellow)
	title_surf_rect = title_surf.get_rect()
	title_surf_rect.center = screen_rect.center
	title_surf_rect.y = mayor_grid_y[0]//2
	title2_surf = title_font.render('Flashcards!', True, yellow)
	title2_surf_rect = title2_surf.get_rect()
	title2_surf_rect.midtop = title_surf_rect.midbottom
	title2_surf_rect.y *= 1.1
	
	# Draw buttons
	start_game = MenuButton(text='Start hangman', bg_rect=(left_grid_x, starts[0], left_grid_x, space_for_buttons-10))
	see_stacks = MenuButton(text='Stacks gallery', bg_rect=(left_grid_x, starts[1], left_grid_x, space_for_buttons-10))
	exit = MenuButton(text='Exit', bg_rect=(left_grid_x, starts[2], left_grid_x, space_for_buttons-10))

	# Gather button Rects in a Group
	menu_buttons = pygame.sprite.RenderUpdates(start_game, see_stacks, exit)

	# main screen loop
	while showing_main_menu:
		
		surface.blits([(title_surf, title_surf_rect), (title2_surf, title2_surf_rect)])
		
		mousex, mousey = 0, 0
		mouseClicked, mouseReleased = False, False
		
		# Re-initialize buttons in case we come back from other screen
		[button.resurrect() for button in menu_buttons]

		# Event handling
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				showing_main_menu = False
				pygame.quit()
				sys.exit()
			
			elif event.type == MOUSEBUTTONDOWN:
				mousex, mousey = event.pos
				mouseClicked = True
			elif event.type == MOUSEBUTTONUP:
				mousex, mousey = event.pos
				mouseReleased = True

		# Highlight box if mouse clicked it
		for button in menu_buttons:
			if button.rect.collidepoint((mousex, mousey)) and mouseClicked:
				button.is_clicked = True
			elif mouseReleased:
				button.is_clicked = False

		menu_buttons.draw(surface)
		menu_buttons.update(surface)
		pygame.display.update()
		fpsClock.tick(fps)

		# If button pressed, perform its action
		if start_game.rect.collidepoint((mousex, mousey)) and mouseReleased:
			surface.fill(black)
			pygame.display.update()
			run_game(surface=mainsurface)

		if see_stacks.rect.collidepoint((mousex, mousey)) and mouseReleased:
			surface.fill(black)
			pygame.display.update()
			show_stacks(surface=mainsurface)

		if exit.rect.collidepoint((mousex, mousey)) and mouseReleased:
			pygame.quit()
			sys.exit()

	# End of main loop
# End of show_start_screen()

def run_game(surface):
	
	surface.fill(background)

	# Either load an unfinished session or initialize a new one
	try:
		current_session = load_session('current_session.obj')
	except:
		current_session = master_session.sampleN_pop(50)

	# Try importing session history or initialize a history object
	try:
		old_sessions = load_session('old_sessions.obj')
	except:
		old_sessions = []

	# If last session is completed, create a new one
	if current_session.completed:
		old_sessions.append(current_session)
		current_session = master_session.sampleN_pop(50)		
	
	# Sort words into groups
#	stock = pygame.sprite.Group()
#	for entry in vocabulary:
#		wordcard = WordCard(entry=entry)
#		stock.add(wordcard)

#	known = pygame.sprite.Group()
#	unknown = pygame.sprite.Group()

	### Initialize sprites ---
	# TODO I could rewrite this piece using classes and stuff but for now it works
	hangman = Hangman()	

	# Choose a random word and make sure it is valid (has meaning)
	shown_word = WordCard(entry=current_session.sample1())
	while not shown_word.check_validity():
			shown_word = WordCard(entry=current_session.sample1())
	input_box = InputBox(screen_width//10, 3*screen_height//4,
						screen_width//3, 0.8*screen_height//4)

	# Stack count
	stack_count = pygame.Rect((0,0,75,75))
	stack_count.center = screen_rect.center
	stack_count.y -= 3*90

	# Score count
	correct_guesses = pygame.Rect((0,0,75,75))
	correct_guesses.center = screen_rect.center
	correct_guesses.y -= 2*90

	wrong_guesses = pygame.Rect((0,0,75,75))
	wrong_guesses.center = screen_rect.center
	wrong_guesses.y -= 90

	# Help button
	help_button_rect = pygame.Rect((0,0,75,75))
	help_button_rect.center = screen_rect.center
	# help_button_rect.y += 90
	question_mark = main_game_font.render('?', True, yellow)
	question_rect = question_mark.get_rect()
	question_rect.center = help_button_rect.center

	# Show one letter button
	show_letter = pygame.Rect((0,0,75,75))
	show_letter.center = screen_rect.center
	show_letter.y += 90
	show_letter_surf = pygame.Surface(show_letter.size)
	show_a = main_game_font.render('A', True, yellow)
	show_a_rect = show_a.get_rect()
	show_a_rect.midright = show_letter.center
	pygame.draw.line(show_letter_surf, yellow, 
			(0.1*show_letter.w, 0.8*show_letter.h),
			(0.4*show_letter.w, 0.8*show_letter.h), 2)
	pygame.draw.line(show_letter_surf, yellow, 
			(0.6*show_letter.w, 0.8*show_letter.h),
			(0.9*show_letter.w, 0.8*show_letter.h), 2)

	# Button to skip word
	skip_word = pygame.Rect((0,0,75,75))
	skip_word.center = screen_rect.center
	skip_word.y += 2*90
	arrow_surf = pygame.Surface(skip_word.size)
	arrow_rect = arrow_surf.get_rect()
	pygame.draw.line(arrow_surf, blue, (arrow_rect.w//10, arrow_rect.centery),
					(9*arrow_rect.w//10, arrow_rect.centery), 5)
	pygame.draw.lines(arrow_surf, blue, False,
					[(arrow_rect.w//2, arrow_rect.h//5),
					(9*arrow_rect.w//10, arrow_rect.centery),
					(arrow_rect.w//2, 3*arrow_rect.h//4)], 5)
	arrow_rect.center = skip_word.center

	# Show word button
	show_word = pygame.Rect((0,0,75,75))
	show_word.center = screen_rect.center
	show_word.y += 3*90
	show_word_surf = pygame.Surface(show_word.size)
	pygame.draw.line(show_word_surf, red, (3*show_word.w//10, 3*show_word.h//10),
					(7*show_word.w//10, 7*show_word.h//10), 7)
	pygame.draw.line(show_word_surf, red, (3*show_word.w//10, 7*show_word.h//10),
					(7*show_word.w//10, 3*show_word.h//10), 7)

	# Button to exit to main menu
	main_menu_button = pygame.Rect(0,0,screen_height//13,screen_height//13)
	main_menu_surf = pygame.Surface(main_menu_button.size)
	main_menu_surf.fill(yellow)
	pygame.draw.line(main_menu_surf, black, (main_menu_button.w//10, main_menu_button.h//2),
					(9*main_menu_button.w//10, main_menu_button.h//2), 7)
	pygame.draw.lines(main_menu_surf, black, False,
					[(main_menu_button.w//2, main_menu_button.h//5),
					(main_menu_button.w//10, main_menu_button.h//2),
					(main_menu_button.w//2, 3*main_menu_button.h//4)], 7)

	game_running = True
	while game_running:
		### Event handling variables ---
		mousex, mousey = 0, 0
		mouseClicked, mouseReleased = False, False

		# Event handling
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				save_session(old_sessions, 'old_sessions.obj')
				save_session(current_session, 'current_session.obj')
				save_session(master_session, 'master_session.obj')
				pygame.quit()
				sys.exit()
			
			elif event.type == MOUSEBUTTONDOWN:
				mousex, mousey = event.pos
				mouseClicked = True
			elif event.type == MOUSEBUTTONUP:
				mousex, mousey = event.pos
				mouseReleased = True

			elif event.type == KEYDOWN and event.key == K_SPACE:
				pass

			elif event.type == KEYDOWN and event.key == K_RETURN:
				answer = input_box.handle_event(event)
				if answer.lower() == shown_word.entry.word.lower():
					shown_word.reveal(surface)
					pygame.display.update()
					hangman.step = 0
					correct_word_animation()

					# Check if the word was already either known or unknown
					word_already_unknown, word_already_known = False, False
					for known_entry in current_session.known:
						if shown_word.entry == known_entry:
							word_already_known = True
					for unknown_entry in current_session.unknown:
						if shown_word.entry == unknown_entry:
							word_already_unknown = True

					# Remove from the unkown stack if it was there
					if word_already_unknown:
						entry_in_unknown_list = [entry for entry in current_session.unknown if entry == shown_word.entry][0]
						current_session.unknown.remove(entry_in_unknown_list)
						current_session.known.append(shown_word.entry)
					# Add to known only if it wasn't known already
					elif not word_already_known:
						current_session.known.append(shown_word.entry)
					shown_word = WordCard(entry=current_session.sample1())
				else:
					hangman.step += 1
					if hangman.step == 7:
						hangman.draw(surface=mainsurface)
						surface.blit(hangman.image, hangman.rect)
						pygame.display.update()

						shown_word.reveal(surface)
						out_of_attempts_animation()
						hangman.step = 0
						
						# Check if word was already known or unknown
						word_already_unknown, word_already_known = False, False
						for known_entry in current_session.known:
							if shown_word.entry == known_entry:
								word_already_known = True
						for unknown_entry in current_session.unknown:
							if shown_word.entry == unknown_entry:
								word_already_unknown = True
						# Add to unknown only if it wasn't already there
						if not word_already_unknown:
							current_session.unknown.append(shown_word.entry)
						# If it was known, remove from known and add to unknown
						if word_already_known:
							entry_in_known_list = [entry for entry in current_session.known if entry == shown_word.entry][0]
							current_session.known.remove(entry_in_known_list)
							current_session.unknown.append(shown_word.entry)

						shown_word = WordCard(entry=current_session.sample1())

			if help_button_rect.collidepoint((mousex, mousey)):
				shown_word.showing_example = True
			elif show_letter.collidepoint((mousex, mousey)):
				shown_word.showing_letter = True
			elif skip_word.collidepoint((mousex, mousey)) and mouseReleased:
				current_session.active_stack.append(shown_word.entry)
				shown_word = WordCard(entry=current_session.sample1())
			elif show_word.collidepoint((mousex, mousey)) and mouseReleased:
				shown_word.reveal(surface)
				pygame.display.update()
				time.sleep(2)
				hangman.step = 0
				word_already_unknown, word_already_known = False, False
				for known_entry in current_session.known:
					if shown_word.entry == known_entry:
						word_already_known = True
				for unknown_entry in current_session.unknown:
					if shown_word.entry == unknown_entry:
						word_already_unknown = True
				# Add to unknown only if it wasn't already there
				if not word_already_unknown:
					current_session.unknown.append(shown_word.entry)
				# If it was known, remove from known and add to unknown
				if word_already_known:
					entry_in_known_list = [entry for entry in current_session.known if entry == shown_word.entry][0]
					current_session.known.remove(entry_in_known_list)
					current_session.unknown.append(shown_word.entry)
				shown_word = WordCard(entry=current_session.sample1())

			elif main_menu_button.collidepoint((mousex, mousey)) and mouseReleased:
				save_session(old_sessions, 'old_sessions.obj')
				save_session(current_session, 'current_session.obj')
				save_session(master_session, 'master_session.obj')
				game_running = False

			input_box.handle_event(event)

		### Update states ----
		if len(current_session.known) == len(current_session.stack) and \
			len(current_session.unknown) == 0: # A bit redundant, but just to make sure
			session_complete_animation()
			current_session.completed = True
			old_sessions.append(current_session)
			current_session = master_session.sampleN_pop(50)

		input_box.update()

		stack_n = main_game_font.render(str(len(current_session.unseen)), True, white)
		stack_n_rect = stack_n.get_rect()
		stack_n_rect.center = stack_count.center

		correct_n = main_game_font.render(str(len(current_session.known)), True, green)
		correct_n_rect = correct_n.get_rect()
		correct_n_rect.center = correct_guesses.center
		wrong_n = main_game_font.render(str(len(current_session.unknown)), True, red)
		wrong_n_rect = wrong_n.get_rect()
		wrong_n_rect.center = wrong_guesses.center

		# Draw
		surface.fill(background)
		shown_word.draw(surface=surface)
		input_box.draw(screen=surface)
		hangman.draw(surface=mainsurface)

		pygame.draw.rect(surface, white, stack_count, 5)
		surface.blit(stack_n, stack_n_rect)

		pygame.draw.rect(surface, green, correct_guesses, 5)
		surface.blit(correct_n, correct_n_rect)

		pygame.draw.rect(surface, red, wrong_guesses, 5)
		surface.blit(wrong_n, wrong_n_rect)

		pygame.draw.rect(surface, yellow, help_button_rect, 5)
		surface.blit(question_mark, question_rect)

		surface.blit(show_letter_surf, show_letter)
		surface.blit(show_a, show_a_rect)
		pygame.draw.rect(surface, yellow, show_letter, 5)

		surface.blit(arrow_surf, arrow_rect)
		pygame.draw.rect(surface, blue, skip_word, 5)

		surface.blit(show_word_surf, show_word)
		pygame.draw.rect(surface, red, show_word, 5)

		surface.blit(main_menu_surf, main_menu_button)

		surface.blit(hangman.image, hangman.rect)
		pygame.display.update()
		fpsClock.tick(fps)

	surface.fill(black)


def correct_word_animation():
	surface_alphas = list(range(0, 255, 255//15)) + [255]*15 + list(range(255, 0, -255//10))

	correct_text = correct_font.render('Correct!', True, green)

	box_surface = pygame.Surface(correct_text.get_size())
	box_surface_rect = box_surface.get_rect()
	box_surface_rect.center = screen_rect.center
	box_surface.fill((0,0,0,0))
	
	box_surface.blit(correct_text, pygame.Rect((2,2),(correct_text.get_size())))
	box_surface.set_alpha(255)
	
	for alpha in surface_alphas:
		mainsurface.fill(black, box_surface_rect)
		box_surface.set_alpha(alpha)
		mainsurface.blit(box_surface, box_surface_rect)
		pygame.display.update(box_surface_rect)
		fpsClock.tick(fps)

def out_of_attempts_animation():
	surface_alphas = list(range(0, 255, 255//15)) + [255]*15 + list(range(255, 0, -255//10))
	wrong_text = correct_font.render('Out of attempts!', True, red)

	box_surface = pygame.Surface(wrong_text.get_size())
	box_surface_rect = box_surface.get_rect()
	box_surface_rect.center = screen_rect.center
	box_surface.fill((0,0,0,0))

	box_surface.blit(wrong_text, pygame.Rect((2,2),(wrong_text.get_size())))
	box_surface.set_alpha(255)
	
	for i in range(2):
		for alpha in surface_alphas:
			mainsurface.fill(black, box_surface_rect)
			box_surface.set_alpha(alpha)
			mainsurface.blit(box_surface, box_surface_rect)
			pygame.display.update(box_surface_rect)
			fpsClock.tick(fps)

def session_complete_animation():
	surface_alphas = list(range(0, 255, 255//15)) + [255]*15 + list(range(255, 0, -255//10))
	session_text = correct_font.render('Session', True, green)
	complete_text = correct_font.render('complete!', True, green)

	box_surface = pygame.Surface((complete_text.get_width(), 2.1*session_text.get_height()))
	box_surface_rect = box_surface.get_rect()
	box_surface_rect.center = screen_rect.center
	box_surface.fill((0,0,0,0))

	box_surface.blit(session_text, pygame.Rect((2,2),(session_text.get_size())))
	box_surface.blit(complete_text, pygame.Rect((2,box_surface_rect.h//2),(complete_text.get_size())))
	box_surface.set_alpha(255)

	for alpha in surface_alphas:
		mainsurface.fill(black, box_surface_rect)
		box_surface.set_alpha(alpha)
		mainsurface.blit(box_surface, box_surface_rect)
		pygame.display.update(box_surface_rect)
		fpsClock.tick(fps)


def show_stacks(surface, nrows=4, ncols=5):
	"""Show 4x5 grid with stack progress: 
		-Green stacks are complete
		-Yellow  stacks are active
		-Rest of grids filled with gray squares
	"""

	# Either load an unfinished session or initialize a new one
	try:
		current_session = load_session('current_session.obj')
	except:
		current_session = master_session.sampleN_pop(50)

	# Try importing session history or initialize a history object
	try:
		old_sessions = load_session('old_sessions.obj')
	except:
		old_sessions = []

	# If last session is completed, create a new one
	if current_session.completed:
		old_sessions.append(current_session)
		current_session = master_session.sampleN_pop(50)		

	mainsurface.fill(black)

	# Calculate layout: 4 rows, 5 stacks a row
	y_grid = [(i+1)*screen_height//nrows for i in range(nrows)]
	x_grid = [(i+1)*screen_width//ncols for i in range(ncols)]
	grid = [(x,y) for x in x_grid for y in y_grid]

	# Gather past and present sessions
	session_displays = pygame.sprite.Group()
	for session in old_sessions:
		session_displays.add(SessionDisplay(session=session))
	session_displays.add(SessionDisplay(session=current_session))
	all_sessions = session_displays.sprites()
	
	# Assign coordinates in grid to each session
	for i in range(len(all_sessions)):
		all_sessions[i].rect.center = grid[i]
		

	# Display return button
	return_button = pygame.Rect(0,0,screen_height//10,screen_height//10)
	return_surf = pygame.Surface(return_button.size)
	return_surf.fill(yellow)
	pygame.draw.line(return_surf, black, (return_button.w//10, return_button.h//2),
					(9*return_button.w//10, return_button.h//2), 7)
	pygame.draw.lines(return_surf, black, False,
					[(return_button.w//2, return_button.h//5),
					(return_button.w//10, return_button.h//2),
					(return_button.w//2, 3*return_button.h//4)], 7)


	showing_stacks = True
	while showing_stacks:
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONUP:
				if return_button.collidepoint(event.pos):
					save_session(current_session, 'current_session.obj')
					showing_stacks = False

			session_displays.update(event, surface)


		surface.fill(black)
		session_displays.draw(surface)
		surface.blit(return_surf, return_button)
		
		pygame.display.update()
		fpsClock.tick(fps)

		if not showing_stacks:
			surface.fill(black)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__": main()
