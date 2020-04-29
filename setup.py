from setuptools import setup, find_packages

setup(name='arxiv_library',
      version='0.1',
      description='Extract Mathematical Expressions from ArXiV publications',
      url='https://github.com/Whadup/arxiv-library',
      author=u'Lukas Pfahler, Jonathan Schill, Jan Richter',
      author_email='{lukas.pfahler, jonathan.schill, jan-philip.richter}@tu-dortmund.de',
      license='MIT',
      packages=find_packages(),
      install_requires=['arxiv', 'tqdm'],
      zip_safe=False,
      include_package_data=True,
)
