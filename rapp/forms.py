from django import forms

class FichierForm(forms.Form):
	nom = forms.CharField(help_text="Specifier le nom du fichier")
	file = forms.FileField(help_text="Le fichier")