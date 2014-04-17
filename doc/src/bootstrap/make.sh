dir=tmp
rm -rf $dir
mkdir $dir
cp bootstrap_demo.do.txt $dir
cd $dir
darkpygm='monokai'
#darkpygm='fruity'  # suboptimal
#darkpygm='native'  # not good

doconce format html bootstrap_demo --html_style=bootstrap --pygments_html_style=default --html_admon=bootstrap_panel --html_output=bootstrap_plain
doconce split_html bootstrap_plain

doconce format html bootstrap_demo --html_style=bootstrap --pygments_html_style=default --html_admon=bootstrap_panel --html_output=bootstrap_FlatUI --html_code_style=inherit --bootstrap_FlatUI

doconce format html bootstrap_demo --html_style=bootstrap_bloodish --pygments_html_style=default --html_admon=bootstrap_panel --html_output=bootstrap_bloodish --html_code_style=inherit

links=
links1=
styles="cerulean cosmo flatly journal lumen readable simplex spacelab united yeti"
for style in $styles; do
doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=default --html_admon=bootstrap_alert --html_output=${style}_v1 --html_code_style=inherit
links1="$links1 <a href=\"${style}_v1.html\" target=\"_blank\">${style}_v1</a>"

doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=default --html_admon=bootstrap_panel --html_output=$style --html_code_style=inherit
links="$links <a href=\"${style}.html\" target=\"_blank\">${style}</a>"
done

# Dark styles
styles="amelia cyborg darkly slate superhero"
for style in $styles; do
doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=$darkpygm --html_admon=bootstrap_alert --html_output=${style}_v1 --keep_pygments_html_bg --html_code_style=inherit --html_pre_style=inherit
links1="$links1 <a href=\"${style}_v1.html\" target=\"_blank\">${style}_v1</a>"

doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=$darkpygm --html_admon=bootstrap_panel --html_output=$style --keep_pygments_html_bg --html_code_style=inherit --html_pre_style=inherit
links="$links <a href=\"${style}.html\" target=\"_blank\">${style}</a>"
done

cat > index.html <<EOF
<title>Demonstration of Boostrap styles for Doconce documents</title>
<h1>Demonstration of Boostrap styles for Doconce documents</h1>
Click to see Bootstrap/Bootswatch demos:<br>
<a href="bootstrap_plain.html" target="_blank">Plain bootstrap</a>:
<pre>
doconce format html bootstrap_demo --html_style=bootstrap
        --pygments_html_style=default --html_admon=bootstrap_panel
        --html_output=bootstrap_plain
doconce split_html bootstrap_plain
</pre>

The style above, but added
<a href="bootstrap_FlatUI.html" target="_blank">Flat UI</a>:
<pre>
doconce format html bootstrap_demo --html_style=bootstrap
        --pygments_html_style=default --html_admon=bootstrap_panel
        --html_output=bootstrap_FlatUI --html_code_style=inherit
        --bootstrap_FlatUI
</pre>
<a href="bootstrap_bloodish.html" target="_blank">bloodish</a>
<br>
Bootswatch styles (admons as panels first):
$links
<pre>
doconce format html bootstrap_demo --html_style=bootswatch_spacelab
        --pygments_html_style=default --html_admon=bootstrap_panel
        --html_output=spacelab --html_code_style=inherit
</pre>
For dark styles we add <tt>--html_pre_style=inherit --keep_pygments_html_bg</tt> as options to avoid white background:
<pre>
doconce format html bootstrap_demo --html_style=bootswatch_cyborg
        --pygments_html_style=monokai --html_admon=bootstrap_panel
        --html_output=cyborg --keep_pygments_html_bg
        --html_code_style=inherit --html_pre_style=inherit
</pre>
<br>
Admons as alerts:
$links1
EOF

cp *.html .*.html ../../../pub/bootstrap
