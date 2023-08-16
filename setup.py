from setuptools import setup, find_packages

setup(
    name="libcxx",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Metadata
    author="Eric Fiselier",
    author_email="ericwf@google.com",
    description="A set of tools for capturing libc++ metrics over time",
    long_description='''A set of tools for capturing libc++ metrics over time''',
    long_description_content_type="text/markdown",
    url="efcs.ca/this-is-not-a-website",
)
