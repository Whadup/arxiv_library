from setuptools import setup, find_packages

setup(name='arxiv_library',
      version='0.1',
      description='Extract Mathematical Expressions from ArXiV publications',
      url='https://github.com/Whadup/arxiv-library',
      author=u'Lukas Pfahler, Jonathan Schill, Jan Richter',
      author_email='{lukas.pfahler, jonathan.schill, jan-philip.richter}@tu-dortmund.de',
      license='MIT',
      packages=['arxiv_library',
                'arxiv_library.compilation',
                'arxiv_library.extraction',
                'arxiv_library.io_pkg'],
      package_data={
          "": ["*.js"],
      },
      scripts=['extract_formulas'],
      install_requires=['arxiv', 'ray', 'python-magic', 'chardet', 'psutil', 'tqdm'],
      zip_safe=False
      )
