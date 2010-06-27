# contact_form imports
from contact_form.forms import ContactForm as BaseContactForm

#lfs imports
import lfs.core.utils

class ContactForm(BaseContactForm):
    """Specific ContactForm for LFS.
    """
    def __init__(self, data=None, files=None, request=None, *args, **kwargs):
        super(ContactForm, self).__init__(data=data, files=files, request=request, *args, **kwargs)
        self.shop = lfs.core.utils.get_default_shop()
        
    def from_email(self):
        return self.shop.from_email

    def recipient_list(self):
        return self.shop.get_notification_emails()