"""
Various utilities for working with hg (Mercurial version control system).
"""

from commands import getstatusoutput as system

def get_tip():
    """
    Return the tip (revision number of the most recent changeset)
    of a hg tree (current working directory).
    """
    failure, output = system('hg tip')
    lines = output.splitlines()
    tip = lines[0].split(':')[1]
    user = lines[2].split(':')[-1]
    return int(tip), user


def get_last_two_changesets(filename):
    """
    Return the revision number of the last two changesets for a file
    (given by filename).
    """
    failure, output = system('hg log %s' % filename)
    lines = output.splitlines()
    last = lines[0].split(':')[1]
    for line in lines:
        if line.startswith('changeset'):
            next_last = line.split(':')[1]
            break
    return int(last), int(next_last)

def makediff_pdf(filename, rev1, rev2):
    """
    First, check if revisions rev1 and rev2 of a file (filename)
    are equal. If so, make a pdf diff file filename-diff using pdiff.
    Assume that rev1 is the old revision and rev2 is the new revision.
    """
    out1 = '%s-%s' % (filename, rev1)
    out2 = '%s-%s' % (filename, rev2)
    failure, dummy = system('hg cat -r %s %s > %s' % \
                            (rev1, filename, out1))
    failure, dummy = system('hg cat -r %s %s > %s' % \
                            (rev2, filename, out1))
    filestr1 = open(out1).read()
    filestr2 = open(out2).read()
    import difflib
    diff = difflib.ndiff(filestr1, filestr2)
    if diff.strip == '':
        return False
    cmd = 'pdiff %s %s -l -o - | ps2pdf -sPAPERSIZE=a4 - %s-diff.pdf' % \
          (out1, out2, filename)
    failure, output = system(cmd)
    return True
        
def get_all_files():
    """Return a list of all files in the current dir tree managed by hg."""
    failure, output = system('hg manifest')
    return output.splitlines()

def get_changes_in_last_update():
    tip = get_tip()
    for f in get_all_files():
        new, old = get_last_two_changesets(f)
        if new == tip:
            # changes in last update:
            makediff_pdf(f, old, new)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'changes':
        get_changes_in_last_update()
    


        
    
