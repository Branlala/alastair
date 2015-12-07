from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Button, Field, Hidden, HTML, Div
from crispy_forms.bootstrap import FormActions, AppendedText, StrictButton,  InlineField
from cooking.models import Project, Meal, Meal_Receipe, Inventory_Item

class ConfirmDeleteForm(forms.Form):

	def __init__(self, *args, **kwargs):
		super(ConfirmDeleteForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_class = 'form-inline'
		self.helper.field_template = 'bootstrap3/layout/inline_field.html'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.layout = Layout(
			HTML('<input type="hidden" name="object_id" value="{% firstof object.id objectid %}" />'),
			FormActions(
				Submit('save', 'Yes', css_class='btn btn_success'),
				HTML('<a href="{{ noaction }}" class="btn btn-default">No</a>')
				),
			)
		