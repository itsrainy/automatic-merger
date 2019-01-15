Automatic Merger between Git Repo Branches
# DO NOT USE THIS. IT IS NOT INTENDED FOR PRODUCTION USE AT ALL. I WROTE IT IN LESS THAN 2 HOURS AND IT HAS NOT BEEN THOROUGHLY TESTED OR VALIDATED

To set up:
1. Run `./setup-testrepo1.sh`. This will create a test repo with three branches in a folder called `test-data`
2. Ensure that you have a `merger-config.json` file that looks like the following:
```{
    "repositories": [
        {
            "name": "repo1",
            "url": "test-data/repo1",
            "locationOnDisk" : "CHANGE THIS",
            "edges": [
                {
                    "from": "testBranch1",
                    "to": "testBranch2"
                },
                {
                    "from": "testBranch2",
                    "to": "testBranch3"
                }
            ]
        }
    ]
}```

You will need to change the `locationOnDisk` to be whatever location you want the service's version of the repo to live at

3. Run `python auto-merger.py 8080` in a separate shell. This will set up the script to listen on port 8080
4. Run `add-commit-to-parent-branch.sh`. This will add a commit to the `testBranch1` branch for you
5. From a separate shell, run `curl -d '{"repo": "repo1", "branch": "testBranch1"}' localhost:8080`. This will tell the service that a new commit has been added to `testBranch1`

After that, you can verify the service has updated the repo by looking at the logs it spits out or by running `git log` in the actual repo folder.
