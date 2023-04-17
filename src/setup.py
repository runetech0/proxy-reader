import setuptools


setuptools.setup(
    name="proxy_reader",
    version="0.1.2",
    author="Rehman Ali",
    author_email="rehmanali.9442289@gmail.com",
    description="A Simple tool to bulk read, format and check proxies",
    url="https://github.com/rehmanali1337/proxy-reader",
    packages=setuptools.find_packages(),
    install_requires=[],
    package_data={"proxy_reader": ["py.typed"]},
)
