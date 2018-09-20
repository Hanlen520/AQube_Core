from setuptools import setup, find_packages


setup(
    name='aqube',
    version='0.1.0',
    description='a flexible tool to operate android',
    author='williamfzc',
    author_email='fengzc@vip.qq.com',
    url='https://github.com/williamfzc/AQube_Core',
    packages=find_packages(),
    install_requires=[
        'fire',
        'python-json-logger',
        'requests',
    ]
)
