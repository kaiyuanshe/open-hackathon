from distutils.core import setup
from backend import __version__

setup(name='osslab',
      version = __version__,
      author = 'junbo wang',
      author_email='juniwang@microsoft.com',
      packages=['osslab'],
) 
