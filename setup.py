from distutils.core import setup
from osslab import __version__

setup(name='osslab',
      version = __version__,
      author = 'junbo wang',
      author_email='juniwang@microsoft.com',
      packages=['osslab', 'osslab.src.common','osslab.src.exprs', 'osslab.src.database'],
) 
