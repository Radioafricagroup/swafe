from setuptools import setup

setup(name='swafe',
      version='0.1',
      description='A python library for orchestrating AWS SWF workflows',
      classifiers=[
          'Development Status :: 1 - Alpha',
          'License :: OSI Approved :: GNU GPLv3',
          'Programming Language :: Python :: 2.7',
          'Topic :: AWS Simple Wokflow',
      ],
      keywords='aws-swf SWF',
      url='https://github.com/ishuah/swafe',
      author='Ishuah Kariuki',
      author_email='kariuki@ishuah.com',
      license='GNU GPLv3',
      packages=['swafe'],
      install_requires=[
          'boto3',
          'click'
      ],
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'swafe = swafe.cli:run',
          ]
      })
