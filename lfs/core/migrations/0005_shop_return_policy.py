from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_alter_shop_image_alter_shop_meta_title_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="return_days",
            field=models.PositiveSmallIntegerField(
                default=14, help_text="Days to return a product; 0 means no returns.", verbose_name="Return days"
            ),
        ),
        migrations.AddField(
            model_name="shop",
            name="return_fees",
            field=models.CharField(
                choices=[("FreeReturn", "Free return"), ("ReturnFeesCustomerResponsibility", "Customer pays the return")],
                default="FreeReturn",
                max_length=40,
                verbose_name="Return fees",
            ),
        ),
        migrations.AddField(
            model_name="shop",
            name="return_method",
            field=models.CharField(
                choices=[("ReturnByMail", "By mail"), ("ReturnInStore", "In store")],
                default="ReturnByMail",
                max_length=40,
                verbose_name="Return method",
            ),
        ),
        migrations.AddField(
            model_name="shop",
            name="return_policy_url",
            field=models.CharField(
                blank=True,
                help_text="Path or URL of the page with the return policy, e.g. /page/widerrufsbelehrung/.",
                max_length=255,
                verbose_name="Return policy page",
            ),
        ),
    ]
