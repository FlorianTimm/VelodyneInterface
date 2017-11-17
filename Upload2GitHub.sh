git pull
autopep8 --in-place --aggressive --aggressive *.py
git add .
datum=$(date +%y-%m-%d_%H:%M:%S)
git commit -m "Stand $datum"
git push
