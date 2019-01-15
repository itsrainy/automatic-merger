mkdir -p test-data/repo1/
cd test-data/repo1
git init .
touch a few files
git add .
git commit -m "Initial commit in test repo"
git checkout -b testBranch1
git checkout -b testBranch2
git checkout -b testBranch3
git checkout master