#!/usr/bin/make -f
# SPDX-License-Identifier: AGPL-3.0-or-later

OUTPUTS=freedombox-manual.pdf plinth.1 manual-pages

MANUAL_LANGUAGES=en es

MANUAL_URL="https://wiki.debian.org/{lang-fragment}FreedomBox/Manual?action=show&mimetype=text%2Fdocbook"
MANUAL_URL_RAW="https://wiki.debian.org/{lang-fragment}FreedomBox/Manual?action=raw"
MANUAL_PAGE_URL="https://wiki.debian.org/{lang-fragment}FreedomBox/Manual/{page}?action=show&mimetype=text%2Fdocbook"

DESTDIR=
INSTALL_DIR=$(DESTDIR)/usr/share/freedombox
SCRIPTS_DIR=scripts

manual-pdfs=$(foreach lang,$(MANUAL_LANGUAGES),manual/$(lang)/freedombox-manual.pdf)
manual-xmls=$(patsubst %.pdf,%.xml,$(manual-pdfs))
OUTPUTS=$(manual-pdfs) plinth.1 manual-pages

INSTALL_OPTS=-D --mode=644

# In order to debug various problems with the documents especially
# intermediate LaTeX state, run make as follows:
#
#   $ make DEBUG=true
#   or
#   $ make DEBUG=true <target>
#
XMLTO_DEBUG_FLAGS=
ifneq ($(DEBUG),)
	XMLTO_DEBUG_FLAGS=--noclean -p '--debug'
endif

.PHONY: all install
all: $(OUTPUTS)

install: all
	for file in $(manual-pages-part-html) $(manual-pdfs); do \
		install $(INSTALL_OPTS) -t $(INSTALL_DIR)/$$(dirname $${file}) \
			$${file} ; \
	done
	for lang in $(MANUAL_LANGUAGES); do \
		install $(INSTALL_OPTS) manual/$${lang}/images/*.png \
			manual/$${lang}/images/*.jpg \
			-t $(INSTALL_DIR)/manual/$${lang}/images ; \
	done

# Do not edit the manual page in this directory.  The manual is
# maintained as separate pages on the FreedomBox wiki and aggregated
# into a single page using the MoinMoin include feature.  Then it is
# exported as Docbook format and kept here.
#
# It is important to keep a copy of the manual in this source tree
# because Debian packages promise an entire source tree including the
# documentation.
#
# Use 'make fetch' to retrieve the latest manual from the wiki and
# commit it to the repository.  The wiki page is already reviewed, so
# commits that update the manual just using the 'fetch' target do not
# require further reviews.
fetch-main-list:=$(foreach lang,$(MANUAL_LANGUAGES),fetch-main-$(lang))
fetch-pages-list:=$(foreach lang,$(MANUAL_LANGUAGES),fetch-pages-$(lang))

.PHONY: fetch $(fetch-main-list) $(fetch-pages-list)
fetch: $(fetch-main-list) $(fetch-pages-list)

fetch-main-%: lang = $*
fetch-main-%: lang-fragment = $(subst en/,,$*/)
$(fetch-main-list): fetch-main-%:
	MANUAL_URL_LANG=$(subst {lang-fragment},$(lang-fragment),$(MANUAL_URL)) ; \
	wget --quiet -O - $${MANUAL_URL_LANG} | \
	  xmllint --format --output manual/$(lang)/freedombox-manual.raw.xml -
	mkdir -p manual/$(lang)/images/
	xsltproc $(SCRIPTS_DIR)/fetch-images.xslt manual/$(lang)/freedombox-manual.raw.xml | \
	  sort -u | \
	  awk 'NF {print "wget --quiet -O manual/$(lang)/images/" $$1 " " $$2}' | \
	  sh

fetch-pages-%: lang = $*
fetch-pages-%: lang-fragment = $(subst en/,,$*/)
$(fetch-pages-list): fetch-pages-%:
	MANUAL_URL_LANG=$(subst {lang-fragment},$(lang-fragment),$(MANUAL_URL_RAW)) ; \
	MANUAL_PAGE_URL_LANG=$(subst {lang-fragment},$(lang-fragment),$(MANUAL_PAGE_URL)) ; \
	PAGES=$$(wget --quiet -U Firefox -O - $${MANUAL_URL_LANG} | \
	  sed -n -e "s|.*FreedomBox/Manual/\([a-zA-Z0-9_-]*\).*|\1|p" | sort -u | \
	  grep -v -e GettingHelp -e Developer -e QuickStart) ; \
	for PAGE in $${PAGES} ; do \
	  FILE="manual/$(lang)/$${PAGE}.raw.xml" ; \
	  URL=$$(echo $${MANUAL_PAGE_URL_LANG} | sed "s/{page}/$${PAGE}/") ; \
	  echo "Downloading $(lang) $${PAGE}" ; \
	  wget --quiet --user-agent=Firefox -O $${FILE} $${URL} ; \
	done

manual-pages-raw:=$(foreach lang,$(MANUAL_LANGUAGES),$(filter-out manual/%/freedombox-manual.raw.xml,$(wildcard manual/$(lang)/*.raw.xml)))
manual-pages-part-html:=$(patsubst %.raw.xml, %.part.html, $(manual-pages-raw)) $(foreach lang,$(MANUAL_LANGUAGES),manual/$(lang)/freedombox-manual.part.html)
manual-pages-html:=$(patsubst %.part.html, %.html, $(manual-pages-part-html))
manual-pages-xml:=$(patsubst %.raw.xml, %.xml, $(manual-pages-raw))

.PHONY: manual-pages
manual-pages: $(manual-pages-part-html)

$(manual-pdfs): %.pdf: %.xml
	xmlto $(XMLTO_DEBUG_FLAGS) --with-dblatex pdf -o $(dir $@) $<

$(manual-pages-part-html): %.part.html: %.html
	perl -pe 'BEGIN {undef $$/} s/.*<body[^>]*>(.*)<\/body\s*>.*/$$1/si' $< > $@

$(manual-xmls): %.xml: %.raw.xml $(SCRIPTS_DIR)/fixes.xslt
	xsltproc --output $@ $(SCRIPTS_DIR)/fixes.xslt $<

$(manual-pages-xml): %.xml: %.raw.xml $(SCRIPTS_DIR)/manual-page-fixes.xslt
	xsltproc --output $@ $(SCRIPTS_DIR)/manual-page-fixes.xslt $<
	$(SCRIPTS_DIR)/post-processor remove-footer $@
	$(SCRIPTS_DIR)/post-processor fix-wiki-urls $@

$(manual-pages-html): %.html: %.xml
	xsltproc --output $@ /usr/share/xml/docbook/stylesheet/docbook-xsl/xhtml5/docbook.xsl $<
	rm -f $(dir $@)docbook.css

%.1: %.xml
	xmlto man $<

.PHONY: clean
clean:
	rm -f $(manual-pages-html) $(manual-pages-part-html) $(manual-pages-xml) $(manual-xmls)
	rm -f $(OUTPUTS)
