.PHONY: setup
setup:
	quarto add quarto-ext/shinylive

.PHONY: preview
preview:
	quarto preview index.qmd --port 54321

.PHONY: render
render:
	rm -rf docs
	quarto render index.qmd
	touch docs/.nojekyll
