===== Note: Sphinx themes must match Sphinx versions =====

New versions of Sphinx will sometimes make use of newer versions of
JavaScript files like `jquery.js`. In `sphinx_themes` we therefore
avoid including standard themes that come with Sphinx, such that these
are available as part of Sphinx and hence compatible with the software.
Most of the other themes build on basic themes. For example, `jquery.js`
is only contained in the `basic` and `bootstrap` themes (`basic` is
part of Sphinx, while `bootstrap` must be updated via
`pip install`. Other themes that rely on a `pip install` include `cloud`, `redcloud`, `impressjs`, `solarized`, `sphinx_rtd_theme`.

!bc sys
sudo pip install -e hg+https://bitbucket.org/ecollins/cloud_sptheme#egg=cloud_sptheme --upgrade
sudo pip install -e git+https://github.com/ryan-roemer/sphinx-bootstrap-theme#egg=sphinx-bootstrap-theme --upgrade
sudo pip install -e hg+https://bitbucket.org/miiton/sphinxjp.themes.solarized#egg=sphinxjp.themes.solarized --upgrade
sudo pip install -e git+https://github.com/shkumagai/sphinxjp.themes.impressjs#egg=sphinxjp.themes.impressjs --upgrade
sudo pip install -e git+https://github.com/kriskda/sphinx-sagecell#egg=sphinx-sagecell --upgrade
sudo pip install sphinx_rtd_theme --upgrade
!ec
