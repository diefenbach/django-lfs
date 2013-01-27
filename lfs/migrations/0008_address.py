# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db import connection
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from lfs.addresses.models import Address
from lfs.catalog.models import DeliveryTime
from lfs.criteria.models import CartPriceCriterion
from lfs.criteria.models import CombinedLengthAndGirthCriterion
from lfs.criteria.models import CountryCriterion
from lfs.criteria.models import HeightCriterion
from lfs.criteria.models import LengthCriterion
from lfs.criteria.models import WidthCriterion
from lfs.criteria.models import WeightCriterion
from lfs.criteria.models import ShippingMethodCriterion
from lfs.criteria.models import PaymentMethodCriterion
from lfs.customer.models import Customer
from lfs.order.models import Order

class Migration(SchemaMigration):
    no_dry_run = True
    def forwards(self, orm):
        """ refactored address
        """

        # Addresses
        db.add_column("customer_customer", "sa_content_type", models.ForeignKey(ContentType, related_name="sa_content_type", blank=True, null=True))
        db.add_column("customer_customer", "sa_object_id", models.PositiveIntegerField(default=0))
        
        db.add_column("customer_customer", "ia_content_type", models.ForeignKey(ContentType, related_name="ia_content_type", blank=True, null=True))
        db.add_column("customer_customer", "ia_object_id", models.PositiveIntegerField(default=0))
        
        db.add_column("order_order", "sa_content_type", models.ForeignKey(ContentType, related_name="sa_content_type", blank=True, null=True))
        db.add_column("order_order", "sa_object_id", models.PositiveIntegerField(default=0))
        
        db.add_column("order_order", "ia_content_type", models.ForeignKey(ContentType, related_name="ia_content_type", blank=True, null=True))
        db.add_column("order_order", "ia_object_id", models.PositiveIntegerField(default=0))
        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customer_address")
        for address in dictfetchall(cursor):
            try:
                # 1st try to get customer by the stored customer_id in addresses
                customer = Customer.objects.get(pk=address["customer_id"])
            except Customer.DoesNotExist:
                # If there is no customer_id we try the other way around.
                customer_cursor = connection.cursor()
                customer_cursor.execute("SELECT id from customer_customer WHERE selected_invoice_address_id=%s or selected_shipping_address_id=%s" % (address["id"], address["id"]))
                try:
                    customer_id = customer_cursor.fetchone()[0]
                except TypeError:
                    continue
                else:
                    customer = Customer.objects.get(pk=customer_id)
        
            # Create new address out of old
            new_address = Address.objects.create(
                pk=address["id"],
                customer= customer,
                firstname = address["firstname"],
                lastname = address["lastname"],
                company_name = address["company_name"],
                line1 = address["line1"],
                line2 = address["line2"],
                zip_code = address["zip_code"],
                city = address["city"],
                state = address["state"],
                country_id = address["country_id"],
                phone = address["phone"],
                email = address["email"],
            )
        
            # Get current selected shipping and invoice address (these aren't
            # available through ORM)
            customer_cursor = connection.cursor()
            customer_cursor.execute("SELECT selected_invoice_address_id, selected_shipping_address_id from customer_customer WHERE id=%s" % customer.id)
            cur_ia, cur_sa = customer_cursor.fetchone()
        
            # Assign the new address to the customer
            if cur_ia == address["id"]:
                customer.selected_invoice_address = new_address
            elif cur_sa == address["id"]:
                customer.selected_shipping_address = new_address
            customer.save()
        
        # Migrate addresses of orders
        cursor.execute("SELECT * FROM order_order")
        for order in dictfetchall(cursor):
        
            if order["user_id"]:
                try:
                    customer = Customer.objects.get(user=order["user_id"])
                except Customer.DoesNotExist:
                    continue
            else:
                customer = None
        
            invoice_address = Address.objects.create(
                order_id = order["id"],
                customer = customer,
                firstname = order["invoice_firstname"],
                lastname = order["invoice_lastname"],
                company_name = order["invoice_company_name"],
                line1 = order["invoice_line1"],
                line2 = order["invoice_line2"],
                zip_code = order["invoice_code"],
                city = order["invoice_city"],
                state = order["invoice_state"],
                country_id = order["invoice_country_id"],
                phone = order["invoice_phone"],
                email = order["customer_email"],
            )
        
            shipping_address = Address.objects.create(
                order_id = order["id"],
                customer = customer,
                firstname = order["shipping_firstname"],
                lastname = order["shipping_lastname"],
                company_name = order["shipping_company_name"],
                line1 = order["shipping_line1"],
                line2 = order["shipping_line2"],
                zip_code = order["shipping_code"],
                city = order["shipping_city"],
                state = order["shipping_state"],
                country_id = order["shipping_country_id"],
                phone = order["shipping_phone"],
                email = order["customer_email"],
            )
        
            order_instance = Order.objects.get(pk=order["id"])
            order_instance.invoice_address = invoice_address
            order_instance.shipping_address = shipping_address
            order_instance.save()
        
        fields = [
            "invoice_firstname",
            "invoice_lastname",
            "invoice_company_name",
            "invoice_line1",
            "invoice_line2",
            "invoice_city",
            "invoice_state",
            "invoice_code",
            "invoice_country_id",
            "invoice_phone",
            "shipping_firstname",
            "shipping_lastname",
            "shipping_company_name",
            "shipping_line1",
            "shipping_line2",
            "shipping_city",
            "shipping_state",
            "shipping_code",
            "shipping_country_id",
            "shipping_phone",
        ]
        
        for field in fields:
            db.delete_column("order_order", field)
    
    def backwards(self, orm):
        db.delete_column("customer_customer", "sa_content_type_id")
        db.delete_column("customer_customer", "sa_object_id")
        
        db.delete_column("customer_customer", "ia_content_type_id")
        db.delete_column("customer_customer", "ia_object_id")
        
        db.delete_column("order_order", "sa_content_type_id")
        db.delete_column("order_order", "sa_object_id")
        
        db.delete_column("order_order", "ia_content_type_id")
        db.delete_column("order_order", "ia_object_id")
        

def dictfetchall(cursor):
    """
    Returns all rows from a cursor as a dict
    """
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
