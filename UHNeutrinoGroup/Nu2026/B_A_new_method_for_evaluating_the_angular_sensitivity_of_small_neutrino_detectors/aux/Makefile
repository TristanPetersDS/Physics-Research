# usage: make clean
#	 make
PROJECT=main
SOURCES=$(*.tex sections/*.tex)
TEX=pdflatex
BIBTEX=bibtex
BUILDTEX=$(TEX) $(PROJECT).tex
BUILDDRAFT=$(TEX) "\def\draft{}\input{$(PROJECT).tex}"

all: $(PROJECT).pdf

$(PROJECT).pdf: $(SOURCES)

#all:
	$(BUILDTEX)
	$(BIBTEX) $(PROJECT)
	$(BUILDTEX)
	$(BUILDTEX)

draft:
	$(BUILDDRAFT)
	$(BIBTEX) $(PROJECT)
	$(BUILDDRAFT)
	$(BUILDDRAFT)

clean:
	/usr/bin/rm -f *.ps *.dvi *.aux *.log p.ps *backup *~ *.bbl *blg *.pdf *.toc
