---
layout: page
title: Contribute
permalink: /contribute/
---

There are several ways to contribute to OSIS. You don't even need to be a Python
developer.

### Reporting Issues

If you wish to point out an issue in the application or propose a new feature,
you can do so by filing a
[GitHub issue](https://github.com/uclouvain/osis/issues).

### Developing

#### Updating your Fork

It's a good practice to update your fork before submitting a new pull request.
It helps the project manager on his demanding job of merging and solving
conflicts on the code. To update your fork, add a new remote link pointing to
the original repository:

    $ git remote add upstream https://github.com/uclouvain/osis.git

This step is performed only once because Git preserves a list of remote links
locally. Fetch the content of upstream in order to perform a merge with your
local master branch:

    $ git fetch upstream

Then, go to the local master branch (if you are not already there) and merge it
with upstream's master branch:

    $ git checkout master
    $ git merge upstream/master

Finally, push your master branch to your own repository:

    $ git push origin master

Now, you are ready to write your contributions.
