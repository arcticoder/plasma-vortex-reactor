# Minimal Makefile to build the phase3_stability paper

TEX=phase3_stability.tex
PDF=$(TEX:.tex=.pdf)

all: $(PDF)

$(PDF): $(TEX)
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(TEX) || \
	pdflatex -interaction=nonstopmode $(TEX) || \
	xelatex -interaction=nonstopmode $(TEX)

clean:
	latexmk -C || true
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.fls *.fdb_latexmk

.PHONY: all clean
