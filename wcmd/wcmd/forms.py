from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.http import *
from wcmd.wcmd.models import *
import datetime
from django.contrib.admin import widgets
#from leaflet.forms.widgets import LeafletWidget
from taggit.forms import TagField, TagWidget
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row
from crispy_bootstrap5.bootstrap5 import FloatingField

#from django.utils.timezone import utc

#timenow = datetime.datetime.utcnow().replace(tzinfo=utc)
timenow = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

class AgencyForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AgencyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_tag = False
        #self.helper.form_action = reverse_lazy('your_post_url')
        self.helper.layout = Layout(
            Fieldset(
                '', #why?
                Row(
                    FloatingField("name", wrapper_class="col-8"),
                    FloatingField("sla", wrapper_class="col-4"),
                    css_id="three",
                    ),
                FloatingField("page_content", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
                FloatingField("remarks", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
            ),
            #Submit('submit', 'Submit', css_class='btn btn-primary'),
        )

    class Meta:
        model = Agency
        fields = ['name', 'sla', 'page_content', 'remarks']

class AgencyMeasuresForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AgencyMeasuresForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_tag = False
        #self.helper.form_action = reverse_lazy('your_post_url')
        self.helper.layout = Layout(
            Fieldset(
                '', #why?
                Row(
                    FloatingField("name", wrapper_class="col-8"),
                    FloatingField("sla", wrapper_class="col-4"),
                    css_id="three",
                    ),
                FloatingField("page_content", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
                FloatingField("remarks", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
            ),
            #Submit('submit', 'Submit', css_class='btn btn-primary'),
        )

    class Meta:
        model = Agency
        fields = ['name', 'sla', 'page_content', 'remarks']

class AgencyMeasureForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AgencyMeasureForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_tag = False
        #self.helper.form_action = reverse_lazy('your_post_url')
        self.helper.layout = Layout(
            Fieldset(
                '', #why?
                FloatingField("fullname"),
                FloatingField("name"),
                FloatingField("sortrank"),
                FloatingField("indicator"),
                FloatingField("question"),
                FloatingField("quality"),
                FloatingField("required"),
                FloatingField("reported_as"),
                FloatingField("units"),
                FloatingField("formula"),
                FloatingField("page_content", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
                FloatingField("remarks", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
            ),
            #Submit('submit', 'Submit', css_class='btn btn-primary'),
        )

    class Meta:
        model = Measure
        fields = ['agency', 'fullname', 'name', 'sortrank', 'indicator', 'question', 'quality', 'required', 'reported_as', 'units', 'formula', 'page_content', 'remarks']


class WildernessForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(WildernessForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_tag = False
        #self.helper.form_action = reverse_lazy('your_post_url')
        self.helper.layout = Layout(
            Fieldset(
                '', #why?
                FloatingField("name"),
                FloatingField("agency"),
                Row(
                    FloatingField("state", wrapper_class="col-4"),
                    FloatingField("designation_date", wrapper_class="col-4"),
                    FloatingField("acreage", wrapper_class="col-4"),
                    css_id="three",
                    ),
                FloatingField("tags"),
                FloatingField("comment", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
                FloatingField("description", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
                FloatingField("page_content", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
                FloatingField("remarks", autofocus="true", onfocus="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\"", oninput="this.style.height = \"\";this.style.height = this.scrollHeight + 3 + \"px\""),
            ),
            #Submit('submit', 'Submit', css_class='btn btn-primary'),
        )

    class Meta:
        model = Wilderness
        fields = ['name', 'designation_date', 'state', 'comment', 'acreage', 'description', 'agency', 'tags', 'page_content', 'remarks']
