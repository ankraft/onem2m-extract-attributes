from setuptools import setup, find_packages

setup(
    name='oneM2M-extractAttributes',
    version='1.0.0',
    url='https://github.com/ankraft/onem2m-extract-attributes',
    author='Andreas Kraft',
    author_email='an.kraft@gmail.com',
    description='Extract attributes, short and long names, categories, and more from the oneM2M specification documents',
    packages=find_packages(),
	install_requires=[
		'docx',
		'rich',
		'unidecode'
	],
)
