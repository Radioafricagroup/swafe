from setuptools import setup, find_packages

setup(name='swafer',
      version='0.0.3',
      description='A python library for orchestrating AWS SWF workflows, extended on Swafe by Ishuah, maintained by piedcrow',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
          'Intended Audience :: Developers',
      ],
      keywords='aws-swf SWF',
      url='https://github.com/Radioafricagroup/swafe',
      author='Joseph G.',
      author_email='ndungugitau@gmail.com',
      license='GNU GPLv3',
      packages=find_packages(exclude=("test*", )),
      package_dir={
        'swafe': 'swafe'
        },
      install_requires=[
          'boto3',
          'click',
          'future'

      ],
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'swafe = swafe.cli:run',
          ]
      },
      test_suite='nose.collector',
      tests_require=['nose', 'moto'])
