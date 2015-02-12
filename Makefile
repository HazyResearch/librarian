# Makefile for DeepDive Librarian

# Using BuildKit (https://github.com/netj/buildkit)
PROJECTNAME := librarian
PACKAGEEXECUTES := bin/librarian

include buildkit/modules.mk
buildkit/modules.mk:
	git submodule update --init

