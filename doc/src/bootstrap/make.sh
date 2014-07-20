dir=tmp
rm -rf $dir
mkdir $dir
cp bootstrap_demo.do.txt index.do.txt template_*.html $dir
cd $dir
darkpygm='monokai'
#darkpygm='fruity'  # suboptimal
#darkpygm='native'  # not good

doconce format html bootstrap_demo --html_style=bootstrap --pygments_html_style=default --html_admon=bootstrap_panel --html_output=bootstrap_plain
doconce split_html bootstrap_plain --pagination

styles="bloodish blue bluegray brown red FlatUI bootflat"
for style in $styles; do
doconce format html bootstrap_demo --html_style=bootstrap_$style --pygments_html_style=default --html_admon=bootstrap_panel --html_output=bootstrap_$style --html_code_style=inherit
done

styles="cerulean cosmo flatly journal lumen readable simplex spacelab united yeti"
for style in $styles; do
doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=default --html_admon=bootstrap_alert --html_output=${style}_v1 --html_code_style=inherit

doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=default --html_admon=bootstrap_panel --html_output=$style --html_code_style=inherit
done

style=vagrant
doconce format html bootstrap_demo --html_style=$style --html_template=template_$style.html --pygments_html_style=default --html_admon=bootstrap_panel --html_output=$style --html_code_style=inherit

style=bootstrap_wtoc
doconce format html bootstrap_demo --html_style=bootstrap --html_template=../../../../bundled/html_styles/style_bootstrap_wtoc/template_$style.html --html_toc_depth=8 --html_admon=bootstrap_panel --html_output=$style --html_code_style=inherit

# Dark styles
styles="amelia cyborg darkly slate superhero"
for style in $styles; do
doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=$darkpygm --html_admon=bootstrap_alert --html_output=${style}_v1 --keep_pygments_html_bg --html_code_style=inherit --html_pre_style=inherit

doconce format html bootstrap_demo --html_style=bootswatch_$style --pygments_html_style=$darkpygm --html_admon=bootstrap_panel --html_output=$style --keep_pygments_html_bg --html_code_style=inherit --html_pre_style=inherit
done

# CBC style (demonstrates also how to insert a banner and footer image)
# needs custom editing and adding of code
doconce format html bootstrap_demo --html_style=bootstrap_cbc --pygments_html_style=default --html_admon=bootstrap_panel --html_output=cbc --keep_pygments_html_bg --html_code_style=inherit --html_pre_style=inherit
doconce replace ' navbar-fixed-top' '' cbc.html
doconce subst '<!-- Bootstrap navigation bar -->' '<div class="masthead">\n<div class="container">\n<a href="http://cbc.simula.no"><img src="http://cbc.simula.no/styles/stylefigs/CBClogoweb334x72.gif"></a>\n</div>\n</div>\n' cbc.html
doconce subst -s '<!-- Bootstrap footer.+?-->' '<footer><a href="http://simula.no"><img width="250" align=right src="http://cbc.simula.no/pub/figs/simula_logo_pos.png"></a></footer>' cbc.html

# index.html file with links to all the demos
doconce format html index --html_style=bootswatch_spacelab --pygments_html_style=none --html_links_in_new_window

cp *.html .*.html ../../../pub/bootstrap
