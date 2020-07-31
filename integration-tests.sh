echo 'running stdin example'
cat examples/star18504.txt | python3 -m nmrpystar.examples.full stdin

echo 'running file example'
python3 -m nmrpystar.examples.full file

echo 'running url example'
python3 -m nmrpystar.examples.full url
