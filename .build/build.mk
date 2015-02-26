# Make rules for building every module
# Generated: 2015-02-25T11:55:09-08:00

# depends
build: $(BUILDDIR)/timestamp/depends.built
$(BUILDDIR)/timestamp/depends.built: $(BUILDDIR)/timestamp/depends.lastmodified $(DEPENDS)
	cd depends && ./.module.build depends
	@mkdir -p '$(@D)' && touch '$@'

# librarian
#  (no executable .module.build)

# shell
#  (no executable .module.build)

$(BUILDDIR)/timestamp/%.lastmodified:
	@BUILDDIR=$(BUILDDIR) create-modules-lastmodified '$*'
