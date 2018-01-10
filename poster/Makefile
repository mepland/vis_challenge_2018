DOCNAME = vis_challenge_2018_poster-matthew_epland

TEXENG = lualatex
TEXFLAGS = --file-line-error # --shell-escape

BIBENG = bibtex
BIBFLAGS =

.PHONY: all clean cleanpdf cleanall info open help

all:
	$(info $(TEXENG) $(TEXFLAGS) $(DOCNAME))
	$(TEXENG) $(TEXFLAGS) $(DOCNAME)
	$(BIBENG) $(BIBFLAGS) $(DOCNAME)
	$(TEXENG) $(TEXFLAGS) $(DOCNAME)
	$(TEXENG) $(TEXFLAGS) $(DOCNAME)

clean:
	-@rm -f *.log
	-@rm -f *.aux
	-@rm -f *.1
	-@rm -f *.t1
	-@rm -f *.mp
	-@rm -f *.vrb
	-@rm -f $(DOCNAME)Notes.bib
	-@rm -f $(DOCNAME).bbl
	-@rm -f $(DOCNAME).toc
	-@rm -f $(DOCNAME).out
	-@rm -f $(DOCNAME).blg
	-@rm -f $(DOCNAME).nav
	-@rm -f $(DOCNAME).snm

cleanpdf:
	-@rm -f $(DOCNAME).pdf

cleanall: clean cleanpdf

info:
	$(info DOCNAME = $(DOCNAME))
	$(info TEXENG = $(TEXENG))
	$(info TEXFLAGS = $(TEXFLAGS))
	$(info BIBENG = $(BIBENG))
	$(info BIBFLAGS = $(BIBFLAGS))

open:
	-@evince $(DOCNAME).pdf </dev/null &>/dev/null &

help:
	@echo ""
	@echo "make          to make output PDF"
	@echo "make clean    to clean auxiliary files (not output PDF)"
	@echo "make cleanpdf to clean output PDF file"
	@echo "make cleanall to clean all files"
	@echo "make open     to open output PDF"
	@echo "make info     to view Makefile settings"
	@echo ""

