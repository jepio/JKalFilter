from distutils.core import setup, Extension

ext = Extension("JKalFilter.libtest._libtest", ["libtest/libtest.c"])

setup(name="JKalFilter",
      version="1.0",
      description="Python Kalman Filter library.",
      author="jepio",
      url="https://jepio.github.io/JKalFilter/",
      ext_modules=[ext],
      packages=["JKalFilter", "JKalFilter.libtest"],
      package_dir={"": ".."})

