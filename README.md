# batchtk

batchtk is my (james.chen@downstate.edu) python package for handling custom remote job submissions
```
.
├── README.md
├── batchtk ->python package<-
│   ├── batchtk ->generate batch exploration csv based on exploration space<-
│   │   ├── __init__.py
│   │   └── batchify.py 
│   ├── ipynb ->jupyter notebooks to test out various things<-
│   │   └── batchify.ipynb
│   └── runtk ->a script with subprocess handling, with variable passing through the environment<-
│       ├── __init__.py
│       ├── runners.py 
│       └── utils.py
├── avatk.egg-info ->python package stuff that allows for pip install -e .<-
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   ├── dependency_links.txt
│   ├── requires.txt
│   └── top_level.txt
└── pyproject.toml
```
since this is a WIP, if you wish to use the code I would request that you fork it / branch it so that I can also see 
what direction to take the code.

The MIT License (MIT)

Copyright (c) 2023 James Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
