==========
dockomorph
==========

A daemon which builds/runs docker images in response to github notifications.

Code Architecture
=================

+------------------+
| web server       |
| +----------------+
| | github webhook |
+-+----------------+
    |
    |
+------------------+
|   | orchestrator |
|   |              |
|   v              |
| +---------+      |
| | repoman |      |
| +---------+      |
|   |              |
|   v              |
| +----------+     |
| | dockherd |     |
| +----------+     |
|                  |
+------------------+
