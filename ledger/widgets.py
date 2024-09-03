"""
HTML Widget classes
"""

from __future__ import unicode_literals
import copy
import json
from django.forms.utils import flatatt, to_current_timezone
from django.utils.html import conditional_escape, format_html, html_safe
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
from django.forms import Media, MediaDefiningClass, Widget, CheckboxInput
from django.utils.safestring import SafeText
# from ledger.validationchecks import is_json

from django.utils.encoding import (
    #   force_str, force_text, python_2_unicode_compatible,
      force_str, force_text,
)

__all__ = (
    'ClearableMultipleFileInput', 'FileInput', 'RendererMixin', 'ChoiceFieldRenderer' 
)

MEDIA_TYPES = ('css', 'js')

class InputMultiFile(Widget):
    """
    Base class for all <input> widgets (except type='checkbox' and
    type='radio', which are special).
    """
    input_type = None  # Subclasses must define this.
    def format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
#        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name, )
        final_attrs = self.build_attrs(self.attrs, attrs)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self.format_value(value))
        return format_html('<input{} >', flatatt(final_attrs))

class FileInput(InputMultiFile):
    input_type = 'file'
    needs_multipart_form = True
    def render(self, name, value, attrs=None):
        return super(FileInput, self).render(name, None, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        "File widgets take data from FILES, not POST"
        return files.get(name)

    def value_omitted_from_data(self, data, files, name):
        return name not in files

class AjaxFileUploader(FileInput):
    initial_text = ugettext_lazy('Currently testing')
    input_text = ugettext_lazy('Change')
    clear_checkbox_label = ugettext_lazy('Clear')

    template_with_initial = (
        '%(initial_text)s: <a href="%(initial_url)s">%(initial)s</a>'
        '%(clear_template)s<br />%(input_text)s: %(input)s %(ajax_uploader)s'
    )

    template_with_clear = '%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'
   
    def clear_checkbox_name(self, name):
        """
        Given the name of the file input, return the name of the clear checkbox
        input.
        """
        return name + '-clear'

    def clear_checkbox_id(self, name):
        """
        Given the name of the clear checkbox input, return the HTML id for it.
        """
        return name + '_id'

    def is_initial(self, value):
        """
        Return whether value is considered to be initial value.
        """
        return bool(value and getattr(value, 'url', False))

    def get_template_substitution_values(self, value):
        """
        Return value-related substitutions.
        """
        #return {
        #    'initial': conditional_escape(value),
        #    'initial_url': conditional_escape(value.url),
        #}


    def render(self, name, value, attrs=None):

        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }

        #if 'multiple' in attrs:
        #final_attrs = self.build_attrs(attrs, type=self.input_type, name=name,)
        final_attrs = self.build_attrs(self.attrs, attrs)
        upload_type = 'single'

        if 'multiple' in final_attrs:
            upload_type = 'multiple'
        
        template = '%(ajax_uploader)s %(clearfiles)s'
        substitutions['input'] = super(AjaxFileUploader, self).render(name, value, attrs)

#        substitutions['ajax_uploader'] = '<button type="button" class="btn btn-primary" onclick="ajax_loader_django.openUploader(\''+name+'\',\''+upload_type+'\');" >Upload Files</button><br>'
#        substitutions['ajax_uploader'] += '<TEXTAREA name="'+name+'_json" id="'+name+'_json"></TEXTAREA>'
#        substitutions['clearfiles'] = ''

        value1 = {} 
        if type(value) is list:
           substitutions['clearfiles'] = "<div class='col-sm-12'><Label>Files:</Label></div>"

           if value:
              for fi in value:
                  if fi:
                      fi['short_name'] =SafeText(fi['path'])[19:]
                      fi['doc_id'] = fi['fileid']
                      fi['extension'] = fi['extension']
                      substitutions['clearfiles'] += "<div class='col-sm-8'><A HREF='/media/"+fi['path']+"'>"
                      if fi['name']:
                         substitutions['clearfiles'] += SafeText(fi['name'])
                      else:
                         substitutions['clearfiles'] += SafeText(fi['path'])[19:]

                      substitutions['clearfiles'] += "</A></div>"
                      substitutions['clearfiles'] += "<div class='col-sm-4'><input type='checkbox' "
                      substitutions['clearfiles'] += " name='"+name+"-clear_multifileid-"+str(fi['fileid'])+"'"
                      substitutions['clearfiles'] += " id='"+name+"-clear_multifileid-"+str(fi['fileid'])+"'"
                      substitutions['clearfiles'] += " > Clear</div>"

        else:
           if value is None:
             value1 =  '' 
           else:

               value1['short_name'] = SafeText(value.upload.name)[19:]
               value1['path'] = value.upload.name
               value1['name'] = value.name
               value1['doc_id'] = value.id
               value1['extension'] = value.extension
           value = value1 

        
        substitutions['ajax_uploader'] = '<button type="button" class="btn btn-primary" onclick="ajax_loader_django.openUploader(\''+name+'\',\''+upload_type+'\');" >Upload Files</button><br>'
        substitutions['ajax_uploader'] += '<TEXTAREA name="'+name+'_json" id="'+name+'_json" style="display:none">'
        if value == '':
           donothing = ''
        else:
           substitutions['ajax_uploader'] += json.dumps(value)
        substitutions['ajax_uploader'] += '</TEXTAREA>'

        #substitutions['ajax_uploader'] += '<TEXTAREA name="'+name+'" id="'+name+'" style="display:none">'
        #if value == '':
        #   donothing = ''
        #else:
        #   substitutions['ajax_uploader'] += json.dumps(value)
        #substitutions['ajax_uploader'] += '</TEXTAREA>'

        substitutions['ajax_uploader'] += '<div id="'+name+'__uploader" ></div>'
        substitutions['ajax_uploader'] += '<div id="'+name+'__showfiles" class="showfiles"><BR>'
        if value == '':
           donothing = ''
        else:
           if type(value) is list:
              count = 1
           
              for fi in value:
                 if 'short_name' in fi:
