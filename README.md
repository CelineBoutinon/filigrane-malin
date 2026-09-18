# 🦊 Filigrane Malin


## **L'alternative 100% hors-ligne, intelligente & sécurisée pour protéger vos documents d'identité.**

![Démonstration de Filigrane Malin](./demo.gif)


## 🛑 Pourquoi *Filigrane Malin* ?

**Filigrane Malin** répond au besoin de protection des données personnelles en offrant la possibilité d'apposer un filigrane et de protéger un document PDF ou une image avec un mot de passe par un processus réalisé **100% localement sur votre propre machine**. Aucune information ne quitte votre ordinateur dans le processus de création du document sécurisé, seulement lorsque **VOUS** décidez (éventuellement) de le partager après sécurisation.

Le service officiel de l'État [`filigrane.beta.gouv.fr`](https://filigrane.beta.gouv.fr/) est une excellente initiative sur le papier. Cependant, il exige des utilisateurs qu'ils envoient leurs documents les plus sensibles (cartes d'identité, passeports, fiches de paie, avis d'imposition...) sur des serveurs distants **AVANT** l'apposition du filigrane et de toute protection cryptographique éventuelle. Bien que ne contrevenant pas aux dispositions du RGPD, ce processus expose des utilisateurs vulnérables à des risques résiduels qu'ils ne comprennent pas toujours. **Il y a une différence de taille entre conformité réglementaire et sécurité maximale.**

À l'heure où les vols de données personnelles des citoyen(ne)s français(es) se multiplient dans les services publics, les associations sportives et les grandes entreprises, il faut bien comprendre que **télécharger une pièce d'identité non chiffrée et non filigranée sur un serveur tiers présente toujours un risque et expose inutilement les utilisateurs au vol de leurs données et à l'usurpation potentielle de leur identité** (qui, rappelons-le, touche plus de 200 000 personnes en France chaque année). 

* **Une promesse n'est pas un bouclier :** Le RGPD est un cadre juridique, pas un pare-feu. Il ne protège pas contre les failles "zero-day", les erreurs de configuration des serveurs, l'usurpation des accès des personnels de l'État ou l'interception de données pendant leur trajet depuis votre ordinateur vers les serveurs de l'État.

* **Une « fenêtre de vulnérabilité » résiduelle :** Même si `filigrane.beta.gouv.fr` promet une suppression instantanée du fichier téléchargé, et du fichier généré après téléchargement (ou au maximum dans les 24 heures si vous ne le téléchargez pas), votre document non sécurisé doit tout de même quitter votre ordinateur, voyager sur Internet et résider (même brièvement) sur les serveurs de l'État. Si ce serveur est compromis à ce moment précis, le script de suppression ne sert à rien : les données ont déjà été copiées.

* **Le miel & les abeilles :** Étant donné que tout le pays est invité à télécharger ses pièces d'identité et autres documents sensibles sur une unique adresse Internet, ce serveur devient une cible massive et de haute valeur (un "honeypot"🍯) pour les pirates informatiques (en espérant que ces lignes ne suscitent pas de vocations...).

**Filigrane Malin** permet une mitigation maximale de ces risques en permettant d'apposer le filigrane et une protection cryptographique (optionnelle) **100% localement** sur votre ordinateur.


## ✨ Fonctionnalités Avancées
Outre le traitement 100% local, *Filigrane Malin* inclut les éléments distinctifs suivants :
* **Déformation par onde sinusoïdale :** Le texte du filigrane suit une ligne de base ondulée, rendant l'effacement par Photoshop ou par IA générative beaucoup plus complexe et chronophage.
* **Typographie alternée & ombre portée :** Lignes de couleurs alternées avec des ombres portées pour garantir le contraste sur n'importe quel fond.
* **Filigrane paramétrable par l'utilisateur :** Outre le contenu textuel du filigrane à appliquer sur son document, l'utilisateur peut modifier la taille et les couleurs de police, l'orientation du texte ou encore l'intensité de la déformation par onde sinusoïdale.
* **Support multi-formats :** Traite les documents PDF ou les images (PNG, JPG, JPEG) et les restitue en documents PDF sécurisés sans perte de qualité.
* **Protection par mot de passe & chiffrement AES-128 :** Plus qu'un simple processeur d'images, *Filigrane Malin* est un véritable utilitaire OPSEC Zero-Trust (Sécurité Opérationnelle en mode Zéro-Confiance). Doté d'un générateur de mots de passe intégré qui utilise le module cryptographique *secrets* de Python pour créer des mots de passe robustes et à haute entropie, d'une longueur de 16 caractères, combinant majuscules, minuscules, chiffres et caractères spéciaux, il est en conformité avec les [recommandations officielles de la CNIL](https://www.cnil.fr/fr/mots-de-passe-recommandations-pour-maitriser-sa-securite) en matière de création de mots de passe sécurisés.
* **Outil pédagogique :** En éduquant l'utilisateur sur les principes de création de mots de passe *vraiment* sécurisés, et en l'encourageant à dissocier la charge utile (le document) de la clé (le mot de passe) en utilisant deux canaux de communication distincts, *Filigrane Malin* vise à vulgariser auprès du grand public les méthodes appliquées par les professionnels de la cybersécurité pour manipuler des données sensibles. Par ailleurs, si l'utilisateur souhaite créer son propre mot de passe, *Filigrane Malin* lui permet également d'en évaluer la force en affichant le temps de piratage estimé. Enfin, l'application affiche un avertissement lié à la réutilisation des mots de passe dès que l'utilisateur saisit son propre mot de passe au lieu d'utiliser le générateur intégré, et propose des liens externes vers des sites de vulgarisation en matière de création et de gestion sécurisées des mots de passe.


## 🚀 Installation

### 📌 Option no-code pour tou(te)s
Allez dans la section **[Releases](../../releases)** de ce dépôt (sur la droite de cet écran) et suivez les instructions.

### 📌 Option code source pour les devs...
... qui n'ont pas besoin d'instructions 😉  


## 🛠️ Stack Technique
**Version de Python :** 3.13.2

**Interface utilisateur :** Streamlit

**Traitement d'image :** Pillow

**Traitement PDF :** PyMuPDF

**Génération des mots de passe :** Secrets


***Mentions légales :***  
 *Filigrane Malin est un outil fourni 'tel quel', sans garantie d'aucune sorte, explicite ou implicite. L'utilisateur reste seul responsable de l'utilisation de ses documents et du respect des exigences des organismes destinataires. Veuillez vous référer au fichier LICENSE.txt pour plus d'informations.*
 
*Vibe-codé avec Google Gemini & 💙🤍❤️ pour la protection de la vie privée des Français(es).*  