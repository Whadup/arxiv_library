FROM ubuntu
SHELL ["/bin/bash", "-c"]
#ARG USER="schill"
#ARG USERID=8216
ARG USER="pfahler"
ARG USERID=8194
ARG GROUPID=9004
ARG GROUPNAME="s876a1"
# Switch to root, otherwise the permissions to create a new user are missing.
USER "root" 

RUN apt-get update
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin
RUN apt-get install -y \
	curl \
	bzip2 \
	psmisc \
	nano \
	git \
	openssh-client

ENV MINICONDA_VERSION 4.7.10
ENV MINICONDA_MD5 1c945f2b3335c7b2b15130b1b2dc5cf4

# RUN curl -s https://repo.continuum.io/archive/Anaconda3-$ANACONDA_VERSION-Linux-x86_64.sh -o anaconda.sh && \
# 	echo "${ANACONDA_MD5}  anaconda.sh" > anaconda.md5 && \
# 	if [ $(md5sum -c anaconda.md5 | awk '{print $2}') != "OK" ] ; then exit 1; fi && \
# 	mkdir -p /opt && \
# 	sh ./anaconda.sh -b -p /opt/conda && \
# 	rm anaconda.sh anaconda.md5

RUN curl -s https://repo.anaconda.com/miniconda/Miniconda3-$MINICONDA_VERSION-Linux-x86_64.sh -o anaconda.sh && \
	echo "${MINICONDA_MD5}  anaconda.sh" > anaconda.md5 && \
	if [ $(md5sum -c anaconda.md5 | awk '{print $2}') != "OK" ] ; then exit 1; fi && \
	mkdir -p /opt && \
	sh ./anaconda.sh -b -p /opt/conda && \
	rm anaconda.sh anaconda.md5

ENV CONDA_DIR /opt/conda
ENV PATH $CONDA_DIR/bin:$PATH

COPY environment.yml .
RUN source $CONDA_DIR/bin/activate && conda env create -f environment.yml && rm environment.yml


RUN apt-get install -y npm
RUN npm install -g yargs mathjax-node mathjax-node-sre katex
COPY arxiv_library/compilation/js/katex.js /usr/local/lib/node_modules/katex/dist/
ENV NODE_PATH "/usr/local/lib/node_modules"

# Create a new user.
RUN mkdir -p "/home/${USER}" && \
	echo "${USER}:x:${USERID}:${GROUPID}:${USER}:/home/${USER}:/bin/bash" >> /etc/passwd && \
	echo "${GROUPNAME}:x:${GROUPID}:${USER}" >> /etc/group                               && \
	chown -R "${USERID}:${GROUPID}" "/home/${USER}"

WORKDIR "/home/${USER}"
RUN mkdir arxiv_library
COPY . arxiv_library/
RUN chown -R "${USER}" arxiv
USER "${USER}"
RUN echo "source $CONDA_DIR/bin/activate" >> ~/.bashrc
RUN echo "conda activate arxiv" >> ~/.bashrc

# RUN cd mathjax-node-cli && 
WORKDIR "/home/${USER}/arxiv_library"
CMD ["bash"]
