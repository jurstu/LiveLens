# how to run this

python3 -m liveLens.view

or 

python3 -m liveLens.gifGenerator



# how to profile and view
pip3 install snakeviz

python3 -m cProfile -o profile.out -m liveLens.gifGenerator

snakeviz profile.out