#                    substitutions['ajax_uploader'] += '<div class="col-xs-12 col-sm-12 col-md-12 col-lg-12">'
#                    substitutions['ajax_uploader'] += '</div>';
#                    substitutions['ajax_uploader'] += '<li>'+str(count)+'. <A HREF="/media/'+fi['path']+'">'+fi['short_name']+'</A>  <a onclick="ajax_loader_django.deleteFile(\'river_lease_scan_of_application\',\''+str(fi['doc_id'])+'\',\''+str(upload_type)+'\')" href="javascript:void(0);">X</a> </li>'

                     substitutions['ajax_uploader'] += '<div class="col-xs-12 col-sm-12 col-md-12 col-lg-12">'
                     substitutions['ajax_uploader'] += '<div class="col-xs-9 col-sm-9 col-md-9 col-lg-9">'
                     #substitutions['ajax_uploader'] += str(count)+'. <A HREF="/media/'+fi['path']+'">'
                     substitutions['ajax_uploader'] += str(count)+'. <A HREF="/private-media/view/'+str(fi['doc_id'])+'-file'+str(fi['extension'])+'" target="new_tab_'+str(fi['doc_id'])+'">'

                     if 'name' in fi:
                           substitutions['ajax_uploader'] += fi['name']
                     else:
                           substitutions['ajax_uploader'] += fi['short_name']

                     substitutions['ajax_uploader'] += '</A>'
                     substitutions['ajax_uploader'] += '</div>'
                     substitutions['ajax_uploader'] += '<div class="col-xs-3 col-sm-3 col-md-3 col-lg-3">';
                     substitutions['ajax_uploader'] += '<A onclick="ajax_loader_django.deleteFile(\''+name+'\',\''+str(fi['doc_id'])+'\',\''+upload_type+'\')" href="javascript:void(0);"><span class="glyphicon glyphicon-remove" aria-hidden="true" style="color: red"></span></A>'
                     substitutions['ajax_uploader'] += '</div>'
                     substitutions['ajax_uploader'] += '</div>'

                     count = count + 1
           else:
                 if 'short_name' in value:
                     #substitutions['ajax_uploader'] += '<li>1. <A HREF="/media/'+value['path']+'">'+value['short_name']+'</A></li>'

                     substitutions['ajax_uploader'] += '<div class="col-xs-9 col-sm-9 col-md-9 col-lg-9">'
                     #substitutions['ajax_uploader'] += '<A HREF="/media/'+value['path']+'">'
                     substitutions['ajax_uploader'] += '<A HREF="/private-media/view/'+str(value['doc_id'])+'-file'+str(value['extension'])+'"  target="new_tab_'+str(value['doc_id'])+'">'
                    
                     if 'name' in value:
                         substitutions['ajax_uploader'] += value['name']
                     else:
                         substitutions['ajax_uploader'] += value['short_name']

 
                     substitutions['ajax_uploader'] += '</A>'
                     substitutions['ajax_uploader'] += '</div>';
                     substitutions['ajax_uploader'] += '<div class="col-xs-3 col-sm-3 col-md-3 col-lg-3">'
                     substitutions['ajax_uploader'] += '<A onclick="ajax_loader_django.deleteFile(\''+name+'\',\''+str(value['doc_id'])+'\',\''+upload_type+'\')" href="javascript:void(0);"><span class="glyphicon glyphicon-remove" aria-hidden="true" style="color: red"></span></A>'
                     substitutions['ajax_uploader'] += '</div>'
                  
           #substitutions['ajax_uploader'] += '<li>1. <A HREF="">File 1</A></li>'
           #substitutions['ajax_uploader'] += '<li>2. <A HREF="">File 2</A></li>'
        substitutions['ajax_uploader'] += '</div>'
        substitutions['clearfiles'] = ''

         
        if self.is_initial(value):
            template = self.template_with_initial
            substitutions.update(self.get_template_substitution_values(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions
        return mark_safe(template % substitutions)

    def value_from_datadict(self, data, files, name):
        upload = super(AjaxFileUploader, self).value_from_datadict(data, files, name)
        if not self.is_required and CheckboxInput().value_from_datadict(
                data, files, self.clear_checkbox_name(name)):

            if upload:
                # If the user contradicts themselves (uploads a new file AND
                # checks the "clear" checkbox), we return a unique marker
                # object that FileField will turn into a ValidationError.
                return FILE_INPUT_CONTRADICTION
            # False signals to clear any existing value, as opposed to just None
            return False
        return upload

    def use_required_attribute(self, initial):
        return super(AjaxFileUploader, self).use_required_attribute(initial) and not initial

    def value_omitted_from_data(self, data, files, name):
        return (
            super(AjaxFileUploader, self).value_omitted_from_data(data, files, name) and
            self.clear_checkbox_name(name) not in data
        )

