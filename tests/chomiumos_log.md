PS C:\Users\jayla> git clone https://chromium.googlesource.com/chromiumos
Cloning into 'chromiumos'...
remote: Finding sources: 100% (924/924)
remote: Total 924 (delta 363), reused 877 (delta 363)
Receiving objects: 100% (924/924), 296.59 KiB | 342.00 KiB/s, done.
Resolving deltas: 100% (363/363), done.
Note: switching to 'f73e3693af99fd87555ebb4a1dbf6d9bc4a6ab20'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

Turn off this advice by setting config variable advice.detachedHead to false

PS C:\Users\jayla>lets make a new repo moving forward- taking the opportunity to merge anything we can 

Output:

Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\jayla> docker build -t app:local -f Dockerfile .

[+] Building 0.2s (1/1) FINISHED       docker:desktop-linux
 => [internal] load build definition from Dockerfile   0.1s
 => => transferring dockerfile: 2B                     0.0s
ERROR: failed to build: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory

View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/9aemjed2n0nki0yhfd0lzt2p4

What's next:
    Debug this build failure with Gordon → docker ai "help me fix this build failure"
PS C:\Users\jayla> git switch -c chromium-4rl
fatal: not a git repository (or any of the parent directories): .git
PS C:\Users\jayla>
----