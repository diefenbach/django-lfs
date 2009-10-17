Shipping
========

General
-------
* There can be several shipping methods, e.g. "standard" and "express" from
  which the customer can choose.

* A shipping method can be set to active/inactive by a simple flag.

* The shipping methods may be restricted by criteria, e.g. the shop owner just
  want to provide "express" when the customer lives within a certain country. 
  
* Only when **all** criteria of a shipping method are true the shipping method 
  is valid.

* Only active and valid shipping methods are provided to choose.

* A shipping method has a default price, which is by default the current price
  of the shipping method.

* A shipping method can have additional prices for a shipping method. Example: 
  if the total cart price is greater than x the price for "standard" shipping 
  method should be y.
  
* Shipping method prices are restricted by criteria. The first price for which
  all criteria a true is the current price of the shipping method. If no 
  additional price is true the default price of the shippping method is taken as
  the current price.

* First the customer gets the default shipping method automatically. This is -
  at the moment and might be changed - the first active and valid shipping 
  method.

* If the current choosen shipping method gets invalid after the shop customer
  changes her cart the default shipping method will be assigned.
  
Berechnung der Lieferzeit
=========================

* Lieferzeiten hängen von der Liefermethode ab, d.h. jede Liefermethode hat
  genau eine Lieferzeit.

* Die Lieferzeit eines Produktes kann sich für die Produktansicht und der
  Warenkorbansicht unterschieden.

* Die Lieferzeit eines Produkts für die Produktansicht wird der Standard-
  Liefermethode eines Produktes entnommen. Diese ist zur Zeit die erste gültige 
  (basierend auf Kriterien) Liefermethode eines Produktes.

* Die Lieferzeit eines Produkts für die Warenkorbansicht wird der Liefermethode
  entnommen, die der Shopkunde gewählt hat. Ist diese jedoch für ein Produkt nicht
  gültig (auf Basis ihrer Kriterien), so wird die Lieferzeit auch hier der 
  Standard-Liefermethode entnommen.

* Die Lieferzeiten der Produkte in Warenkorbansicht werden zwar zu Zeit nicht 
  angezeigt, jedoch dienen diese als Basis für die Berechnung der Gesamtlieferzeit 
  des Warenkorbs.

* Ein Produkt kann eine manuelle Lieferzeiten haben. Ist dies der Fall wird diese 
  Lieferzeit angezeigt und die Berechnung auf Basis der Kriterien entfällt.

* Darüber hinaus kann ein Produkt eine Bestellzeit und eine Bestelldatum haben. 
  Ist ein Proudukt nicht mehr auf Lager, wird diese Bestellzeit (abzüglich der 
  bereits vergangenen Tage seit der Bestellung) hinzugefügt.  