#!/usr/bin/env python
import random
import pickle

class WordEntry():
	"""Simple class to for a vocabulary word"""
	def __init__(self, word, category, meaning, example, difficulty, is_known=False):
		self.word = word
		self.category = category
		self.meaning = meaning
		self.example = example
		self.difficulty = difficulty
		self.is_known = is_known
	
	def __repr__(self):
		return '{w} ({c}): {m}'.format(w=self.word, c=self.category, m=self.meaning)
	
	def __str__(self):
		return '{w} ({c})\n{m}\n{e}'.format(w=self.word, c=self.category, m=self.meaning, e=self.example)

	def __eq__(self, other):
		if isinstance(other, WordEntry):
			if self.word == other.word and self.category == other.category:
				return True
			else:
				return False
		else:
			raise TypeError('Comparison has to be between two WordEntry objects')

class Session():
	"""Class containing a collection of 50 WordCards that are either known or unkown"""
	def __init__(self, entries_list):
		self.stack = [entry for entry in entries_list] 
		self.active_stack = self.stack.copy()
		self.words = [entry.word for entry in self.stack]
		self.unseen = self.stack.copy()
		self.known = []
		self.unknown = []
		self.completed = False

	def __repr__(self):
		return (
			'Known: {k}\tUnknown: {u}'
			.format(k = len(self.known), u = len(self.unknown))
		)
	
	def __str__(self):
		return (
			'WordCard Session with {k} known and {u} unknown words among {s}; '
			'of which {a_s} are active'
			.format(k=len(self.known), u=len(self.unknown),
					s=len(self.stack), a_s=len(self.active_stack))
		)

	def __len__(self):
		return len(self.stack)

	def sample1(self):
		"""Sample 1 word out the stack. Depending on the word status, it has 
		a different chance of apprearing, namely:
		- Known word: 20%
		- Unseen word: 40%
		- Unknown word: 40%"""
		#choice = self.active_stack.keys()[random.choice(range(len(self.active_stack)))]
		len_k = 1 if len(self.known)>0 else 0
		len_uk = 1 if len(self.unknown)>0 else 0
		len_us = 1 if len(self.unseen)>0 else 0
		set_to_choose = random.choice(len_k*['known'] + \
				2*len_uk*['unknown'] + 2*len_us*['unseen'])
		if set_to_choose == 'known':
			return self.known[random.choice(range(len(self.known)))]
		elif set_to_choose == 'unknown':
			return self.unknown[random.choice(range(len(self.unknown)))]
		elif set_to_choose == 'unseen':
			return self.unseen.pop(random.choice(range(len(self.unseen))))
		else:
			return self.sample1()

	def sampleN_pop(self, n):
		""" Only meant for Master session. Sample n words out of the stack of 
		words that have not been used yet"""
		#choices = self.active_stack.keys()[random.sample(range(len(self.active_stack)), n)]
		choices = random.sample(range(len(self.active_stack)), n)
		stack_to_pop = [self.active_stack[choice] for choice in choices]
		self.active_stack = [entry for entry in self.active_stack if entry not in stack_to_pop]
		return Session(stack_to_pop)


def load_session(path):
	"""Wrapper for pickle.load()"""
	with open(path, 'rb') as p:
		session = pickle.load(p)
	return session

def save_session(obj, filename):
	"""Wrapper for pickle.dump()"""
	with open(filename, 'wb') as p:
		session = pickle.dump(obj, p)
	return None



"""
		choice_pool = self.known + 2*self.unknown + 2*self.unseen
		choice = random.choice(choice_pool)
		self.unseen -= 1
		if self.unseen < 0:
			self.unseen = 0
		return 
"""
