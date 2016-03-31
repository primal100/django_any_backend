from setuptools import setup, find_packages


setup(name='django_any_backend',
    version='0.1',
    description="Enable custom backends in Django",
    long_description="Easily implement custom backends such as remote APIs in Django",
    author='Paul Martin',
    author_email='greatestloginnameever@gmail.com',
    url='https://github.com/primal100/django_any_backend',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)