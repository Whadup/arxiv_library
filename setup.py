from setuptools import setup

setup(name='arxiv_library',
      version='0.1',
      description='Extract Mathematical Expressions from ArXiV publications',
      url='https://github.com/Whadup/arxiv-library',
      author=u'Lukas Pfahler, Jonathan Schill, Jan Richter',
      author_email='{lukas.pfahler, jonathan.schill, jan-philip.richter}@tu-dortmund.de',
      license='MIT',
      packages=['arxiv_library'],
      install_requires=['arxiv', 'tqdm'],
      zip_safe=False
)
