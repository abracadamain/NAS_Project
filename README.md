# NAS_Project

## fichier d'intentions:

Fichier JSON qui décrit l'architecture voulue du réseau, dans lequel sont listés tous les routeurs, triés par AS. Dans notre cas on a un réseau provider composé de 4 routeurs dont 2 de bordure. Et on a 2 clients possédants chacun 2 AS d'un routeur. Le fichier décrit les informations suivantes :

- les AS
- les plages d'adresses ipv4 pour chaque AS
- les masques des adresses loopback et adresses ipv4 (définissant la taille du sous-réseau)
- les routeurs avec leurs interfaces et voisins en lien physiques
- les type de routeur (P, PE ou CE)
- le numéro de chaque client

## Comment configurer le réseau décrit par le fichier d'intention sur GNS3?

- créer l'architecture correspondante au fichier sur GNS3 et nommer le projet 'NAS'
- lancer le code conversion.py
- les fichiers cfg de configuration pour chaque routeur sont générés
- en gardant GNS3 ouvert, lancer le bot Drag and Drop en exécutant Drag_and_Drop.py
- le réseau est configuré automatiquement

## Fonctionalités supportées :

- génération automatique des adresses ip dont loopback
- mise en place des protocoles de routage interne et externe
- mise en place de MPLS
- Drag and Drop bot

## Fonctionalités non supportées :

- Route reflection
- VPN sharing
- Internet services
- OSPF metric optimization
