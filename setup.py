from distutils.core import setup
from backend import __version__

setup(name='backend_osslab',
      version = __version__,
      author = 'jihua kang',
      author_email='t-jikang@microsoft.com',
      packages=['backend','backend.apiserver','backend.backendlogger','backend.orm'],
) 
