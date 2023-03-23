import gettext

# Load the English translations
translations = gettext.translation('app', localedir="locales", languages=['ar'])
translations.install()
_ = translations.gettext
print(_("list_of_interfaces"))