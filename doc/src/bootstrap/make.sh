dir=tmp
rm -rf $dir
mkdir $dir
cp bootstrap_demo.do.txt $dir
cd $dir
darkpygm='monokai'

doconce format html bootstrap_demo --html_style=bootstrap --pygments_html_style=default --html_admon=bootstrap_panel --html_output=plain_bootstrap
doconce split_html plain_bootstrap

doconce format html bootstrap_demo --html_style=bootstrap --pygments_html_style=default --html_admon=bootstrap_panel --html_output=FlatUI_bootstrap --bootstrap_code=off --bootstrap_FlatUI

links=
links1=
styles="cerulean cosmo flatly journal lumen readable simplex spacelab united yeti"
for style in $styles; do
doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=default --html_admon=bootstrap_alert --html_output=${style}_v1 --bootstrap_code=off
links1="$links1 <a href=\"${style}_v1.html\" target=\"_blank\">${style}_v1</a>"

doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=default --html_admon=bootstrap_panel --html_output=$style --bootstrap_code=off
links="$links <a href=\"${style}.html\" target=\"_blank\">${style}</a>"
done

styles="amelia cyborg darkly slate superhero"
for style in $styles; do
doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=$darkpygm --html_admon=bootstrap_alert --html_output=${style}_v1 --keep_pygments_html_bg --bootstrap_code=off
links1="$links1 <a href=\"${style}_v1.html\" target=\"_blank\">${style}_v1</a>"

doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=$darkpygm --html_admon=bootstrap_panel --html_output=$style --keep_pygments_html_bg --bootstrap_code=off
links="$links <a href=\"${style}.html\" target=\"_blank\">${style}</a>"
done

cat > index.html <<EOF
<title>Demonstration of Boostrap styles for Doconce documents</title>
<h1>Demonstration of Boostrap styles for Doconce documents</h1>
Click to see Bootstrap/Bootswatch demos:<br>
<a href="plain_bootstrap.html" target="_blank">plain bootstrap</a>
<a href="FlatUI_bootstrap.html" target="_blank">Flat UI</a><br>
Bootswatch styles (admons as panels first):
$links
<br>
Admons as alerts:
$links1
EOF

cp *.html .*.html ../../../pub/bootstrap
