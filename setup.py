"""
Install tvb-nest and tvb-scripts packages.

Execute:
    python setup.py install/develop

"""

import shutil
import setuptools


VERSION = "0.1.0"

INSTALL_REQUIREMENTS = []

setuptools.setup(name='avatk',
                 version=VERSION,
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 install_requires=INSTALL_REQUIREMENTS,
                 description='A package for multiscale co-simulations with TVB and NEST, ANNarchy and NETPYNE (NEURON).',
                 license="GPL v3",
                 author="Dionysios Perdikis, André Blickensdörfer, Valeryi Bragin, Lia Domide, TVB Team",
                 author_email='tvb.admin@thevirtualbrain.org',
                 url='http://www.thevirtualbrain.org',
                 download_url='https://github.com/the-virtual-brain/tvb-multiscale',
                 keywords='tvb brain simulator nest neuroscience human animal neuronal dynamics builders delay')

shutil.rmtree('tvb_multiscale.egg-info', True)