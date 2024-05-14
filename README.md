# batchtk

batchtk is my (james.chen@downstate.edu) python package for handling custom remote job submissions
```
.
├── batchtk
│   ├── raytk <- integration with ray
│   │   ├── __init__.py
│   │   └── search.py
│   ├── runtk <- tools for custom job submission
│   │   ├── dispatchers.py
│   │   ├── header.py
│   │   ├── __init__.py
│   │   ├── runners.py
│   │   ├── sockets.py
│   │   ├── submits.py
│   │   └── utils.py
│   └── utils <- utilities used by rest of the package
│       ├── __init__.py
│       └── utils.py
├── examples
│   └── colab <- examples of package usage
│       ├── basic_runner.py
│       ├── batchtk0.ipynb
│       ├── batchtk1.ipynb
│       ├── batchtk2.ipynb
│       └── socket_runner.py
├── LICENSE.md
├── pyproject.toml
├── README.md
└── tests <- pytest checks
    ├── cleanup.zsh
    ├── runner_scripts
    │   └── socket_py.py
    ├── test_dispatcher.py
    ├── test_job.py
    ├── test_sh.py
    ├── test_socket.py
    └── test_submit.py

9 directories, 26 files
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
