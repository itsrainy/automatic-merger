cd test-data/repo1
git checkout testBranch1
echo $RANDOM >> testfile
git add .
git commit -m "Brand new test commit"
git checkout master