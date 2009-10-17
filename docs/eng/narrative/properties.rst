==========
Properties
==========

Zweck
=====
* Properties dienen dazu Produkte variable Eigenschaften zuzuweisen.

* Properties werden genutzt um: Produkte zu filtern (Filtered Navigation, 
  Filtered Search), Produkte zu vergleiche, zur Erzeugung von Varianten 
  (Shopbetreiber) und Auswahl von Variante (Käufer).

Allgemein
=========

* Properties werden zentral verwaltet.

* Properties werden mittels einer Propertygruppe zusammengefasst.

* Ein Property kann mehreren Propertygruppen zugewiesen werden.

* Properties werden über Produktgrupppen Produkten zugeordnet: Produkte haben 
  Propertygruppen, Propertygruppen haben Properties, daraus folgt: Produkte 
  haben die Properties ihrer zugewiesenen Produktgruppen.
  
* Properties um Eigenschaften zuzuweisen, steht sinvollerweise nur für den 
  Subtyp "Produkt" und "Variante" zur Verfügung.

* Properties um Varianten zu erzeugen, steht sinvollerweise nur für den Subtyp 
  "Product mit Varianten" zur Verfügung.
  
* Produkte können zur Generierung von Varianten lokale Properties haben. Diese
  sind nur für das jeweilige Produkt gültig.

Löschen und Entfernen von Properties/Propertygruppen
=====================================================

* Wird ein Property gelöscht, werden alle Werte, die Produkte für dieses 
  Property zugewiesen bekommen haben, gelöscht.

* Wird ein Property aus einer Gruppe entfernt, werden von Produkten, die dieser 
  Gruppe zugewiesen sind alle zugewiesnen Werte für dieses Property gelöscht.
    
* Wird eine Propertygruppe gelöscht, werden von Produkten, die dieser Gruppe
  zugewiesen sind alle Werte für die Properties dieser Gruppe haben gelöscht.
  
Filter
======
* Wenn ein Filter gesetzt wird, werden:

  - Produkte angezeigt, die dem Filter entsprechen.
  
  - "Produkte mit Varianten" angezeigt, bei denen mindestens eine Variante dem
    Filter entspricht. (Es werden nicht die Varianten selbst angezeigt).