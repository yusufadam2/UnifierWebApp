# w6-comp10120-tutorial
Source repository for the comp10120 tutorial project for tutorial group W6

Hosted at [http://comp10120.ddns.net](http://comp10120.ddns.net)

## Git Usage
Git command reference:

### Before Starting Working
Before starting work on any code, make sure to update your local repo. Run:
```sh
git fetch
git status
```

If there are no newer commits on your current branch, then proceed to "Building 
a Feature". Otherwise, run:
```sh
git pull
```

Make sure to resolve any merge conflicts by manually editing the affected files.

### Building a Feature
When starting work on a new feature, run:
```sh
git branch <name-of-branch>
git checkout <name-of-branch>
```
NOTE: The name of the branch should be a short, all-lowercase word or two,
separated by hyphens. For example `user-matching`, or `frontend-index`.

When working on a new feature, frequently run:
```sh
git add .
git commit
git push
```
NOTE: `git add .` will start tracking all changes in the current directory (`.`) 
and in subfolders of `.`. Thus, make sure to be in w6-comp10120-tutorial/webapp 
to ensure no changes are left behind.

NOTE2: The first time you push to the branch, no "remote branch" will have been 
created. Git might complain. To fix this, replace `git push` with `git push -u 
origin <name-of-branch>`.

#### Commit Messages
Commit messages should be of the following format:
```
Max 73 character short overview of changes, followed by a newline

A more in-depth overview of changes, with reasons for broad additions 
and changes listed in the following format:
+ reason for adding feature X
  + reason for adding subfeature X.1
  ~ reason for reworking/updating subfeature X.2
  - reason for removing feature X.3
~ reason for reworking/updating feature Y
- reason for removing feature Z
```
NOTE: The short overview must not have any trailing punctuation

#### Pull Requests
Once work on a branch has been completed, go to the gitlab repo and submit a 
"Pull Request". This will allow us to perform a quick code review and ensure 
that the small bugs dont get into the repo (and have to be constantly fixed by 
many tiny commits which spam the commit history).

### Cleaning Up
When a pull request has been accepted and the changes merged into master, 
pull the changes and cleanup your local branch. Run:
```sh
git checkout master
git pull
git branch -d <name-of-branch>
```

