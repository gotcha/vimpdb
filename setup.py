from setuptools import setup, find_packages

version = '0.4.5'

setup(name='vimpdb',
      version=version,
      description="Vim and Pdb integration",
      long_description=open("README.rst").read() + "\n" +
                       open("CREDITS.txt").read() + "\n" +
                       open("CHANGES.txt").read() + "\n" +
                       open("TODO.txt").read(),
      classifiers=[
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Text Editors',
      ],
      keywords='pdb vim',
      author='Godefroid Chapelle',
      author_email='gotcha@bubblenet.be',
      url='http://github.com/gotcha/vimpdb',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'vim_bridge',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
