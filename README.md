# ERO2

## Setup

Installation et setup :

`pip install virtualenv`

`python3 -m virtualenv ERO2-venv`

Pour interagir avec l'environnement :

`source ERO2-venv/bin/activate` pour se mettre dans l'environnement

`deactivate` pour quitter l'environnement

Ensuite installer les packages dans l'environnement avec : 

`pip install -r requirements.txt`

Puis, toujours dans l'environnement faire la commande suivante pour avoir le
kernel jupyter associé :

`python3 -m ipykernel install --user --name ERO2-venv --display-name "ERO2 (ERO2-venv)"`

Ensuite :

`jupyter notebook` ou `jupyter lab`

Dans jupyter, aller dans 'Kernel', puis 'Change Kernel', et choisir
"ERO2 (ERO2-venv)" (ou juste "ERO2-venv")
