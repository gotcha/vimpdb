from setuptools import setup, find_packages

version = '0.1'

setup(name='vimpdb',
      version=version,
      description="Vim and Pdb integration",
      long_description=open("README.txt").read() + "\n" +
                       open("CREDITS.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[],
      keywords='',
      author='Godefroid Chapelle',
      author_email='gotcha@bubblenet.be',
      url='',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
