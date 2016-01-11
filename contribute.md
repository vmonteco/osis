---
layout: page
title: Contribute
permalink: /contribute/
---

There are several ways to contribute to OSIS. You don't even need to be a Python developer

# Code of Conduct *

As contributors and maintainers of this project, and in the interest of fostering an open and welcoming community, we pledge to respect all people who contribute through reporting issues, posting feature requests, updating documentation, submitting pull requests or patches, and other activities.

We are committed to making participation in this project a harassment-free experience for everyone, regardless of level of experience, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

Examples of unacceptable behavior by participants include:

- The use of sexualized language or imagery
- Personal attacks
- Trolling or insulting/derogatory comments
- Public or private harassment
- Publishing other's private information, such as physical or electronic addresses, without explicit permission
- Other unethical or unprofessional conduct.

Project maintainers have the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned to this Code of Conduct. By adopting this Code of Conduct, project maintainers commit themselves to fairly and consistently applying these principles to every aspect of managing this project. Project maintainers who do not follow or enforce the Code of Conduct may be permanently removed from the project team.

This code of conduct applies both within project spaces and in public spaces when an individual is representing the project or its community.

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by opening an issue or contacting one or more of the project maintainers.

<sup>* This Code of Conduct is adapted from the [Contributor Covenant](http://contributor-covenant.org/version/1/2/0/), version 1.2.0.</sup>

# Modalities

#### Reporting Issues

If you wish to point out an issue in the application or propose a new feature, you can do so by filing a [GitHub issue](https://github.com/uclouvain/osis-louvain/issues).

#### Developing

##### Updating your Fork

It's a good practice to update your fork before submiting a new pull request. It helps the project manager on his demanding job of merging and solving conflicts on the code. To update your fork, add a new remote link pointing to the original repository:

    $ git remote add upstream https://github.com/uclouvain/osis-louvain.git

This step is performed only once because Git preserves a list of remote links locally. Fetch the content of upstream in order to perform a merge with your local master branch:

    $ git fetch upstream

Then, go to the local master branch (if you are not already there) and merge it with upstream's master branch:

    $ git checkout master
    $ git merge upstream/master

Finally, push your master branch to your own repository:

    $ git push origin master

Now, you are ready to write your contributions.
