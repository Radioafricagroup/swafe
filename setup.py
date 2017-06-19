from setuptools import setup, find_packages

setup(name='swafe',
      version='0.1.10.dev1',
      description='A python library for orchestrating AWS SWF workflows',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: Developers',
      ],
      keywords='aws-swf SWF',
      url='https://github.com/ishuah/swafe',
      author='Ishuah Kariuki',
      author_email='kariuki@ishuah.com',
      license='GNU GPLv3',
      packages=find_packages(exclude=("test*", )),
      package_dir={
        'swafe': 'swafe'
        },
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
