#!/usr/bin/env python

import sys
import cPickle
import StringIO

# Thanks to http://nadiaspot.com/why-python-pickle-is-insecure/

class SafeUnpickler(object):
	PICKLE_SAFE = {}

	@classmethod
	def find_class(cls, module, name):
		if not module in cls.PICKLE_SAFE:
			raise cPickle.UnpicklingError('Attempting to unpickle unsafe module %s' % module)
		
		__import__(module)
		mod = sys.modules[module]
			
		if not name in cls.PICKLE_SAFE[module]:
			raise cPickle.UnpicklingError('Attempting to unpickle unsafe class %s' % name)
			
		klass = getattr(mod, name)
		return klass

	@classmethod
	def loads(cls, pickle_string):
		try:
			safeUnpickler = cPickle.Unpickler(StringIO.StringIO(pickle_string))
			safeUnpickler.find_global = cls.find_class
			return safeUnpickler.load()
		except Exception, e:
			raise cPickle.UnpicklingError('Unpickler Error')
			
	@classmethod
	def load(cls, pickle_file):
		try:
			safeUnpickler = cPickle.Unpickler(pickle_file)
			safeUnpickler.find_global = cls.find_class
			return safeUnpickler.load()
		
		except EOFError, er:
			raise cPickle.UnpicklingError('Unpickler EOF Error')
		
		except Exception, e:
			raise cPickle.UnpicklingError('Unpickler Error')
