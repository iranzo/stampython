from setuptools import setup

setup(name='stampython',
      version='0.4',
      description='Karma bot for Telegram',
      url='http://github.com/iranzo/stampython',
      author='Pablo Iranzo Gómez',
      author_email='Pablo.Iranzo@gmail.com',
      license='GPL',
      scripts=['stampy.py'],
      install_requires=[
          'json',
          'sqlite3',
          'urllib',
          'prettytable',
      ],
      zip_safe=False)
