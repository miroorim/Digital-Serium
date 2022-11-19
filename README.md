# Digital Serium

L'equipe de Serium à pour but d'améliorer la communication entre les médecins et leurs patients, dans un objectif de prévention.
Il faudrait pouvoir récolter des données de santé de façons journaliere, qui serait ensuite transmise au médecin traitant qui pourrait alors intervenir le plus tot posible en cas d’anomalie.

Dans cette optique nous avons créer "Digital Serium". Digital Serium est un miroir pas comme les autres. C'est un miroir inteligent spécialisé dans la santé.
Il se compose de nombreux capteurs. Plus précisement, une camera infra-rouge(IR), une caméra utlra-violet (UV) et d'une caméra du spectre visible, d'une qualité de 32 Mpx. 
Ce miroir est doté d'un systeme d'affichage permetant un retour visuel. 

Chacune des cameras ont un roles bien precis et repondent à un besoin spécifique. Ainsi la camera IR permet de decteter la fièvre, les zones inflamatoires ou encore des maladie tel que la varice et le cancer du seins.
La caméra UV permet une detection fiable de l'acnée, de la peau sèche ainsi que certains champignons de peau. 
Pour finir, la camera classico-classique analyse la posture de l'individu, le taint de la peau pour detecter des maladies ou des carances.

Toutes ces données sont recolté puis chiffré en utulisant le Multi-Party Computation, très fiable et securisé mais un peu couteux. Une fois les données chiffrées elles sont stockées chez un hébergeur certifié par l'agence du numérique en santé.
L'hebergeur en question sera ici OVH. 

Une fois les données stockée elles serviront à de nombreuse chose. Premierement à l'amélioration du model d'IA (spécifique à l'utilisateur), les données seront ensuites transformé en un contre rendu mensuel qui serat transmis au medecin traitant.
Enfin les données seront anonymisé, transormer en statistique et revendu à différent acteur du milieu. Les données brutes sont ensuite suprimmées (30j glissant).

Finalement le miroir vient avec une application "Serium else" de suivis.
Ainsi l'utilisateur peut suivre sont evolution dans le temps de façons journalière, hebdomadaire ou mensuel. De plus, l'application intègre l'indicateur Serium qui est notre indicateur propriétaire regroupant l'ensemble des données collectées pour établir un score de santé global.
Serium health intègre aussi des recommandations en fonction de notre état de santé. 

