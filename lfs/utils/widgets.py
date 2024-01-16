from django.forms.widgets import Select


class SelectImage(Select):
    pass
    # def render(self, name, value, attrs=None, choices=(), renderer=None):
    #     if value is None:
    #         value = ""
    #     self.image_id = "image_%s" % attrs["id"]
    #     final_attrs = self.build_attrs(self.attrs, attrs)
    #     defaultimage = None
    #     for id, keys in self.choices:
    #         if str(id) == str(value):
    #             defaultimage = keys[2][1]

    #     # Try to pick first image as default image
    #     if defaultimage is None:
    #         if len(self.choices) > 0:
    #             defaultimage = self.choices[0][1][1][1]
    #     return render_to_string(
    #         "manage/widgets/selectimage.html",
    #         context={
    #             "selectimageid": self.image_id,
    #             "choices": self.choices,
    #             "currentvalue": value,
    #             "finalattrs": flatatt(final_attrs),
    #             "imageurl": defaultimage,
    #         },
    #     )
