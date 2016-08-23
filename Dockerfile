FROM ubuntu:16.04

RUN apt-get -qq update &&\
    apt-get install -qy sudo

ADD . /doconce
WORKDIR /doconce
RUN ./doc/src/manual/install_doconce.sh &&\
    # make sure this git version is installed and not the one from the script
    python setup.py install &&\
    # reduce space in the image
    rm -rf srclib &&\
    apt-get remove --purge -qy libreoffice libreoffice-dmaths kdiff3 totem evince 
