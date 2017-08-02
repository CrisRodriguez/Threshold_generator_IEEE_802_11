# Threshold_generator_IEEE_802_11
The files in the respository are an extension to the IEEE 802.11a/g/p introduced by Bastian Bloessl. In this work, a fuzzy system is proposed in order to stablish the processing threshold in the physical layer of IEEE 802.11a/g/p.

# Files
The files are organized in folders that corresponds to the ones that they must be put when it is implemented with the IEEE 802.11a/g/p transceiver.

# Inclusion
As a first step, each one of the files must be put in the folders that they belong to. In most cases they have the same names, just in the flowgraphs and application codes, they must be put in examples and apps, respectivly.

Later, the C++ blocks must be declared in the CMakeLists and in the Siwg list, as well as the python files in the init_.py file.

# Dependences

The thereshold generator block uses the pylab library of Python, which is not usually installed in most systems, so if you aren't sure about having it in your operative system, please run the installation. It can by done by way of installing all the necessary dependences as indicated in https://www.scipy.org/install.html.

