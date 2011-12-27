===================
How To Setup Paypal
===================

Overview
========

In this how-to you will learn how to setup paypal for your shop

Steps
=====

1. Setup a paypal developer account at https://developer.paypal.com/

2. Add a pre-configured test Buyer https://developer.paypal.com/cgi-bin/devscr?cmd=_sandbox-acct-session

3. Add a pre-configured test Seller https://developer.paypal.com/cgi-bin/devscr?cmd=_sandbox-acct-session

4. Launch the sandbox account for the Seller from https://developer.paypal.com/cgi-bin/devscr?cmd=_sandbox-acct-session

5. Set up IPN

  * Click on "Profile" - "Instant Payment Notification Preferences"

  * Set the Notification URL to   http://www.yourdomainname.com/paypal/ipn/

  * Turn IPN On

6. Set up PDT

 * Click on "Profile" - "Website Payment Preferences"

 * Turn on "Auto Return"

 * Set the "Return URL" to http://www.yourdomainname.com/paypal/pdt/

 * Set "Payment Data Transfer" to On, this will create an Identity Token for us.


7. Copy our seller information to settings.py e.g.::

    PAYPAL_RECEIVER_EMAIL = "seller_1262786866_biz@yourdomainname.com"
    PAYPAL_IDENTITY_TOKEN = "j0Iw3M4l6znE45kWkyQs43PkwC9bkaceteiWXfddg5q_CW1Ev4HGuqVPPfBG"

8. Deploy your site to a live internet site for testing (Paypal servers must be able to see your site).

9. When you are finished testing your site and ready to go live, set up a live Paypal Business account (Website Payments Standard account has been reported to work) and repeat steps 5-8
