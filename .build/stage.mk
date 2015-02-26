# Make rules for staging products of every module
# Generated: 2015-02-25T11:55:11-08:00

# depends
$(STAGED): $(STAGEDIR)/depends/bundled
$(STAGEDIR)/depends/bundled: depends/.build/bundled $(STAGEDIR)/depends/
	mkdir -p $@
	rsync -aH --copy-unsafe-links $</. $@/
# XXX always copying since Make doesn't know if files are changed inside a directory or not
.PHONY: $(STAGEDIR)/depends/bundled
$(STAGED): $(STAGEDIR)/depends/runtime
$(STAGEDIR)/depends/runtime: depends/.build/runtime $(STAGEDIR)/depends/
	mkdir -p $@
	rsync -aH --copy-unsafe-links $</. $@/
# XXX always copying since Make doesn't know if files are changed inside a directory or not
.PHONY: $(STAGEDIR)/depends/runtime
$(STAGED): $(STAGEDIR)/depends/check-runtime-depends-once
$(STAGEDIR)/depends/check-runtime-depends-once: depends/check-runtime-depends-once $(STAGEDIR)/depends/
	cp -f $< $@

# librarian
$(STAGED): $(STAGEDIR)/bin/librarian.d/librarian-publish
$(STAGEDIR)/bin/librarian.d/librarian-publish: librarian/librarian-publish $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/librarian-project
$(STAGEDIR)/bin/librarian.d/librarian-project: librarian/librarian-project $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/storage_s3.py
$(STAGEDIR)/bin/librarian.d/storage_s3.py: librarian/storage_s3.py $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/database_sheetsdb.py
$(STAGEDIR)/bin/librarian.d/database_sheetsdb.py: librarian/database_sheetsdb.py $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/sheetsdb
$(STAGEDIR)/bin/librarian.d/sheetsdb: librarian/sheetsdb $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@

# shell
$(STAGED): $(STAGEDIR)/bin/librarian
$(STAGEDIR)/bin/librarian: shell/librarian $(STAGEDIR)/bin/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/librarian-hack
$(STAGEDIR)/bin/librarian.d/librarian-hack: shell/librarian-hack $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/librarian-version
$(STAGEDIR)/bin/librarian.d/librarian-version: shell/librarian-version $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/error
$(STAGEDIR)/bin/librarian.d/error: shell/error $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/usage
$(STAGEDIR)/bin/librarian.d/usage: shell/usage $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/msg
$(STAGEDIR)/bin/librarian.d/msg: shell/msg $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/be-quiet
$(STAGEDIR)/bin/librarian.d/be-quiet: shell/be-quiet $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@
$(STAGED): $(STAGEDIR)/bin/librarian.d/verbosity-isnt
$(STAGEDIR)/bin/librarian.d/verbosity-isnt: shell/verbosity-isnt $(STAGEDIR)/bin/librarian.d/
	cp -f $< $@

# Directories
$(STAGEDIR)/depends/:
	mkdir -p $@
$(STAGEDIR)/bin/librarian.d/:
	mkdir -p $@
$(STAGEDIR)/bin/:
	mkdir -p $@
$(STAGED):
	@! [ -e $(STAGEIGNORE) -a ! -L $(BUILDDIR)/stage.ignore ] || relsymlink $(STAGEIGNORE) $(BUILDDIR)/stage.ignore
	@STAGEDIR=$(STAGEDIR) BUILDDIR=$(BUILDDIR) \
remove-stale-files
#	@touch $@
	### BuildKit: staged all modules
