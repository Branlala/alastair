from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from crispy_forms.bootstrap import FormActions, AppendedText, StrictButton,  InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, Field, Hidden, HTML, Div

class MyLoginForm(AuthenticationForm):
	
	def __init__(self, *args, **kwargs):
		super(MyLoginForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-6'
		self.helper.layout = Layout(
			'username',
			Field('password'),
			FormActions(Submit('login', 'Login', css_class='btn btn_success')),
			)
			
class MyPasswordChangeForm(PasswordChangeForm):
	
	def __init__(self, *args, **kwargs):
		super(MyPasswordChangeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-6'
		self.helper.layout = Layout(
			'old_password',
			'new_password1',
			'new_password2',
			FormActions(Submit('save', 'Save', css_class='btn btn_success')),
			)
			