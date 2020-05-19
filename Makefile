build: check-environment
	find . -size +50M | xargs -i% echo "WARNING: Not sending large file to Docker %"
	docker rmi s876cnsm:5000/${USER}-arxiv_extraction
	find . -size +50M > .dockerignore && \
		docker build -t s876cnsm:5000/${USER}-arxiv_extraction . \
		-f Dockerfile \
		--build-arg USER=${USER} \
		--build-arg USERID=${UID} \
		--build-arg "constraint:nodetype!=phi"
	docker push s876cnsm:5000/${USER}-arxiv_extraction

build-unsafe: check-environment
	rm -f .dockerignore && \
	docker build -t s876cnsm:5000/${USER}-arxiv_extraction . \
		-f Dockerfile \
		--build-arg USER=${USER} \
		--build-arg USERID=${UID} \
		--build-arg "constraint:node==s876gn02"
	docker push s876cnsm:5000/${USER}-arxiv_extraction
run:
	docker run --rm -ti \
		-c20 -m128g \
		--shm-size 128g \
		--name ${USER}-arxiv$(POSTFIX) \
		-v/rdata/s01c_a1_001:/rdata/ \
		-e "constraint:nodetype!=phi" \
		--tmpfs /ramdisk \
		s876cnsm:5000/${USER}-arxiv_extraction

check-environment:
	[ -z "${UID}" ] && { echo "UID not set, run 'export UID' "; exit 1; } || true
	[ -z "${USER}" ] && { echo "USER not set, run 'export USER' "; exit 1; } || true
