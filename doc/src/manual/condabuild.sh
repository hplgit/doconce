#!/bin/bash
# Build doconce for conda

packages="
pbr
sphinxjp.themecore
cloud_sptheme
cogapp
mako
paver
pdftools
preprocess
ptex2tex
publish
sphinx-bootstrap-theme
sphinx-sagecell
sphinxcontrib-paverutils
sphinxjp.themes.solarized
sphinxjp.themes.impressjs
pypdf2
doconce
"

for p in $packages; do
echo $p
conda build $p
if [ $? -ne 0 ]; then
  echo "conda failed: $p"
  exit 1
fi
done

# Upload to binstar?
#conda config --set binstar_upload yes