Gestion inscription - Relais de l'ENSIL
=======================================

UNDER WRITING !

L'ensemble des informations présentes ici sont décrites pour un environnement Linux.
Pour travailler, modifier et debuger, il est vivement recommandé d'avoir soit un PC
sur Linux, soit de démarrer une machine virtuelle avec un Linux (voir dernière partie)

Quickstart
----------
- Paquet à installer
> apt-get install python2 python-virtualenv git
- (pour eclipse)
> apt-get install java...

> git clone (? TODO)
> cd relais
> make virtualenv
> make dependencies
# copy database or > ./manage.py syncdb
> ./manage.py runserver

Structure du projet
-------------------
./
~~
Racine du projet

- ./db.sqlite3: base de donnée SQLite pour le Relais
- ./Makefile: comme son nom l'indique
- ./requirements.txt: liste des dépendances
- ./manage.py: gestion du projet Django

./apache/
~~~~~~~~~
Contient scripts + configuration lors du déploiement

./engine/
~~~~~~~~~
Configuration du moteur de Django

- ./settings/: configuration globale sur site si dev ou production
- ./urls.py: configuration globale des redirections url <-> vues

./relais/
~~~~~~~~
Ensemble de "l'application" module d'inscription

- ./admin.py: définition et paramètrage pour le module d'administration
- ./constants.py: définition de constantes utilisable à travers plusieurs fonctions
- ./forms.py: définition des formulaires en Python ainsi que leur procédure de
  vérification et validation
- ./models.py: définition des tables dans la base de donnée ainsi que leur procédure de
  vérification et validation
- ./helpers/: définition de quelques fonctions communes
- ./locale/: traduction du site
- ./migrations/: étape à effectuer lorsque l'on change la base de donnée
- ./static/: fichiers CSS/JS ou autre utilisés par le site, mais pas par Python
- ./template/: template HTML utilisées pour la génération des pages
- ./templatetags/: outils supplémentaires utilisés lors des générations des templates
- ./urls/: configuration des redirections url<->view au sein de l'application Relais
- ./views/: controle les données, génère le rendu et les appels dans la base de donnée


Comment developper
------------------
Démarrage
~~~~~~~~~
Afin de ne pas coder comme des pieds, on va utiliser l'éditeur IDE Eclipse avec une extension pour gérer
Python et Django.

* Télécharger la version Mars.1 de Eclipse ici:
* Extraire dans votre dossier personnel
* Le lancer
* Ensuite, Help -> Install new software (?)
* PyDev (URL)
* Django (URL)
* Cocher les extensions et valider, puis redémarrer Eclipse.

Importer le projet tout juste cloné
* File -> Import
* Select Existing Project on Workspace
... ?

Modification du virtualenv

Règle de codage
~~~~~~~~~~~~~~~
On respecte dans la mesure du possible la norme de PEP8


Comment récupérer le projet
---------------------------
Actuellement, l'ensemble du module d'inscription est sur mon serveur personnel.
Afin de garder un historique des modifications qui ont été apportées au cours du temps,
le logiciel de versionning Git est utilisé.

Principe: à chaque modification de base (ajout d'une fonctionnalité, correction d'un bug),
on effectue un "commit" qui correspondant à la différence avant/après modifications
des fichiers impliqués.

git clone: récupère un dépot git distant pour pouvoir travailler chez nous
git add /path/to/file: ajoute dans un commit un nouveau fichier non versionalisé
git add -u: ajoute dans le commit en cours tous les fichiers déjà versionalisés qui ont été modifiés
git commit -s: crée un commit avec un commentaire à faire avec la signature de l'auteur du commit
git reset: annule le commit en cours (n'annule pas les modifications)
git checkout /path/to/file: annule les modifications d'un fichier
git reset HEAD --hard: retourne à la version originale (annule toutes les modifications)
git pull --rebase: recupère les modifications distantes et tente d'appliquer les modifications locales
git push origin master: pousse les modifications vers le serveur Git distant
git log: affiche l'historique des modifications
git log --oneline --decorate: idem, mais en version simplifiée
git show: affiche en détail le dernier commit
git show SHA1: affiche en détail le commit avec le numéro SHA1 correspondant

Machine virtuelle
-----------------
Si pour une raison quelconque, vous n'avez pas de PC sur Linux pour développer,
utiliser une machine virtuelle tout prête, avec Eclipse et tout déjà d'installé.

TODO
