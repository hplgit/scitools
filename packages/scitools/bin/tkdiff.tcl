#!/bin/sh
#-*-tcl-*-
# the next line restarts using wish \
exec wish "$0" -- ${1+"$@"}

# $Id: tkdiff.tcl,v 1.1.1.1 2004/04/17 07:23:06 hpl Exp $

###############################################################################
#
# TkDiff -- A graphical front-end to diff for Unix and NT.
# Copyright (C) 1994-1998 by John M. Klassa.
#
# Usage:
#         To interactively pick files:
#             tkdiff
#
#         Plain files:
#             tkdiff <file1> <file2>
#
#         Plain file with conflict markers:
#             tkdiff -conflict <file>
#
#         Source control RCS/CVS/SCCS/PVCS/Perforce:
#             tkdiff <file> (same as -r)
#             tkdiff -r <file>
#             tkdiff -r<rev> <file>
#             tkdiff -r<rev> -r <file>
#             tkdiff -r<rev1> -r<rev2> <file>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# THINGS TO DO:
#
# the code that parses the command line ought to be separated from the
# code that reads in the files. That way we can parse the command line
# right up front and display potential problems on stdout instead of
# waiting until the window display.
###############################################################################


# get this out of the way -- we want to draw the whole user interface
# behind the scenes, then pop up in all of its well-laid-out glory
wm withdraw .

# set a couple o' globals that we might need sooner than later
set g(name) "TkDiff"
set g(version) "3.02"
set g(nativeMenus) 1

# ok, I'll admit -- this is a personal preference. I suppose I ought to
# move this into the preferences or remove it entirely. Sue me. :-)
option add "*TearOff" false 100

###############################################################################
# determine the name of the temporary directory and the name of
# the rc file, both of which are dependent on the platform.
###############################################################################
switch $tcl_platform(platform) {
    windows {
        if {[info exists env(TEMP)]} {
            set opts(tmpdir) $env(TEMP)
        } else {
            set opts(tmpdir) C:/temp
        }
        set basercfile "_tkdiff.rc"
    }
    default {
        # Make menus and buttons prettier
        option add *Font -*-Helvetica-Medium-R-Normal-*-12-*

        if {[info exists env(TMPDIR)]} {
            set opts(tmpdir) $env(TMPDIR)
        } else {
            set opts(tmpdir) /tmp
        }
        set basercfile ".tkdiffrc"
    }
}

###############################################################################
# compute preferences file location. Note that TKDIFFRC can hold either
# a directory or a file, though we document it as being a file name
###############################################################################
if {[info exists env(TKDIFFRC)]} {
    set rcfile $env(TKDIFFRC)
    if {[file isdirectory $rcfile]} {
        set rcfile [file join $rcfile $basercfile]
    }

} elseif {[info exists env(HOME)]} {
    set rcfile [file join $env(HOME) $basercfile]

} else {
    set rcfile [file join "/" $basercfile]
}

###############################################################################
# Fonts are selected based on platform.  Can anyone clean this
# up by finding one set of fonts that looks good everywhere?
# bdo - probably not; fonts are probably best left platform-specific
# For windows I personally recommend Monotype.com, free from Microsoft
# (not that I like Microsoft, but Monotype is a decent fixed width
# font).
###############################################################################

if {$tcl_platform(platform) == "windows"} {
    if {$tk_version >= 8.0} {
        set font "{{Lucida Console} 7}"; # Breaks if you're running
        set bold "{{Lucida Console} 7}"; # Windows with a mono display.
    } else {
        # These XFDs are from Sun's font alias file
        # Also known as 6x13
        set font \
            -misc-fixed-medium-r-semicondensed--13-120-75-75-c-60-iso8859-1
        # Also known as 6x13bold
        set bold \
            -misc-fixed-bold-r-semicondensed--13-120-75-75-c-60-iso8859-1
    }
} else {
    set font 6x13
    set bold 6x13bold
}

###############################################################################
# more initialization...
###############################################################################

array set g {
    changefile      "tkdiff-change-bars.out"
    destroy         ""
    ignore_event,1  0
    ignore_event,2  0
    ignore_hevent,1 0
    ignore_hevent,2 0
    initOK          0
    mapborder       0
    mapheight       0
    mergefile       "tkdiff-merge.out"
    returnValue     0
    showmerge       0
    started         0
    tempfiles       ""
    thumbMinHeight  10
    thumbHeight     10
}

array set finfo {
    pth,1       ""
    pth,2       ""
    title       {}
    tmp,1       0
    tmp,2       0
}

###############################################################################
# These options may be changed at runtime
###############################################################################

array set opts {
    autocenter  1
    autoselect  0
    colorcbs    0
    customCode  {}
    diffcmd     "diff -w"
    editor      ""
    geometry    "80x30"
    showcbs     1
    showln      1
    showmap     1
    syncscroll  1
    toolbarIcons 1
    tagcbs      0
    tagln       0
    tagtext     1
}

if {$tcl_platform(platform) == "windows"} {
    set opts(fancyButtons) 1
} else {
    set opts(fancyButtons) 0
}

# reporting options
array set report {
    doSideLeft           0
    doLineNumbersLeft    1
    doChangeMarkersLeft  1
    doTextLeft           1
    doSideRight          1
    doLineNumbersRight   1
    doChangeMarkersRight 1
    doTextRight          1
    filename             "tkdiff.out"
}


if {[string first "color" [winfo visual .]] >= 0} {
    # We have color
    # (but, let's not go crazy...)
    array set opts [subst {
        textopt "-background white -foreground black  -font $font"
        currtag "-background blue -foreground yellow"
        difftag "-background gray -foreground black  -font $bold"
        deltag  "-background red1 -foreground black"
        instag  "-background green3 -foreground black"
        chgtag  "-background DodgerBlue1 -foreground black"
        -       "-background red1 -foreground red1"
        +       "-background green -foreground green"
        !       "-background blue -foreground blue"
    }]

} else {
    # Assume only black and white
    set bg "black"
    array set opts [subst {
        textopt "-background white -foreground black -font $font"
        currtag "-background black -foreground white"
        difftag "-background white -foreground black -font $bold"
        deltag  "-background black -foreground white"
        instag  "-background black -foreground white"
        chgtag  "-background black -foreground white"
        -       "-background black -foreground white"
        +       "-background black -foreground white"
        !       "-background black -foreground white"
    }]
}

# make sure wrapping is turned off. This might piss off a few people,
# but it would screw up the display to have things wrap
set opts(textopt) "$opts(textopt) -wrap none"

###############################################################################
# Source the rc file, which may override some of the defaults
# Any errors will be reported
###############################################################################

if {[file exists $rcfile]} {

    if {[catch {source $rcfile} error]} {
        set startupError [join [list \
                "There was an error in processing your startup file." \
                "\n$g(name) will still run, but some of your preferences" \
                "\nmay not be in effect." \
                "\n\nFile: $rcfile" \
                "\nError: $error"] " "]
    }
}


# a hack to handle older preferences files...
# if the user has a diffopt defined in their rc file, we'll magically
# convert that to diffcmd...
if {[info exists opts(diffopt)]} {
    set opts(diffcmd) "diff $opts(diffopt)"
}

###############################################################################
# Work-around for bad font approximations,
# as suggested by Don Libes (libes@nist.gov).
###############################################################################
catch {tk scaling [expr 100.0 / 72]}

proc do-exit {{returncode {}}} {
    global g

    # we don't particularly care if del-tmp fails.
    catch {del-tmp}

    if {$returncode == ""} {
        set returncode $g(returnValue)
    }

    # exit with an appropriate return value
    exit $returncode
}


###############################################################################
# Throw up a modal error dialog.
###############################################################################

proc do-error {msg} {
    global argv0
    tk_messageBox -message "$msg" -title "$argv0: Error" -icon error -type ok
}

###############################################################################
# Throw up a modal error dialog or print a message to stderr.  For
# Unix we print to stderr and exit if the main window hasn't been
# created, otherwise put up a dialog and throw an exception.
###############################################################################

proc fatal-error {msg} {
    global g tcl_platform

    if {$tcl_platform(platform) == "windows" || $g(started)} {
        tk_messageBox -title "Error" -icon error -type ok -message $msg
        error "Fatal"
    } else {
        puts stderr $msg
        del-tmp
        do-exit 2
    }
}

###############################################################################
# Return user name.  Credit to Warren Jones (wjones@tc.fluke.com).
###############################################################################

proc whoami {} {
    global env
    if {[info exists env(USER)    ]}      { return $env(USER)    }
    if {[info exists env(LOGNAME) ]}      { return $env(LOGNAME) }
    if {[info exists env(USERNAME)]}      { return $env(USERNAME) }
    if {[info exists env(VCSID)   ]}      { return $env(VCSID) }
    if {[ catch { exec whoami } whoami ]} { return nobody }
    return $whoami
}

###############################################################################
# Return the name of a temporary file
###############################################################################

proc tmpfile {n} {
    global opts
    file join $opts(tmpdir) "[whoami][pid]-$n"
}

###############################################################################
# Execute a command.
# Returns "$stdout $stderr $exitcode" if exit code != 0
###############################################################################

proc run-command {cmd} {
    global opts errorCode

    set stderr ""
    set exitcode 0
    set errfile [tmpfile "r"]

    set failed [catch "$cmd 2>$errfile" stdout]
    # Read stderr output
    catch {
        set hndl [open "$errfile" r]
        set stderr [read $hndl]
        close $hndl
    }
    if {$failed} {
        switch [lindex $errorCode 0] {
            "CHILDSTATUS" {
                set exitcode [lindex $errorCode 2]
            }

            "POSIX" {
                if {$stderr == ""} {
                    set stderr $stdout
                }
                set exitcode -1
            }

            default {
                set exitcode -1
            }
        }
    }

    catch {file delete $errfile}
    return [list "$stdout" "$stderr" "$exitcode"]
}

###############################################################################
# Execute a command.  Die if unsuccessful.
###############################################################################

proc die-unless {cmd file} {
    global opts errorCode

    set result [run-command "$cmd >$file"]
    set stdout   [lindex $result 0]
    set stderr   [lindex $result 1]
    set exitcode [lindex $result 2]

    if {$exitcode != 0} {
        fatal-error "$stderr\n$stdout"
    }
}

###############################################################################
# Filter PVCS output files that have CR-CR-LF end-of-lines
###############################################################################

proc filterCRCRLF {file} {
    set outfile [tmpfile 9]
    set inp [open $file r]
    set out [open $outfile w]
    fconfigure $inp -translation binary
    fconfigure $out -translation binary
    set CR [format %c 13]
    while {![eof $inp]} {
        set line [gets $inp]
        if {[string length $line] && ![eof $inp]} {
            regsub -all "$CR$CR" $line $CR line
            puts $out $line
        }
    }
    close $inp
    close $out
    file rename -force $outfile $file
}


###############################################################################
# Return the smallest of two values
###############################################################################

proc min {a b} {
    return [expr {$a < $b ? $a : $b}]
}

###############################################################################
# Return the largest of two values
###############################################################################

proc max {a b} {
    return [expr {$a > $b ? $a : $b}]
}

###############################################################################
# Toggle change bars
###############################################################################
proc do-show-changebars {{show {}}} {
    global opts
    global w

    if {$show != {}} {set opts(showcbs) $show}

    if {$opts(showcbs)} {
        grid $w(LeftCB)   -row 0 -column 2 -sticky ns
        grid $w(RightCB)  -row 0 -column 1 -sticky ns
    } else {
        grid forget $w(LeftCB)
        grid forget $w(RightCB)
    }
}


###############################################################################
# Toggle line numbers.
###############################################################################
proc do-show-linenumbers {{showLn {}}} {
    global opts
    global w

    if {$showLn != {}} {set opts(showln) $showLn}

    if {$opts(showln)} {
        grid $w(LeftInfo)  -row 0 -column 1 -sticky nsew
        grid $w(RightInfo) -row 0 -column 0 -sticky nsew
    } else {
        grid forget $w(LeftInfo)
        grid forget $w(RightInfo)
    }
}


###############################################################################
# Show line numbers in info windows
###############################################################################

proc draw-line-numbers {} {
    global g
    global w

    $w(LeftInfo)  configure -state normal
    $w(RightInfo) configure -state normal
    $w(LeftCB)    configure -state normal
    $w(RightCB)   configure -state normal

    set lines(Left)  [lindex [split [$w(LeftText) index end-1lines] .] 0]
    set lines(Right) [lindex [split [$w(RightText) index end-1lines] .] 0]

    # Smallest line count
    set minlines [min $lines(Left) $lines(Right)]

    # cache all the blank lines for the info and cb windows, and do
    # one big insert after we're done. This seems to be much quicker
    # than inserting them in the widgets one line at a time.
    set linestuff {}
    set cbstuff {}
    for {set i 1} {$i < $minlines} {incr i} {
        append linestuff "$i\n"
        append cbstuff " \n" ;# for now, just put in place holders...
    }

    $w(LeftInfo)  insert end $linestuff
    $w(RightInfo) insert end $linestuff
    $w(LeftCB)    insert end $cbstuff
    $w(RightCB)   insert end $cbstuff

    # Insert remaining line numbers. We'll cache the stuff to be
    # inserted so we can do just one call in to the widget. This
    # should be much faster, relatively speaking, then inserting
    # data one line at a time.
    foreach mod {Left Right} {
        set linestuff {}
        set cbstuff   {}
        for {set i $minlines} {$i < $lines($mod)} {incr i} {
            append linestuff "$i\n"
            append cbstuff " \n" ;# for now, just put in place holders...
        }
        $w(${mod}Info) insert end $linestuff
        $w(${mod}CB) insert end $cbstuff
    }

    $w(LeftCB)    configure -state disabled
    $w(RightCB)   configure -state disabled

    $w(LeftInfo) configure -state disabled
    $w(RightInfo) configure -state disabled
}

###############################################################################
# Pop up a window for file merge.
###############################################################################

proc popup-merge {{writeproc merge-write-file}} {
    global g
    global w

    set types {
        {{Text Files}    {.txt}}
        {{All Files}     {*}}
    }

    set path [tk_getSaveFile \
            -defaultextension ".tcl" \
            -filetypes $types \
            -initialfile [file nativename $g(mergefile)]]


    if {[string length $path] > 0} {
        set g(mergefile) $path
        $writeproc
    }
}



###############################################################################
# Split a file containing CVS conflict markers into two temporary files
#    name       Name of file containing conflict markers
# Returns the names of the two temporary files and the names of the
# files that were merged
###############################################################################

proc split-cvs-conflicts {name} {
    global g opts

    set first ${name}.1
    set second ${name}.2

    set temp1 [tmpfile 1]
    set temp2 [tmpfile 2]

    if {[catch {set input [open $name r]}]} {
        fatal-error "Couldn't open file '$name'."
    }
    set first [open $temp1 w]
    lappend g(tempfiles) $temp1
    set second [open $temp2 w]
    lappend g(tempfiles) $temp2

    set firstname ""
    set secondname ""
    set output 3

    set firstMatch ""
    set secondMatch ""
    set thirdMatch ""

    while {[gets $input line] >= 0} {
        if {$firstMatch == ""} {
            if {[regexp {^<<<<<<<* +(.*)} $line]} {
                set firstMatch {^<<<<<<<* +(.*)}
                set secondMatch {^=======*}
                set thirdMatch {^>>>>>>>* +(.*)}
            } elseif {[regexp {^>>>>>>>* +(.*)} $line]} {
                set firstMatch {^>>>>>>>* +(.*)}
                set secondMatch {^<<<<<<<* +(.*)}
                set thirdMatch {^=======*}
            }
        }
        if {$firstMatch != ""} {
            if {[regexp $firstMatch $line]} {
                set output 2
                if {$secondname == ""} {
                    regexp $firstMatch $line all secondname
                }
            } elseif {[regexp $secondMatch $line]} {
                set output 1
                if {$firstname == ""} {
                    regexp $secondMatch $line all firstname
                }
            } elseif {[regexp $thirdMatch $line]} {
                set output 3
                if {$firstname == ""} {
                    regexp $thirdMatch $line all firstname
                }
            } else {
                if {$output & 1} { puts $first $line }
                if {$output & 2} { puts $second $line }
            }
        } else {
            puts $first $line
            puts $second $line
        }
    }
    close $input
    close $first
    close $second

    if {$firstname == ""} {
        set firstname "old"
    }
    if {$secondname == ""} {
        set secondname "new"
    }

    return "{$temp1} {$temp2} {$firstname} {$secondname}"
}

###############################################################################
# Get a revision of a file
#   f       file name
#   index   index in finfo array
#   r       revision, "" for head revision
###############################################################################

proc get-file-rev {f index {r ""}} {
    global finfo
    global opts
    global tcl_platform

    if {"$r" == ""} {
        set rev "HEAD"
        set cvsopt  ""
        set rcsopt  ""
        set sccsopt ""
        set pvcsopt ""
        set p4file "$f"
    } else {
        set rev "r$r"
        set cvsopt  "-r $r"
        set rcsopt  "$r"
        set sccsopt "-r$r"
        set pvcsopt "-r$r"
        set p4file "$f#$r"
    }

    set finfo(pth,$index) [tmpfile $index]
    set finfo(tmp,$index) 1

    # NB: it would probably be a Good Thing to move the definition
    # of the various command to exec, to the preferences dialog.

    set dirname [file dirname $f]
    set tailname [file tail $f]

    # For CVS, if it isn't checked out there is neither a CVS nor RCS
    # directory.  It will however have a ,v suffix just like rcs.
    # There is not necessarily a RCS directory for RCS, either.  The file
    # always has a ,v suffix.

    if {[file isdirectory [file join $dirname CVS]]} {
        set cmd "cvs"
        if {$tcl_platform(platform) == "windows"} {append cmd ".exe"}
        set finfo(lbl,$index) "$f (CVS $rev)"
        die-unless "exec $cmd update -p $cvsopt $f" $finfo(pth,$index)

    } elseif {[file isdirectory [file join $dirname SCCS]]} {
        set cmd "sccs"
        if {$tcl_platform(platform) == "windows"} {append cmd ".exe"}
        set finfo(lbl,$index) "$f (SCCS $rev)"
        die-unless "exec $cmd get -p $sccsopt $f" $finfo(pth,$index)


     } elseif {[file isdirectory [file join $dirname RCS]]} {
        set cmd "co"
        if {$tcl_platform(platform) == "windows"} {append cmd ".exe"}
        set finfo(lbl,$index) "$f (RCS $rev)"
        die-unless "exec $cmd -p$rcsopt $f" $finfo(pth,$index)

    } elseif {[regexp {,v$} $tailname]} {
        set cmd "co"
        if {$tcl_platform(platform) == "windows"} {append cmd ".exe"}
        set finfo(lbl,$index) "$f (RCS $rev)"
        die-unless "exec $cmd -p$rcsopt $f" $finfo(pth,$index)

    } elseif {[file exists [file join $dirname vcs.cfg]]} {
        set cmd "get"
        if {$tcl_platform(platform) == "windows"} {append cmd ".exe"}
        set finfo(lbl,$index) "$f (PVCS $rev)"
        die-unless "exec $cmd -p $pvcsopt $f" $finfo(pth,$index)
        filterCRCRLF $finfo(pth,$index)

    } elseif {[info exists ::env(P4CLIENT)]} {
        set cmd "p4"
        if {$tcl_platform(platform) == "windows"} {append cmd ".exe"}
        set finfo(lbl,$index) "$f (Perforce $rev)"
        die-unless "exec $cmd print -q $p4file" $finfo(pth,$index)

    } else {
        fatal-error "File '$f' is not part of a revision control system."
    }
}

###############################################################################
# Setup ordinary file
#   f       file name
#   index   index in finfo array
###############################################################################

proc get-file {f index} {
    global finfo

    if {[file exists $f] != 1} {
        fatal-error "File '$f' does not exist."
    }
    if {[file isdirectory $f]} {
        fatal-error "'$f' is a directory."
    }

    set finfo(lbl,$index) "$f"
    set finfo(pth,$index) "$f"
    set finfo(tmp,$index) 0
}

###############################################################################
# Initialize file variables.
###############################################################################

proc init-files {} {
    global argc argv
    global finfo
    global opts
    global g

    set g(initOK) 0
    set argindex 0
    set revs 0
    set pths 0
    set conflict 0

    # Loop through argv, storing revision args in rev and file args in
    # finfo. revs and pths are counters.
    while {$argindex < $argc} {
        set arg [lindex $argv $argindex]
        switch -regexp -- $arg {
            "^-r$" {
                incr argindex
                incr revs
                set rev($revs) [lindex $argv $argindex]
            }
            "^-r.*" {
                incr revs
                set rev($revs) [string range $arg 2 end]
            }
            "^-conflict$" {
                set conflict 1
            }
            "^-" {
                append opts(diffcmd) " $arg "
            }
            default {
                incr pths
                set finfo(pth,$pths) $arg
            }
        }
        incr argindex
    }

    # Now check how many revision and file args we have.
    if {$conflict} {
        if {$revs == 0 && $pths == 1} {
            ############################################################
            # tkdiff -conflict FILE
            ############################################################
            set files [split-cvs-conflicts "$finfo(pth,1)"]
            get-file [lindex "$files" 0] 1
            get-file [lindex "$files" 1] 2
            set finfo(lbl,1) [lindex "$files" 2]
            set finfo(lbl,2) [lindex "$files" 3]
        } else {
            fatal "Usage: tkdiff -conflict FILE"
        }
    } else {
        if {$revs == 2 && $pths == 1} {
            ############################################################
            #  tkdiff -rREV1 -rREV2 FILE
            ############################################################
            set f $finfo(pth,1)
            get-file-rev "$f" 1 "$rev(1)"
            get-file-rev "$f" 2 "$rev(2)"

        } elseif {$revs == 2 && $pths == 0} {
            ############################################################
            #  tkdiff -rREV -r FILE
            ############################################################
            set f $rev(2)
            get-file-rev "$f" 1 "$rev(1)"
            get-file-rev "$f" 2

        } elseif {$revs == 1 && $pths == 1} {
            ############################################################
            #  tkdiff -rREV FILE
            ############################################################
            set f $finfo(pth,1)
            get-file-rev "$f" 1 "$rev(1)"
            get-file "$f" 2

        } elseif {$revs == 1 && $pths == 0} {
            ############################################################
            # tkdiff -r FILE
            ############################################################
            set f $rev(1)
            get-file-rev "$f" 1
            get-file "$f" 2

        } elseif {$revs == 0 && $pths == 2} {
            ############################################################
            #  tkdiff FILE1 FILE2
            ############################################################
            set f1 $finfo(pth,1)
            set f2 $finfo(pth,2)
            if {[file isdirectory $f1] && [file isdirectory $f2]} {
                fatal-error "Either <file1> or <file2> must be a plain file."
            }

            if {[file isdirectory $f1]} {
                set f1 [file join $f1 [file tail $f2]]
            } elseif {[file isdirectory $f2]} {
                set f2 [file join $f2 [file tail $f1]]
            }

            get-file "$f1" 1
            get-file "$f2" 2

        } elseif {$revs == 0 && $pths == 1} {
            ############################################################
            #  tkdiff FILE
            ############################################################
            set f $finfo(pth,1)
            get-file-rev "$f" 1
            get-file "$f" 2

        } else {
            do-error "Invalid command line!\n    $argv\nSee the help for valid command line parameters."
            do-usage
            tkwait window .usage
            destroy .
            error "Fatal"
        }
    }

    set finfo(title) "$finfo(lbl,1) vs. $finfo(lbl,2)"
    set rootname [file rootname  $finfo(pth,1)]
#    set path     [file dirname   $finfo(pth,1)]
    set path [pwd]
    set suffix   [file extension $finfo(pth,1)]
    set g(mergefile) [file join $path "${rootname}-merge$suffix"]
    set g(initOK) 1
}

###############################################################################
# Set up the display...
###############################################################################
proc create-display {} {

    global g opts bg tk_version
    global w

    # these are the four major areas of the GUI:
    # menubar - the menubar (duh)
    # toolbar - the toolbar (duh, again)
    # client  - the area with the text widgets and the graphical map
    # status us  - a bottom status line

    # this block of destroys is only for stand-alone testing of
    # the GUI code, and can be blown away (or not, if we want to
    # be able to call this routine to recreate the display...)
    catch {
        destroy .menubar
        destroy .toolbar
        destroy .client
        destroy .map
        destroy .status
    }

    # create the top level frames and store them in a global
    # array..
    set w(client)  .client
    set w(menubar) .menubar
    set w(toolbar) .toolbar
    set w(status)  .status

    # other random windows...
    set w(preferences) .pref
    set w(findDialog) .findDialog
    set w(popupMenu)  .popupMenu

    # now, simply build all the pieces
    build-menubar
    build-toolbar
    build-client
    build-status
    build-popupMenu

    # ... and fit it all together...
    if {$g(nativeMenus)} {
        . configure -menu $w(menubar)
    } else {
        pack $w(menubar) -side top -fill x -expand n
    }
    pack $w(toolbar) -side top -fill x -expand n
    pack $w(client)  -side top -fill both -expand y
    pack $w(status)  -side bottom -fill x -expand n

    # Make sure temporary files get deleted
    bind . <Destroy> { del-tmp }

    # other misc. bindings
    common-navigation $w(LeftText) $w(LeftInfo) $w(LeftCB) \
            $w(RightText) $w(RightInfo) $w(RightCB)

    # normally, keyboard traversal using tab and shift-tab isn't
    # enabled for text widgets, since the default binding for these
    # keys is to actually insert the tab charater. Because all of
    # our text widgets are for display only, let's redefine the
    # default binding so the global <Tab> and <Shift-Tab> bindings
    # are used.
    bind Text <Tab>       {continue}
    bind Text <Shift-Tab> {continue}

    # if the user toggles scrollbar syncing, we want to make sure 
    # they sync up immediately
    trace variable opts(syncscroll) w toggleSyncScroll
    wm deiconify .
    focus -force $w(LeftText)
    update idletasks

    set g(started) 1
}

###############################################################################
# when the user changes the "sync scrollbars" option, we want to 
# sync up the left scrollbar with the right if they turn the option
# on
###############################################################################
proc toggleSyncScroll {args} {
    global opts
    global w

    if {$opts(syncscroll) == 1} {
	eval vscroll-sync {{}} [$w(RightText) yview]
    }
}

###############################################################################
# show the popup menu, optionally changing some of the entries based on
# where the user clicked
###############################################################################

proc show-popupMenu { x y } {
    global w
    global g

    set window [winfo containing $x $y]
    if {[winfo class $window] == "Text"} {
        $w(popupMenu) entryconfigure "Find..." -state normal
        $w(popupMenu) entryconfigure "Find Nearest*" -state normal
        $w(popupMenu) entryconfigure "Edit*" -state normal

        if {$window == $w(LeftText) || $window == $w(LeftInfo) || \
                $window == $w(LeftCB)} {
            $w(popupMenu) configure -title "File 1"
            set g(activeWindow) $w(LeftText)
        } else {
            $w(popupMenu) configure -title "File 2"
            set g(activeWindow) $w(RightText)
        }

    } else {
        $w(popupMenu) entryconfigure "Find..." -state disabled
        $w(popupMenu) entryconfigure "Find Nearest*" -state disabled
        $w(popupMenu) entryconfigure "Edit*" -state disabled
    }
    tk_popup $w(popupMenu) $x $y
}


###############################################################################
# build the right-click popup menu
###############################################################################

proc build-popupMenu {} {
    global w g

    # this routine assumes the other windows already exist...
    menu $w(popupMenu)
    foreach win [list LeftText RightText LeftInfo RightInfo \
            LeftCB RightCB mapCanvas] {
        bind $w($win) <3> {show-popupMenu %X %Y}
    }

    set m $w(popupMenu)
    $m add command -label "First Diff" -underline 0 \
            -command [list popupMenu first] \
            -accelerator "F"
    $m add command -label "Previous Diff" -underline 0 \
            -command [list popupMenu previous] \
            -accelerator "P"
    $m add command -label "Center Current Diff" -underline 0 \
            -command [list popupMenu center] \
            -accelerator "C"
    $m add command -label "Next Diff"  -underline 0 \
            -command [list popupMenu next] \
            -accelerator "N"
    $m add command -label "Last Diff" -underline 0 \
            -command [list popupMenu last] \
            -accelerator "L"
    $m add separator
    $m add command -label "Find Nearest Diff" -underline 0 \
            -command [list popupMenu nearest] \
            -accelerator "Double-Click"
    $m add separator
    $m add command -label "Find..." -underline 0 \
            -command [list popupMenu find]
    $m add command -label "Edit" -underline 0 \
        -command [list popupMenu edit]
}

###############################################################################
# handle popup menu commands
###############################################################################
proc popupMenu {command args} {
    global g
    global w

    switch $command {
        center          {$w(centerDiffs) invoke}
        edit            {do-edit}
        find            {$w(find)        invoke}
        first           {$w(firstDiff)   invoke}
        last            {$w(lastDiff)    invoke}
        next            {$w(nextDiff)    invoke}
        previous        {$w(prevDiff)    invoke}
        nearest         {
            moveNearest $g(activeWindow) xy \
                    [winfo pointerx $g(activeWindow)] \
                    [winfo pointery $g(activeWindow)]
        }
    }
}

###############################################################################
# build the main client display (the text widgets, scrollbars, that
# sort of fluff)
###############################################################################

proc build-client {} {
    global g
    global w
    global opts

    frame $w(client)  -bd 2 -relief flat

    # set up global variables to reference the widgets, so
    # we don't have to use hardcoded widget paths elsewhere
    # in the code
    #
    # Text  - holds the text of the file
    # Info  - sort-of "invisible" text widget which is kept in sync
    #         with the text widget and holds line numbers
    # CB    - contains changebars or status or something like that...
    # VSB   - vertical scrollbar
    # HSB   - horizontal scrollbar
    # Label - label to hold the name of the file
    set w(LeftText)  $w(client).left.text
    set w(LeftInfo)  $w(client).left.info
    set w(LeftCB)    $w(client).left.changeBars
    set w(LeftVSB)   $w(client).left.vsb
    set w(LeftHSB)   $w(client).left.hsb
    set w(LeftLabel) $w(client).leftlabel

    set w(RightText)  $w(client).right.text
    set w(RightInfo)  $w(client).right.info
    set w(RightCB)    $w(client).right.changeBars
    set w(RightVSB)   $w(client).right.vsb
    set w(RightHSB)   $w(client).right.hsb
    set w(RightLabel) $w(client).rightlabel

    set w(map)        $w(client).map
    set w(mapCanvas)  $w(map).canvas

    # these don't need to be global...
    set leftFrame  $w(client).left
    set rightFrame $w(client).right

    # we'll create each widget twice; once for the left side
    # and once for the right.
    label $w(LeftLabel) \
            -bd 1 -relief flat \
            -textvariable finfo(lbl,1)

    label $w(RightLabel) \
            -bd 1 -relief flat \
            -textvariable finfo(lbl,2)

    # this holds the text widgets and the scrollbars. The reason
    # for the frame is purely for aesthetics. It just looks
    # nicer, IMHO, to "embed" the scrollbars within the text
    # widget
    frame $leftFrame \
            -bd 1 -relief sunken

    frame $rightFrame \
            -bd 1 -relief sunken

    scrollbar $w(LeftHSB) \
            -borderwidth 1 \
            -orient horizontal \
            -command [list $w(LeftText) xview]

    scrollbar $w(RightHSB) \
            -borderwidth 1 \
            -orient horizontal \
            -command [list $w(RightText) xview]

    scrollbar $w(LeftVSB) \
            -borderwidth 1 \
            -orient vertical \
            -command [list $w(LeftText) yview]

    scrollbar $w(RightVSB) \
            -borderwidth 1 \
            -orient vertical \
            -command [list $w(RightText) yview]

    scan $opts(geometry) "%dx%d" width height

    text $w(LeftText) \
            -padx 4 \
            -wrap none \
            -width $width \
            -height $height \
            -borderwidth  0 \
            -setgrid 1 \
            -yscrollcommand [list vscroll-sync "$w(LeftInfo) $w(LeftCB)" 1] \
            -xscrollcommand [list hscroll-sync 1]

    text $w(RightText) \
            -padx 4 \
            -wrap none \
            -width $width \
            -height $height \
            -borderwidth  0 \
            -setgrid 1 \
            -yscrollcommand [list vscroll-sync "$w(RightInfo) $w(RightCB)" 2] \
            -xscrollcommand [list hscroll-sync 2]

    text $w(LeftInfo) \
            -height 0 \
            -padx 0 \
            -width 6 \
            -borderwidth 0 \
            -setgrid 1 \
            -yscrollcommand [list vscroll-sync "$w(LeftCB) $w(LeftText)" 1]

    text $w(RightInfo) \
            -height 0 \
            -padx 0 \
            -width 6 \
            -borderwidth 0 \
            -setgrid 1 \
            -yscrollcommand [list vscroll-sync "$w(RightCB) $w(RightText)" 2]

    # each and every line in a text window will have a corresponding line
    # in this widget. And each line in this widget will be composed of
    # a single character (either "+", "-" or "!" for insertion, deletion
    # or change, respectively
    text $w(LeftCB) \
            -height 0 \
            -padx 0 \
            -highlightthickness 0 \
            -wrap none \
            -foreground white \
            -width 1 \
            -borderwidth 0 \
            -yscrollcommand [list vscroll-sync "$w(LeftInfo) $w(LeftText)" 1]

    text $w(RightCB) \
            -height 0 \
            -padx 0 \
            -highlightthickness 0 \
            -wrap none \
            -background white \
            -foreground white \
            -width 1 \
            -borderwidth 0 \
            -yscrollcommand [list vscroll-sync "$w(RightInfo) $w(RightText)" 2]

    # Set up text tags for the 'current diff' (the one chosen by the 'next'
    # and 'prev' buttons) and any ol' diff region.  All diff regions are
    # given the 'diff' tag initially...  As 'next' and 'prev' are pressed,
    # to scroll through the differences, one particular diff region is
    # always chosen as the 'current diff', and is set off from the others
    # via the 'diff' tag -- in particular, so that it's obvious which diffs
    # in the left and right-hand text widgets match.

    foreach widget [list $w(LeftText) $w(LeftInfo) $w(LeftCB) \
            $w(RightText) $w(RightInfo) $w(RightCB)] {
        eval "$widget configure $opts(textopt)"
        foreach tag {difftag currtag deltag instag chgtag + - !} {
            eval "$widget tag configure $tag $opts($tag)"
        }
    }

    # adjust the tag priorities a bit...
    foreach window [list LeftText RightText LeftCB RightCB LeftInfo RightInfo] {
        $w($window) tag raise deltag currtag
        $w($window) tag raise chgtag currtag
        $w($window) tag raise instag currtag
        $w($window) tag raise currtag difftag
    }

    # these tags are specific to change bars
    foreach widget [list $w(LeftCB) $w(RightCB)] {
        eval "$widget tag configure + $opts(+)"
        eval "$widget tag configure - $opts(-)"
        eval "$widget tag configure ! $opts(!)"
    }

    # build the map...
    # we want the map to be the same width as a scrollbar, so we'll
    # steal some information from one of the scrollbars we just
    # created...
    set cwidth [winfo reqwidth $w(LeftVSB)]
    set color  [$w(LeftVSB) cget -troughcolor]

    set map [frame $w(client).map \
            -bd 1 \
            -relief sunken \
            -takefocus 0 \
            -highlightthickness 0]

    # now for the real map...
    image create photo map

    canvas $w(mapCanvas) \
            -width [expr {$cwidth + 1}] \
            -yscrollcommand map-resize \
            -background $color \
            -borderwidth 0 \
            -relief sunken \
            -highlightthickness 0
    $w(mapCanvas) create image 1 1 -image map -anchor nw
    pack $w(mapCanvas) -side top -fill both -expand y

    # I'm not too pleased with these bindings -- it results in a rather
    # jerky, cpu-intensive maneuver since with each move of the mouse
    # we are finding and tagging the nearest diff. But, what *should*
    # it do?
    #
    # I think what I *want* it to do is update the combobox and status
    # bar so the user can see where in the scheme of things they are,
    # but not actually select anything until they release the mouse.
    bind $w(mapCanvas) <ButtonPress-1>   [list handleMapEvent B1-Press %y]
    bind $w(mapCanvas) <Button1-Motion>  [list handleMapEvent B1-Motion %y]
    bind $w(mapCanvas) <ButtonRelease-1> [list handleMapEvent B1-Release %y]

    # this is a dummy frame we're going to create that's the
    # same height as a horizontal scrollbar.
    frame $w(client).dummyFrame \
            -borderwidth 0 \
            -height \
            [winfo reqheight $w(LeftHSB)]

    # use grid to manage the widgets in the left side frame
    grid $w(LeftVSB)  -row 0 -column 0 -sticky ns
    grid $w(LeftInfo) -row 0 -column 1 -sticky nsew
    grid $w(LeftCB)   -row 0 -column 2 -sticky ns
    grid $w(LeftText) -row 0 -column 3 -sticky nsew
    grid $w(LeftHSB)  -row 1 -column 1 -sticky ew -columnspan 3

    grid rowconfigure $leftFrame 0 -weight 1
    grid rowconfigure $leftFrame 1 -weight 0

    grid columnconfigure $leftFrame 0 -weight 0
    grid columnconfigure $leftFrame 1 -weight 0
    grid columnconfigure $leftFrame 2 -weight 0
    grid columnconfigure $leftFrame 3 -weight 1

    # likewise for the right...
    grid $w(RightVSB)  -row 0 -column 3 -sticky ns
    grid $w(RightInfo) -row 0 -column 0 -sticky nsew
    grid $w(RightCB)   -row 0 -column 1 -sticky ns
    grid $w(RightText) -row 0 -column 2 -sticky nsew
    grid $w(RightHSB)  -row 1 -column 0 -sticky ew -columnspan 3

    grid rowconfigure $rightFrame 0 -weight 1
    grid rowconfigure $rightFrame 1 -weight 0

    grid columnconfigure $rightFrame 0 -weight 0
    grid columnconfigure $rightFrame 1 -weight 0
    grid columnconfigure $rightFrame 2 -weight 1
    grid columnconfigure $rightFrame 3 -weight 0

    # use grid to manage the labels, frames and map. We're going to
    # toss in an extra row just for the benefit of our dummy frame.
    # the intent is that the dummy frame will match the height of
    # the horizontal scrollbars so the map stops at the right place...
    grid $w(LeftLabel)         -row 0 -column 0 -sticky ew
    grid $w(RightLabel)        -row 0 -column 2 -sticky ew
    grid $leftFrame            -row 1 -column 0 -sticky nsew -rowspan 2
    grid $map                  -row 1 -column 1 -stick ns
    grid $w(client).dummyFrame -row 2 -column 1
    grid $rightFrame           -row 1 -column 2 -sticky nsew -rowspan 2

    grid rowconfigure $w(client) 0 -weight 0
    grid rowconfigure $w(client) 1 -weight 1
    grid rowconfigure $w(client) 2 -weight 0

    grid columnconfigure $w(client) 0 -weight 1
    grid columnconfigure $w(client) 1 -weight 0
    grid columnconfigure $w(client) 2 -weight 1

    # this adjusts the variable g(activeWindow) to be whatever text
    # widget has the focus...
    bind $w(LeftText)  <1> {set g(activeWindow) $w(LeftText)}
    bind $w(RightText) <1> {set g(activeWindow) $w(RightText)}

    set g(activeWindow) $w(LeftText) ;# establish a default

    # this will make the UI toe the line WRT user preferences
    do-show-map
    do-show-changebars
    do-show-linenumbers
    do-show-map

}

###############################################################################
# create (if necessary) and show the find dialog
###############################################################################

proc show-find {} {
    global w g

    if {![winfo exists $w(findDialog)]} {
        toplevel $w(findDialog)
        wm group $w(findDialog) .
        wm transient $w(findDialog) .
        wm title $w(findDialog) "$g(name) Find"

        # we don't want the window to be deleted, just hidden from view
        wm protocol $w(findDialog) WM_DELETE_WINDOW \
                [list wm withdraw $w(findDialog)]

        wm withdraw $w(findDialog)
        update idletasks

        frame $w(findDialog).content -bd 2 -relief groove
        pack $w(findDialog).content -side top -fill both -expand y \
                -padx 5 -pady 5

        frame $w(findDialog).buttons
        pack $w(findDialog).buttons -side bottom -fill x -expand n

        button $w(findDialog).buttons.doit -text "Find Next" -command do-find
        button $w(findDialog).buttons.dismiss \
                -text "Dismiss" \
                -command "wm withdraw $w(findDialog)"
        pack $w(findDialog).buttons.dismiss -side right -pady 5 -padx 5
        pack $w(findDialog).buttons.doit -side right -pady 5 -padx 1

        set ff $w(findDialog).content.findFrame
        frame $ff -height 100 -bd 2 -relief flat
        pack $ff -side top -fill x -expand n -padx 5 -pady 5

        label $ff.label -text "Find what:" -underline 2

        entry $ff.entry -textvariable g(findString)

        checkbutton $ff.searchCase \
                -text "Ignore Case" \
                -offvalue 0 \
                -onvalue 1 \
                -indicatoron true \
                -variable g(findIgnoreCase)

        grid $ff.label -row 0 -column 0 -sticky e
        grid $ff.entry -row 0 -column 1 -sticky ew
        grid $ff.searchCase -row 0 -column 2 -sticky w
        grid columnconfigure $ff 0 -weight 0
        grid columnconfigure $ff 1 -weight 1
        grid columnconfigure $ff 2 -weight 0

        # we need this in other places...
        set w(findEntry) $ff.entry

        bind $ff.entry <Return> do-find

        set of $w(findDialog).content.optionsFrame
        frame $of -bd 2 -relief flat
        pack $of -side top -fill y -expand y -padx 10 -pady 10

        label $of.directionLabel -text "Search Direction:"  -anchor e
        radiobutton $of.directionForward \
                -indicatoron true \
                -text "Down" \
                -value "-forward" \
                -variable g(findDirection)
        radiobutton $of.directionBackward \
                -text "Up" \
                -value "-backward" \
                -indicatoron true \
                -variable g(findDirection)


        label $of.windowLabel -text "Window:" -anchor e
        radiobutton $of.windowLeft \
                -indicatoron true \
                -text "Left" \
                -value $w(LeftText) \
                -variable g(activeWindow)
        radiobutton $of.windowRight \
                -indicatoron true \
                -text "Right" \
                -value $w(RightText) \
                -variable g(activeWindow)


        label $of.searchLabel -text "Search Type:" -anchor e
        radiobutton $of.searchExact \
                -indicatoron true \
                -text "Exact" \
                -value "-exact" \
                -variable g(findType)
        radiobutton $of.searchRegexp \
                -text "Regexp" \
                -value "-regexp" \
                -indicatoron true \
                -variable g(findType)

        grid $of.directionLabel    -row 1 -column 0 -sticky w
        grid $of.directionForward  -row 1 -column 1 -sticky w
        grid $of.directionBackward -row 1 -column 2 -sticky w

        grid $of.windowLabel    -row 0 -column 0 -sticky w
        grid $of.windowLeft     -row 0 -column 1 -sticky w
        grid $of.windowRight    -row 0 -column 2 -sticky w

        grid $of.searchLabel    -row 2 -column 0 -sticky w
        grid $of.searchExact    -row 2 -column 1 -sticky w
        grid $of.searchRegexp   -row 2 -column 2 -sticky w

        grid columnconfigure $of 0 -weight 0
        grid columnconfigure $of 1 -weight 0
        grid columnconfigure $of 2 -weight 1

        set g(findDirection) "-forward"
        set g(findType) "-exact"
        set g(findIgnoreCase) 1
        set g(lastSearch) ""
        if {$g(activeWindow) == ""} {
            set g(activeWindow) [focus]
            if {$g(activeWindow) != $w(LeftText) && \
                    $g(activeWindow) != $w(RightText)} {
                set g(activeWindow) $w(LeftText)
            }
        }
    }

    centerWindow $w(findDialog)
    wm deiconify $w(findDialog)
    after idle focus $w(findEntry)

}

###############################################################################
# do the "Edit->Copy" functionality, by copying the current selection
# to the clipboard
###############################################################################

proc do-copy {} {
    clipboard clear -displayof .
    # figure out which window has the selection...
    catch {
        clipboard append [selection get -displayof .]
    }
}

###############################################################################
# search for the text in the find dialog
###############################################################################

proc do-find {} {
    global g
    global w

    if {![winfo exists $w(findDialog)] || ![winfo ismapped $w(findDialog)]} {
        show-find
        return
    }

    set win $g(activeWindow)
    if {$win == ""} {set win $w(LeftText)}
    if {$g(lastSearch) != ""} {
        if {$g(findDirection) == "-forward"} {
            set start [$win index "insert +1c"]
        } else {
            set start insert
        }
    } else {
        set start 1.0
    }

    if {$g(findIgnoreCase)} {
        set result [$win search $g(findDirection) $g(findType) -nocase -- \
            $g(findString) $start]
    } else {
        set result [$win search $g(findDirection) $g(findType) -- \
            $g(findString) $start]
    }
    if {[string length $result] > 0} {
        # if this is a regular expression search, get the whole line and try
        # to figure out exactly what matched; otherwise we know we must
        # have matched the whole string...
        if {$g(findType) == "-regexp"} {
            set line [$win get $result "$result lineend"]
            regexp $g(findString) $line matchVar
            set length [string length $matchVar]
        } else {
            set length [string length $g(findString)]
        }
        set g(lastSearch) $result
        $win mark set insert $result
        $win tag remove sel 1.0 end
        $win tag add sel $result "$result + ${length}c"
        $win see $result
        focus $win
        # should I somehow snap to the nearest diff? Probably not...
    } else {
        bell;
    }
}
proc build-menubar {} {
    global tooltip
    global w
    global g

    if {$g(nativeMenus)} {
        menu $w(menubar)
    } else {
        frame $w(menubar) -bd 2 -relief flat
    }

    # this is just temporary shorthand ...
    set menubar $w(menubar)


    # First, the menu buttons...

    if {$g(nativeMenus)} {

        set fileMenu   $w(menubar).file
        set viewMenu   $w(menubar).view
        set helpMenu   $w(menubar).help
        set editMenu   $w(menubar).edit
        set mergeMenu  $w(menubar).window
	set markMenu   $w(menubar).marks

        $w(menubar) add cascade -label "File"  -menu $fileMenu  -underline 0
        $w(menubar) add cascade -label "Edit"  -menu $editMenu  -underline 0
        $w(menubar) add cascade -label "View"  -menu $viewMenu  -underline 0
	$w(menubar) add cascade -label "Mark" -menu $markMenu  -underline 3
        $w(menubar) add cascade -label "Merge" -menu $mergeMenu -underline 0
        $w(menubar) add cascade -label "Help"  -menu $helpMenu  -underline 0

    } else {
        # these are shorthand used only in this routine...
        set fileButton $menubar.fileButton
        set viewButton $menubar.viewButton
        set helpButton $menubar.helpButton
        set editButton $menubar.editButton
        set mergeButton $menubar.mergeButton
	set markButton  $menubar.markButton

        set fileMenu   $fileButton.file
        set viewMenu   $viewButton.view
        set helpMenu   $helpButton.help
        set editMenu   $editButton.edit
        set mergeMenu $mergeButton.window
	set markMenu  $markButton.marks

        menubutton $fileButton -text "File" -menu $fileMenu -underline 0
        menubutton $editButton -text "Edit" -menu $editMenu -underline 0
        menubutton $viewButton -text "View" -menu $viewMenu -underline 0
        menubutton $helpButton -text "Help" -menu $helpMenu -underline 0
        menubutton $mergeButton -text "Merge" -menu $mergeMenu -underline 0
	menubutton $markButton  -text "Mark" -menu $markMenu  -underline 3

        pack $fileButton $editButton $viewButton $markButton $mergeButton \
                -side left -fill none -expand n
        if {$::tcl_platform(platform) == "windows"} {
            pack $helpButton -side left -fill none -expand n
        } else {
            pack $helpButton -side right -fill none -expand n
        }
    }

    # these, however, are used in other places..
    set w(fileMenu) $fileMenu
    set w(viewMenu) $viewMenu
    set w(helpMenu) $helpMenu
    set w(editMenu) $editMenu
    set w(mergeMenu) $mergeMenu
    set w(markMenu)  $markMenu

    # Now, the menus...

    # Mark menu...
    menu $markMenu
    $markMenu add command -label "Mark Current Diff" \
	    -command [list diffmark set]
    $markMenu add command -label "Clear Current Diff Mark" \
	    -command [list diffmark clear]

    set "g(tooltip,Mark Current Diff)"  \
	    "Create a marker for the current difference record"
    set "g(tooltip,Clear Current Diff Mark)" \
	    "Clear the marker for the current difference record"

    # File menu...
    menu $fileMenu
    $fileMenu add command \
            -label "New..." \
            -underline 0 \
            -command [list do-new-diff]
    $fileMenu add separator
    $fileMenu add command \
            -label "Recompute Diffs" \
            -underline 0 \
            -command recompute-diff
    $fileMenu add command \
            -label "Write Report..." \
            -command [list write-report popup]
    $fileMenu add separator
    $fileMenu add command \
            -label "Exit" \
            -underline 1 \
            -command do-exit

    set "g(tooltip,Exit)" "Exit $g(name)"
    set "g(tooltip,Recompute Diffs)" \
            "Recompute and redisplay the difference records."
    set "g(tooltip,Write Report...)" \
            "Write the diff records to a file"

    # Edit menu...  If you change, add or remove labels, be sure and
    # update the tooltips.
    menu $editMenu
    $editMenu add command -label "Copy" -underline 0 -command do-copy
    $editMenu add separator
    $editMenu add command -label "Find..." -underline 0 -command show-find
    $editMenu add separator
    $editMenu add command -label "Edit File 1" \
        -command {global g w; set g(activeWindow) $w(LeftText) ; do-edit}
    $editMenu add command -label "Edit File 2" \
        -command {global g w; set g(activeWindow) $w(RightText) ; do-edit}
    $editMenu add separator
    $editMenu add command \
            -label "Preferences..." \
            -underline 3 \
            -command customize

    set "g(tooltip,Copy)"    \
            "Copy the currently selected text to the clipboard."
    set "g(tooltip,Find...)" \
            "Pop up a dialog to search for a string within either file."
    set "g(tooltip,Edit File 1)" \
            "Launch an editor on the file on the left side of the window."
    set "g(tooltip,Edit File 2)" \
            "Launch an editor on the file on the right side of the window."
    set "g(tooltip,Preferences...)"  \
            "Pop up a window to customize $g(name)."

    # View menu...  If you change, add or remove labels, be sure and
    # update the tooltips.
    menu $viewMenu
    $viewMenu add checkbutton \
            -label "Show Line Numbers" \
            -underline 12 \
            -variable opts(showln) \
            -command do-show-linenumbers

    $viewMenu add checkbutton \
            -label "Show Change Bars" \
            -underline 0 \
            -variable opts(showcbs) \
            -command do-show-changebars

    $viewMenu add checkbutton \
            -label "Show Diff Map" \
            -underline 0 \
            -variable opts(showmap) \
            -command do-show-map

    $viewMenu add separator

    $viewMenu add checkbutton \
            -label "Synchronize Scrollbars" \
            -underline 0 \
            -variable opts(syncscroll)
    $viewMenu add checkbutton -label "Auto Center" \
            -underline 0 \
            -variable opts(autocenter) \
            -command {if {$opts(autocenter)} {center}}
    $viewMenu add checkbutton -label "Auto Select" \
            -underline 1 \
            -variable opts(autoselect)

    $viewMenu add separator

    $viewMenu add command \
            -label "First Diff"  \
            -underline 0 \
            -command { move first } \
            -accelerator "F"
    $viewMenu add command \
            -label "Previous Diff"   \
            -underline 0 \
            -command { move -1 } \
            -accelerator "P"
    $viewMenu add command \
            -label "Center Current Diff" \
            -underline 0 \
            -command { center } \
            -accelerator "C"
    $viewMenu add command \
            -label "Next Diff"   \
            -underline 0 \
            -command { move 1 } \
            -accelerator "N"
    $viewMenu add command \
            -label "Last Diff"   \
            -underline 0 \
            -command { move last } \
            -accelerator "L"

    set "g(tooltip,Show Change Bars)" \
            "If set, show the changebar column for each line of each file"
    set "g(tooltip,Show Line Numbers)"  \
            "If set, show line numbers beside each line of each file"
    set "g(tooltip,Synchronize Scrollbars)"  \
            "If set, scrolling either window will scroll both windows."
    set "g(tooltip,Diff Map)"  \
            "If set, display the graphical \"Difference Map\" in the center of the display."
    set "g(tooltip,Auto Select)" \
            "If set, automatically selects the nearest diff record while scrolling"
    set "g(tooltip,Auto Center)"  \
            "If set, moving to another diff record will center the diff on the screen."
    set "g(tooltip,Center Current Diff)"  \
            "Center the display around the current diff record."
    set "g(tooltip,First Diff)"  \
            "Go to the first difference."
    set "g(tooltip,Last Diff)"   \
            "Go to the last difference."
    set "g(tooltip,Previous Diff)"  \
            "Go to the diff record just prior to the current diff record."
    set "g(tooltip,Next Diff)"  \
            "Go to the diff record just after the current diff record."

    # Merge menu. If you change, add or remove labels, be sure and
    # update the tooltips.
    menu $mergeMenu
    $mergeMenu add checkbutton \
            -label "Show Merge Window" \
            -underline 9 \
            -variable g(showmerge) \
            -command do-show-merge
    $mergeMenu add command -label "Write Merge File" -underline 6 \
            -command popup-merge
    set "g(tooltip,Show Merge Window)"  \
            "Pops up a window showing the current merge results."
    set "g(tooltip,Write Merge File)"  \
            "Write the merge file to disk. You will be prompted for a filename."

    # Help menu. If you change, add or remove labels, be sure and
    # update the tooltips.
    menu $helpMenu
    $helpMenu add command -label "On GUI" -underline 3 -command do-help
    $helpMenu add command -label "On Command Line" -underline 3 -command do-usage
    $helpMenu add command -label "On Preferences" -underline 3 -command do-help-preferences
    $helpMenu add separator
    $helpMenu add command -label "About $g(name)" -underline 0 -command do-about

    bind $fileMenu  <<MenuSelect>> {showTooltip menu %W}
    bind $editMenu  <<MenuSelect>> {showTooltip menu %W}
    bind $viewMenu  <<MenuSelect>> {showTooltip menu %W}
    bind $markMenu  <<MenuSelect>> {showTooltip menu %W}
    bind $mergeMenu <<MenuSelect>> {showTooltip menu %W}
    bind $helpMenu  <<MenuSelect>> {showTooltip menu %W}

    set "g(tooltip,On Preferences)" \
            "Show help on the user-settable preferences"
    set "g(tooltip,On GUI)"  \
            "Show help on how to use the Graphical User Interface"
    set "g(tooltip,On Command Line)"  \
            "Show help on the command line arguments"
    set "g(tooltip,About $g(name))"  \
            "Show information about this application"
}

proc showTooltip {which w} {
    global tooltip
    global g
    switch $which {
        menu {
            if {[catch {$w entrycget active -label} label]} {
                set label ""
            }
            if {[info exists g(tooltip,$label)]} {
                set g(statusInfo) $g(tooltip,$label)
            } else {
                set g(statusInfo) $label
            }
            update idletasks
        }

        button {
            if {[info exists g(tooltip,$w)]} {
                set g(statusInfo) $g(tooltip,$w)
            } else {
                set g(statusInfo) ""
            }
            update idletasks
        }
    }
}

proc build-toolbar {} {
    global w g

    frame $w(toolbar) -bd 2 -relief groove
    set toolbar $w(toolbar)

    # these are shorthand used only in this routine...
    set find            $toolbar.find
    set prevDiff        $toolbar.prev
    set firstDiff       $toolbar.first
    set lastDiff        $toolbar.last
    set nextDiff        $toolbar.next
    set centerDiffs     $toolbar.center
    set mergeChoice1    $toolbar.m1
    set mergeChoice2    $toolbar.m2
    set mergeChoiceLbl  $toolbar.mlabel
    set currentPos      $toolbar.cp
    set combo           $toolbar.combo
    set rediff          $toolbar.rediff
    set markclear       $toolbar.clearMark
    set markset         $toolbar.setMark

    # these, however, are used in other places..
    set w(find)             $find
    set w(prevDiff)         $prevDiff
    set w(firstDiff)        $firstDiff
    set w(lastDiff)         $lastDiff
    set w(nextDiff)         $nextDiff
    set w(centerDiffs)      $centerDiffs
    set w(mergeChoice1)     $mergeChoice1
    set w(mergeChoice2)     $mergeChoice2
    set w(currentPos)       $currentPos
    set w(combo)            $combo
    set w(mergeChoiceLabel) $mergeChoiceLbl
    set w(rediff)           $rediff
    set w(markSet)          $markset
    set w(markClear)        $markclear

    label $currentPos -textvariable g(pos)

    # some separators we'll use in other places
    toolsep $toolbar.sep1
    toolsep $toolbar.sep2
    toolsep $toolbar.sep3
    toolsep $toolbar.sep4
    toolsep $toolbar.sep5
    toolsep $toolbar.sep6
    toolsep $toolbar.sep7
    toolsep $toolbar.sep8

    # rediff...
    toolbutton $rediff -text "Rediff" -width 6 -command recompute-diff

    # find...
    toolbutton $find -text "Find" -width 5 -command do-find -bd 1

    # navigation widgets
    toolbutton $prevDiff  -text "Prev"  -width 5 -command [list move -1] -bd 1
    toolbutton $nextDiff  -text "Next"  -width 5 -command [list move 1] -bd 1
    toolbutton $firstDiff -text "First" -width 5 -command [list move first] -bd 1
    toolbutton $lastDiff  -text "Last" -width 5 -command [list move last] -bd 1
    toolbutton $centerDiffs -text "Center" -width 5 -command center -bd 1

    toolbutton $markset -text "Set Mark" \
	    -width 10 -command [list diffmark set] -bd 1
    toolbutton $markclear -text "Clear Mark" \
	    -width 10 -command [list diffmark clear] -bd 1

    ::combobox::combobox $combo -editable false -width 30 -command moveTo

    # the merge widgets
    radiobutton $mergeChoice2 \
	    -borderwidth 1 \
            -indicatoron true \
            -text Right \
            -value 2 \
            -variable g(toggle) \
            -command [list do-merge-choice 2] \
            -takefocus 0
    radiobutton $mergeChoice1 \
	    -borderwidth 1 \
            -indicatoron true \
            -text Left \
            -value 1 \
            -variable g(toggle) \
            -command [list do-merge-choice 1] \
            -takefocus 0

    # this is gross. We want the label next to the radiobuttons to
    # be disabled if the radiobuttons are disabled. But, labels can't
    # be disabled, so we'll use a "dead" button
    button $mergeChoiceLbl -text "Merge Choice:" -borderwidth 0 -command {} \
            -highlightthickness 0

    pack $combo -side left -padx 2
    pack $toolbar.sep1 -side left -fill y -pady 2 -padx 2
    pack $rediff -side left -padx 2
    pack $toolbar.sep6 -side left -fill y -pady 2 -padx 2
    pack $find -side left -padx 2
    pack $toolbar.sep2 -side left -fill y -pady 2 -padx 2
    pack $mergeChoiceLbl $mergeChoice1 $mergeChoice2  -side left -padx 2
    pack $toolbar.sep5 -side left -fill y -pady 2 -padx 3
    pack $firstDiff $prevDiff $nextDiff $lastDiff \
            -side left  -pady 2 -padx 0
    pack $toolbar.sep3 -side left -fill y -pady 2 -padx 2
    pack $centerDiffs -side left  -pady 2 -padx 0
    pack $toolbar.sep7 -side left -fill y -pady 2 -padx 2
    pack $markset $markclear -side left -padx 2
    pack $toolbar.sep8 -side left -fill y -pady 2 -padx 2

    # these bindings provide pseudo-tooltips. Note that if some menu
    # items change, these references need to be updated... Also, we
    # assume the menubar tooltips have already been defined....
    set g(tooltip,$markset)   $g(tooltip,Mark Current Diff)
    set g(tooltip,$markclear) $g(tooltip,Clear Current Diff Mark)

    set g(tooltip,$combo)       "Shows current difference record; allows you to go to a specific difference."
    set g(tooltip,$prevDiff)    $g(tooltip,Previous Diff);
    set g(tooltip,$nextDiff)    $g(tooltip,Next Diff);
    set g(tooltip,$firstDiff)   $g(tooltip,First Diff);
    set g(tooltip,$lastDiff)    $g(tooltip,Last Diff);
    set g(tooltip,$centerDiffs) $g(tooltip,Center Current Diff);
    set g(tooltip,$find)        $g(tooltip,Find...);
    set g(tooltip,$rediff)      $g(tooltip,Recompute Diffs);
    set g(tooltip,$mergeChoice1) \
            "select the diff record on the left for merging"
    set g(tooltip,$mergeChoice2) \
            "select the diff record on the right for merging"

    # the toolbuttons have support for tooltips, the combobox and
    # radiobuttons do not. But, we can use the same callback.
    foreach widget [list $combo $mergeChoice1 $mergeChoice2] {
        bind $widget <Enter>    +[list toolbutton:handleEvent <Enter> %W 0]
        bind $widget <Leave>    +[list toolbutton:handleEvent <Leave> %W 0]
        bind $widget <FocusIn>  +[list toolbutton:handleEvent <FocusIn> %W 0]
        bind $widget <FocusOut> +[list toolbutton:handleEvent <FocusOut> %W 0]
    }

    # this adjusts the image or label on the buttons according to the
    # user preferences
    reconfigure-toolbar
}

proc reconfigure-toolbar {} {
    global opts
    global w

    # standard button reliefs
    foreach button [list prevDiff nextDiff firstDiff lastDiff \
            centerDiffs find markSet markClear rediff] {
        if {$opts(fancyButtons)} {
            $w($button) configure -relief flat
        } else {
            $w($button) configure -relief raised
        }
    }

    # diff mark buttons relief
    foreach widget [info commands $w(toolbar).mark*] {
        if {$opts(fancyButtons)} {
            $widget configure -relief flat
        } else {
            $widget configure -relief raised
        }
    }
	
    # standard button images and labels
    foreach button [list prevDiff nextDiff firstDiff lastDiff \
	    centerDiffs find markSet markClear rediff] {
	if {$opts(toolbarIcons)} {
	    $w($button) configure -width 20 -image ${button}Image
	} else {
	    if {$button == "markSet" || $button == "markClear"} {
		$w($button) configure -width 10 -image {} 
	    } else {
		$w($button) configure -width 5 -image {} 
	    }
	} 
    }

    # merge choice buttons images and labels
    if {$opts(toolbarIcons)} {
	foreach button [list mergeChoice1 mergeChoice2] {
	    $w($button) configure -indicatoron false -image ${button}Image
	}
	# this, in effect, hides the text of the label without
	# actually destroying it
	$w(mergeChoiceLabel) configure -image nullImage

    } else {
	$w(mergeChoiceLabel) configure -image {}
	foreach button [list mergeChoice1 mergeChoice2] {
	    $w($button) configure -indicatoron true -image {}
	}
    }
}

proc build-status {} {
    global w
    global g

    frame $w(status)  -bd 1 -relief flat

    set w(statusLabel) $w(status).label
    set w(statusCurrent) $w(status).current

    label $w(statusCurrent) \
            -textvariable g(statusCurrent) \
            -anchor e \
            -width 14 \
            -borderwidth 1 \
            -relief sunken \
            -padx 4 \
            -pady 2
    label $w(statusLabel) \
            -textvariable g(statusInfo) \
            -anchor w \
            -width 1 \
            -borderwidth 1 \
            -relief sunken \
            -pady 2
    pack $w(statusCurrent) -side right -fill y -expand n
    pack $w(statusLabel) -side left -fill both -expand y
}

###############################################################################
# handles events over the map
###############################################################################
proc handleMapEvent {event y} {
    global opts
    global w
    global g

    switch $event {

        B1-Press {
            set ty1 [lindex $g(thumbBbox) 1]
            set ty2 [lindex $g(thumbBbox) 3]
            if {$y >= $ty1 && $y <= $ty2} {
                set g(mapScrolling) 1
            }
        }

        B1-Motion {
            if {[info exists g(mapScrolling)]} {
                map-seek $y
            }
        }

        B1-Release {
            show-info ""
            set ty1 [lindex $g(thumbBbox) 1]
            set ty2 [lindex $g(thumbBbox) 3]
            # if we release over the trough (actually, *not* over the thumb),
            # just scroll by the size of the thumb
            if {$y < $ty1 || $y > $ty2} {
                if {$y < $ty1} {
                    # if vertical scrollbar syncing is turned on,
                    # all the other windows should toe the line
                    # appropriately...
                    $w(RightText) yview scroll -1 pages
                } else {
                    $w(RightText) yview scroll 1 pages
                }

            } else {
                # do nothing
            }

            catch {unset g(mapScrolling)}
        }
    }
}

# makes a toolbar "separator"
proc toolsep {w} {
    label $w -image [image create photo] -highlightthickness 0 -bd 1 \
            -width 0 -relief groove
    return $w
}

proc toolbutton {w args} {
    global tcl_platform
    global opts

    # create the button
    eval button $w $args

    # add minimal tooltip-like support
    bind $w <Enter>    [list toolbutton:handleEvent <Enter> %W]
    bind $w <Leave>    [list toolbutton:handleEvent <Leave> %W]
    bind $w <FocusIn>  [list toolbutton:handleEvent <FocusIn> %W]
    bind $w <FocusOut> [list toolbutton:handleEvent <FocusOut> %W]

    # give a taste of the MS Windows "look and feel"
    if {$opts(fancyButtons)} {
        $w configure -relief flat
    }

    return $w
}

# handle events in our fancy toolbuttons...
proc toolbutton:handleEvent {event w {isToolbutton 1}} {
    global g
    global opts

    switch $event {
        "<Enter>" {
            showTooltip button $w
            if {$opts(fancyButtons) && $isToolbutton && \
                [$w cget -state] == "normal"} {
                $w configure -relief raised
            }
        }
        "<Leave>" {
            set g(statusInfo) ""
            if {$opts(fancyButtons) && $isToolbutton} {
                $w configure -relief flat
            }
        }
        "<FocusIn>" {
            showTooltip button $w
            if {$opts(fancyButtons) && $isToolbutton && \
                [$w cget -state] == "normal"} {
                $w configure -relief raised
            }
        }
        "<FocusOut>" {
            set g(statusInfo) ""
            if {$opts(fancyButtons) && $isToolbutton} {
                $w configure -relief flat
            }
        }
    }
}

###############################################################################
# move the map thumb to correspond to current shown merge...
###############################################################################
proc map-move-thumb {y1 y2} {
    global g
    global finfo
    global w

    set thumbheight [expr {($y2 - $y1) * $g(mapheight)}]
    if {$thumbheight < $g(thumbMinHeight)} {
        set thumbheight $g(thumbMinHeight)
    }

    if {![info exists g(mapwidth)]} {set g(mapwidth) 0}
    set x1 1
    set x2 [expr {$g(mapwidth) - 3}]

    # why -2? it's the thickness of our border...
    set y1 [expr {int(($y1 * $g(mapheight)) - 2)}]
    if {$y1 < 0} {set y1 0}

    set y2 [expr {$y1 + $thumbheight}]
    if {$y2 > $g(mapheight)} {
        set y2 $g(mapheight)
        set y1 [expr {$y2 - $thumbheight}]
    }

    set dx1 [expr {$x1 + 1}]
    set dx2 [expr {$x2 - 1}]
    set dy1 [expr {$y1 + 1}]
    set dy2 [expr {$y2 - 1}]

    $w(mapCanvas) coords thumbUL \
            $x1 $y2 $x1 $y1 $x2 $y1 $dx2 $dy1 $dx1 $dy1 $dx1 $dy2
    $w(mapCanvas) coords thumbLR \
            $dx1 $y2 $x2 $y2 $x2 $dy1 $dx2 $dy1 $dx2 $dy2 $dx1 $dy2

    set g(thumbBbox) [list $x1 $y1 $x2 $y2]
    set g(thumbHeight) $thumbheight
}

###############################################################################
# Bind keys for Next, Prev, Center, Merge choices 1 and 2
###############################################################################
proc common-navigation {args} {
    global w

    bind . <Control-f> do-find

    foreach widget $args {
        # this effectively disables the widget, without having to
        # resort to actually disabling the widget (the latter which
        # has some annoying side effects). What we really want is to
        # only disable keys that get inserted, but that's difficult
        # to do, and this works almost as well...
        bind $widget <KeyPress> {break};
        bind $widget <<Paste>> {break};

        # ... but now we need to restore some navigation key bindings
        # which got lost because we disable all keys.
        foreach event [list Next Prior Up Down Left Right Home End] {
            foreach modifier [list {} Shift Control Shift-Control] {
                bind $widget "<${modifier}${event}>" \
                        [bind Text "<${modifier}${event}>"]
            }
        }

        # these bindings allow control-f, tab and shift-tab to work
        # in spite of the fact we bound Any-KeyPress to a null action
        bind $widget <Control-f> continue;
        bind $widget <Tab> continue;
        bind $widget <Shift-Tab> continue;

        bind $widget <c> "$w(centerDiffs) invoke; break"
        bind $widget <n> "$w(nextDiff) invoke; break"
        bind $widget <p> "$w(prevDiff) invoke; break"
        bind $widget <f> "$w(firstDiff) invoke; break"
        bind $widget <l> "$w(lastDiff) invoke; break"
        bind $widget <Return> "moveNearest $widget mark insert;break"

        # these bindings keep Alt- modified keys from triggering
        # the above actions. This way, any Alt combinations that
        # should open a menu will...
        foreach key [list c n p f l] {
            bind $widget <Alt-$key> {continue}
        }

        bind $widget <Double-1> "moveNearest $widget xy %x %y; break"

        bind $widget <Key-1> "$w(mergeChoice1) invoke; break"
        bind $widget <Key-2> "$w(mergeChoice2) invoke; break"
    }
}

###############################################################################
# set or clear a "diff mark" -- a hot button to move to a particular diff
###############################################################################

proc diffmark {option {diff -1}}  {
    global g
    global w

    if {$diff == -1} {
	set diff $g(pos)
    }

    set widget $w(toolbar).mark$diff

    switch $option {
	activate {
	    move $diff 0 1
	}

	set {
	    if {![winfo exists $widget]} {
		toolbutton $widget \
			-text "\[$diff\]"  \
			-command [list diffmark activate $diff] \
			-bd 1
		pack $widget -side left -padx 2
		set g(tooltip,$widget) \
			"Diff Marker: Jump to diff record number $diff"
	    }
	    update-display
	}

	clear {
	    if {[winfo exists $widget]} {
		destroy $widget
		catch {unset g(tooltip,$widget)}
	    }
	    update-display
	}

	clearall {
	    foreach widget [info commands $w(toolbar).mark*] {
		destroy $widget
		catch {unset g(tooltip,$widget)}
	    }
	    update-display
	}
    }
}

###############################################################################
# Customize the display (among other things).
###############################################################################

proc customize {} {
    global pref
    global g
    global w
    global opts
    global tmpopts

    catch {destroy $w(preferences)}
    toplevel $w(preferences)

    wm title $w(preferences) "$g(name) Preferences"
    wm transient $w(preferences) .
    wm group $w(preferences) .

    wm withdraw $w(preferences)

    # the button frame...
    frame $w(preferences).buttons -bd 0
    button $w(preferences).buttons.dismiss \
            -width 8 \
            -text "Dismiss" \
            -command {destroy $w(preferences)}
    button $w(preferences).buttons.apply \
            -width 8 \
            -text "Apply" \
            -command apply
    button $w(preferences).buttons.save \
            -width 8 \
            -text "Save" \
            -command save

    button $w(preferences).buttons.help \
            -width 8 \
            -text "Help" \
            -command do-help-preferences

    pack $w(preferences).buttons -side bottom -fill x
    pack $w(preferences).buttons.dismiss -side right -padx 10 -pady 5
    pack $w(preferences).buttons.help    -side right -padx 10 -pady 5
    pack $w(preferences).buttons.save    -side right -padx 1  -pady 5
    pack $w(preferences).buttons.apply   -side right -padx 1  -pady 5

    # a series of checkbuttons to act as a poor mans notebook tab
    frame $w(preferences).notebook -bd 0
    pack $w(preferences).notebook -side top -fill x -pady 4
    set pagelist {}
    foreach page [list General Display Appearance] {
        set frame $w(preferences).f$page
        lappend pagelist $frame
        set rb $w(preferences).notebook.f$page
        radiobutton $rb \
                -command "customize-selectPage $frame" \
                -variable g(prefPage) \
                -value $frame \
                -text $page \
                -indicatoron false \
                -width 10 \
                -borderwidth 1

        pack $rb -side left

        frame $frame -bd 2 -relief groove -width 400 -height 300
    }
    set g(prefPage) $w(preferences).fGeneral

    # make sure our labels are defined
    customize-initLabels

    # this is an option that we support internally, but don't give
    # the user a way to directly edit (right now, anyway). But we 
    # need to make sure tmpopts knows about it
    set tmpopts(customCode) $opts(customCode)

    # General
    set count 0
    set frame $w(preferences).fGeneral
    foreach key {diffcmd tmpdir editor geometry} {
        label $frame.l$count -text "$pref($key): " -anchor w
        set tmpopts($key) $opts($key)
        entry $frame.e$count \
                -textvariable tmpopts($key) -width 50 \
                -bd 2 -relief sunken

        grid $frame.l$count -row $count -column 0 -sticky w -padx 5 -pady 2
        grid $frame.e$count -row $count -column 1 -sticky ew -padx 5 -pady 2

        incr count
    }

    # this is just for filler...
    label $frame.filler -text {}
    grid $frame.filler -row $count
    incr count

    foreach key {fancyButtons toolbarIcons autocenter syncscroll autoselect} {
        label $frame.l$count -text "$pref($key): " -anchor w
        set tmpopts($key) $opts($key)
        checkbutton $frame.c$count \
                -indicatoron true \
                -text "$pref($key)" \
                -justify left \
                -onvalue 1 \
                -offvalue 0 \
                -variable tmpopts($key)

        set tmpopts($key) $opts($key)

        grid $frame.c$count -row $count -column 0 -sticky w -padx 5 \
                -columnspan 2

        incr count
    }

    grid columnconfigure $frame 0 -weight 0
    grid columnconfigure $frame 1 -weight 1

    # this, in effect, adds a hidden row at the bottom which takes
    # up any extra room

    grid rowconfigure    $frame $count -weight 1

    # pack this window for a brief moment, and compute the window
    # size. We'll do this for each "page" and find the largest
    # size to be the size of the dialog
    pack $frame -side right -fill both -expand y
    update idletasks
    set maxwidth [winfo reqwidth $w(preferences)]
    set maxheight [winfo reqheight $w(preferences)]
    pack forget $frame

    # Appearance
    set frame $w(preferences).fAppearance
    set count 0
    foreach key {textopt difftag deltag instag chgtag currtag} {
        label $frame.l$count -text "$pref($key): " -anchor w
        set tmpopts($key) $opts($key)
        entry $frame.e$count \
                -textvariable tmpopts($key) \
                -bd 2 -relief sunken

        grid $frame.l$count -row $count -column 0 -sticky w  -padx 5 -pady 2
        grid $frame.e$count -row $count -column 1 -sticky ew -padx 5 -pady 2

        incr count
    }
    grid columnconfigure $frame 0 -weight 0
    grid columnconfigure $frame 1 -weight 1

    # this, in effect, adds a hidden row at the bottom which takes
    # up any extra room

    grid rowconfigure    $frame $count -weight 1

    pack $frame -side right -fill both -expand y
    update idletasks
    set maxwidth [max $maxwidth [winfo reqwidth $w(preferences)]]
    set maxheight [max $maxheight [winfo reqheight $w(preferences)]]
    pack forget $frame

    # Display
    set frame $w(preferences).fDisplay
    set row 0

    # Option fields
    # Note that the order of the list is used to determine
    # the layout. So, if you add something to the list pay
    # attention to how if affects things.
    #
    # an x means an empty column; a - means an empty row
    set col 0
    foreach key [list \
            showln       tagln      \
            showcbs      tagcbs     \
            showmap      colorcbs   \
            x            tagtext    \
            -                      ] {

        if {$key == "x"} {
            set col [expr {$col ? 0 : 1}]
            if {$col == 0} {incr row}
            continue
        }

        if {$key == "-"} {
            frame $frame.f${row} -bd 0 -height 4
            grid $frame.f${row} -row $row -column 0 -columnspan 2 \
                    -padx 20 -pady 4 -sticky nsew
            set col 1 ;# will force next column to zero and incr row

        } else {

            checkbutton $frame.c${row}${col} \
                    -indicatoron true \
                    -text "$pref($key)" \
                    -onvalue 1 \
                    -offvalue 0 \
                    -variable tmpopts($key)

            set tmpopts($key) $opts($key)

            grid $frame.c${row}$col -row $row -column $col -sticky w -padx 5
        }

        set col [expr {$col ? 0 : 1}]
        if {$col == 0} {incr row}
    }

    grid columnconfigure $frame 0 -weight 0
    grid columnconfigure $frame 1 -weight 0
    grid columnconfigure $frame 2 -weight 0
    grid columnconfigure $frame 3 -weight 0
    grid columnconfigure $frame 4 -weight 1

    # this, in effect, adds a hidden row at the bottom which takes
    # up any extra room

    grid rowconfigure    $frame $row -weight 1

    pack $frame -side right -fill both -expand y
    update idletasks
    set maxwidth [max $maxwidth [winfo reqwidth $w(preferences)]]
    set maxheight [max $maxheight [winfo reqheight $w(preferences)]]
    pack forget $frame

    customize-selectPage

    # compute a reasonable location for the window...
    centerWindow $w(preferences) [list $maxwidth $maxheight]

    wm deiconify $w(preferences)
}

proc customize-selectPage {{frame {}}} {
    global g w

    if {$frame == ""} {
        set frame $g(prefPage)
    }

    pack forget $w(preferences).fGeneral
    pack forget $w(preferences).fAppearance
    pack forget $w(preferences).fDisplay
    pack forget $w(preferences).fBehavior
    pack $frame -side right -fill both -expand y
}

###############################################################################
# define the labels for the preferences. This is done outside of
# the customize proc since the labels are used in the help text.
###############################################################################
proc customize-initLabels {} {
    global pref

    set pref(diffcmd)  {diff command}
    set pref(textopt)  {Text widget options}
    set pref(difftag)  {Tag options for diff regions}
    set pref(currtag)  {Tag options for the current diff region}
    set pref(deltag)   {Tag options for deleted diff region}
    set pref(instag)   {Tag options for inserted diff region}
    set pref(chgtag)   {Tag options for changed diff region}
    set pref(geometry) {Text window size}
    set pref(tmpdir)   {Directory for scratch files}
    set pref(editor)   {Program for editing files}

    set pref(fancyButtons) {Fancy toolbar buttons}
    set pref(showmap)    {Show graphical map of diffs}
    set pref(showln)     {Show line numbers}
    set pref(showcbs)    {Show change bars}
    set pref(autocenter) {Automatically center current diff region}
    set pref(syncscroll) {Synchronize scrollbars}
    set pref(toolbarIcons) {Use icons instead of labels in the toolbar}

    set pref(colorcbs)   {Color change bars to match the diff map}
    set pref(tagtext)    {Highlight file contents}
    set pref(tagcbs)     {Highlight change bars}
    set pref(tagln)      {Highlight line numbers}

    set pref(autoselect) \
            "Automaticallly select the nearest diff region while scrolling"

}

###############################################################################
# Apply customization changes.
###############################################################################

proc apply {} {
    global opts
    global tmpopts
    global w

    if {! [file isdirectory $tmpopts(tmpdir)]} {
        do-error "Invalid temporary directory $tmpopts(tmpdir)"
    }

    if {[catch "$w(LeftText) configure $tmpopts(textopt)
                $w(RightText) configure $tmpopts(textopt)"]} {
        do-error "Invalid settings for text widget: \n\n$tmpopts(textopt)"
        eval "$w(LeftText) configure $opts(textopt)"
        eval "$w(LeftInfo) configure $opts(textopt)"
        return
    }

    # the text options must be ok. Configure the other text widgets
    # similarly
    eval "$w(LeftCB)    configure $tmpopts(textopt)"
    eval "$w(LeftInfo)  configure $tmpopts(textopt)"
    eval "$w(RightCB)   configure $tmpopts(textopt)"
    eval "$w(RightInfo) configure $tmpopts(textopt)"

    if {$tmpopts(geometry) == "" || \
            [catch {scan $tmpopts(geometry) "%dx%d" width height} result]} {
        do-error "invalid geometry setting: $tmpopts(geometry)"
        return
    }
    if {[catch {$w(LeftText) configure -width $width -height $height} result]} {
        do-error "invalid geometry setting: $tmpopts(geometry)"
        return
    }
    $w(RightText) configure -width $width -height $height


    foreach tag {difftag currtag deltag instag chgtag} {
        foreach win [list $w(LeftText)  $w(LeftInfo)  $w(LeftCB) \
                          $w(RightText) $w(RightInfo) $w(RightCB)] {
            if {[catch "$win tag configure $tag $tmpopts($tag)"]} {
                do-error "Invalid settings\n\n$tmpopts($tag)"
                eval "$win tag configure $tag $opts($tag)"
                return
            }
        }
    }

    # set opts to the values from tmpopts
    foreach key {diffcmd textopt difftag currtag deltag instag chgtag \
                 tmpdir editor showmap showln showcbs autocenter syncscroll \
                 tagln tagcbs tagtext autoselect toolbarIcons \
                 geometry fancyButtons colorcbs} {
        set opts($key) $tmpopts($key)
    }

    # reconfigure the toolbar buttons
    reconfigure-toolbar

    # remark all the diff regions, show (or hide) the line numbers,
    # change bars and diff map, and we are done.
    remark-diffs
    do-show-linenumbers
    do-show-changebars
    do-show-map
}

###############################################################################
# Save customization changes.
###############################################################################

proc save {} {
    global g
    global tmpopts rcfile tcl_platform
    global pref

    if {[ file exists $rcfile ]} {
      file rename -force $rcfile "$rcfile~"
    }

    # Need to quote backslashes, replace single \ with double \\
    regsub -all {\\} $tmpopts(tmpdir) {\\\\} tmpdir

    set fid [open $rcfile w]

    # put the tkdiff version in the file. It might be handy later
    puts $fid "# This file was generated by $g(name) $g(version)"
    puts $fid "# [clock format [clock seconds]]\n"
    puts $fid "set prefsFileVersion {$g(version)}\n"

    # now, put all of the preferences in the file
    foreach key {diffcmd textopt difftag currtag deltag instag \
                 chgtag showmap showln showcbs autocenter syncscroll \
                 fancyButtons geometry editor colorcbs autoselect \
                 tagln tagcbs tagtext toolbarIcons } {
        regsub "\n" $pref($key) "\n# " comment
        puts $fid "# $comment"
        puts $fid "set opts($key) {$tmpopts($key)}\n"
    }

    # Seems we can't use {$tmpdir} here or embedded \\ don't translate to \

    puts $fid "# $pref(tmpdir)"
    puts $fid "set opts(tmpdir) \"$tmpdir\"\n"

    # ... and any custom code
    puts $fid "# custom code"
    puts $fid "# put any custom code you want to be executed in the"
    puts $fid "# following block. This code will be automatically executed"
    puts $fid "# after the GUI has been set up but before the diff is "
    puts $fid "# performed. Use this code to customize the interface if"
    puts $fid "# you so desire."
    puts $fid "#  "
    puts $fid "# Even though you can't (as of version 3.02) edit this "
    puts $fid "# code via the preferences dialog, it will be automatically"
    puts $fid "# saved and restored if you do a SAVE from that dialog."
    puts $fid ""
    puts $fid "# Unless you really know what you are doing, it is probably"
    puts $fid "# wise to leave this unmodified."
    puts $fid ""
    puts $fid "set opts(customCode) {\n[string trim $tmpopts(customCode)]\n}\n"

    close $fid

    if { $tcl_platform(platform) == "windows" } {
        file attribute $rcfile -hidden 1
    }
}

###############################################################################
# Text has scrolled, update scrollbars and synchronize windows
###############################################################################

proc hscroll-sync {id args} {
    global g opts
    global w

    # If ignore_event is true, we've already taken care of scrolling.
    # We're only interested in the first event.
    if {$g(ignore_hevent,$id)} {
        return
    }

    # Scrollbar sizes
    set size1 [expr {[lindex [$w(LeftText) xview] 1] - [lindex [$w(LeftText) xview] 0]}]
    set size2 [expr {[lindex [$w(RightText) xview] 1] - [lindex [$w(RightText) xview] 0]}]

    if {$opts(syncscroll) || $id == 1} {
        set start [lindex $args 0]

        if {$id != 1} {
            set start [expr {$start * $size2 / $size1}]
        }
        $w(LeftHSB) set $start [expr {$start + $size1}]
        $w(LeftText) xview moveto $start
        set g(ignore_hevent,1) 1
    }
    if {$opts(syncscroll) || $id == 2} {
        set start [lindex $args 0]
        if {$id != 2} {
            set start [expr {$start * $size1 / $size2}]
        }
        $w(RightHSB) set $start [expr {$start + $size2}]
        $w(RightText) xview moveto $start
        set g(ignore_hevent,2) 1
    }

    # This forces all the event handlers for the view alterations
    # above to trigger, and we lock out the recursive (redundant)
    # events using ignore_event.
    update idletasks
    # Restore to normal
    set g(ignore_hevent,1) 0
    set g(ignore_hevent,2) 0
}

###############################################################################
# Text has scrolled, update scrollbars and synchronize windows
###############################################################################

proc vscroll-sync {windowlist id y0 y1} {
    global g opts
    global w

    if {$id == 1} {
	$w(LeftVSB) set $y0 $y1
    } else {
	$w(RightVSB) set $y0 $y1
    }

    # if syncing is disabled, we're done. This prevents a nasty
    # set of recursive calls
    if {[info exists g(disableSyncing)]} {
        return
    }

    # set the flag; this makes sure we only get called once
    set g(disableSyncing) 1

    # scroll the other windows on the same side as this window
    foreach window $windowlist {
	$window yview moveto $y0
    }

    eval map-move-thumb $y0 $y1

    # Select nearest visible diff region, if the appropriate
    # options are set
    if {$opts(syncscroll) && $opts(autoselect) && $g(count) > 0} {
        set winhalf [expr {[winfo height $w(RightText)] / 2}]
        set result [find-diff [expr {int([$w(RightText) index @1,$winhalf])}]]
        set i [lindex $result 0]

        # have we found a diff other than the current diff?
        if {$i != $g(pos)} {
            # Also, make sure the diff is visible. If not, we won't
            # change the current diff region...
            set topline [$w(RightText) index @0,0]
            set bottomline [$w(RightText) index @0,10000]
            foreach {line s1 e1 s2 e2 type} $g(scrdiff,$i) {}
            if {$s1 >= $topline && $s1 <= $bottomline} {
                move $i 0 0
            }
        }
    }

    # if syncing is turned on, scroll other windows.
    # Annoyingly, sometimes the *Text windows won't scroll properly,
    # at least under windows. And I can't for the life of me figure
    # out why. Maybe a bug in tk?
    if {$opts(syncscroll)} {
	if {$id == 1} {

	    $w(RightText) yview moveto $y0
	    $w(RightInfo) yview moveto $y0
	    $w(RightCB)   yview moveto $y0
	    $w(RightVSB)  set $y0 $y1

	} else {

	    $w(LeftText) yview moveto $y0 
	    $w(LeftInfo) yview moveto $y0
	    $w(LeftCB)   yview moveto $y0
	    $w(LeftVSB)  set $y0 $y1
	}
    }

    # we apparently automatically process idle events after this
    # proc is called. Once that is done we'll unset our flag 
    after idle {catch {unset g(disableSyncing)}}

}

###############################################################################
# Make a miniature map of the diff regions
###############################################################################

proc create-map {map mapwidth mapheight} {
    global g
    global w

    # Text widget always contains blank line at the end
    set lines [expr {double([$w(LeftText) index end]) - 2}]
    set factor [expr {$mapheight / $lines}]

    # We add some transparent stuff to make the map fill the canvas
    # in order to receive mouse events at the very bottom.
    $map blank
    $map put \#000 -to 0 $mapheight $mapwidth $mapheight

    # Line numbers start at 1, not at 0.
    for {set i 1} {$i <= $g(count)} {incr i} {
#        scan $g(scrdiff,$i) "%s %d %d %d %d %s" line s1 e1 s2 e2 type
        foreach {line s1 e1 s2 e2 type} $g(scrdiff,$i) {}

        set y [expr {int(($s2 - 1) * $factor) + $g(mapborder)}]
        set size [expr {round(($e2 - $s2 + 1) * $factor)}]
        if {$size < 1} {
            set size 1
        }
        switch $type {
            "d" { set color red1 }
            "a" { set color green }
            "c" { set color blue }
        }

        $map put $color -to 0 $y $mapwidth [expr {$y + $size}]

    }

    # let's draw a rectangle to simulate a scrollbar thumb. The size
    # isn't important since it will get resized when map-move-thumb
    # is called...
    $w(mapCanvas) create line 0 0 0 0 -tags thumbUL -fill white
    $w(mapCanvas) create line 1 1 1 1 -tags thumbLR -fill black
    $w(mapCanvas) raise thumb

    # now, move the thumb
    eval map-move-thumb [$w(LeftText) yview]

}

###############################################################################
# Resize map to fit window size
###############################################################################

proc map-resize {args} {
    global g opts
    global w

    set mapwidth  [winfo width $w(map)]
    set g(mapborder) [expr { [$w(map) cget -borderwidth] + \
            [$w(map) cget -highlightthickness]}]
    set mapheight [expr {[winfo height $w(map)] - $g(mapborder) * 2}]

    # We'll get a couple of "resize" events, so don't draw a map
    # unless we've got the diffs and the map size has changed
    if {$g(count) == 0 || $mapheight == $g(mapheight)} {
        return
    }

    # If we don't have a map and don't want one, don't make one
    if {$g(mapheight) == 0 && $opts(showmap) == 0} {
        return
    }

    # This seems to happen on Windows!? _After_ the map is drawn the first time
    # another event triggers and [winfo height $w(map)] is then 0...
    if {$mapheight < 1} {
        return
    }

    set g(mapheight) $mapheight
    set g(mapwidth) $mapwidth
    create-map map $mapwidth $mapheight
}

###############################################################################
# scroll to diff region nearest to y
###############################################################################

proc map-scroll {y} {
    global g
    global w
    global opts

    set yview [expr {double ($y) / double($g(mapheight))}]
    # Show text corresponding to map
    catch {$w(RightText) yview moveto $yview} result
    update idletasks

    # Select the diff region closest to the middle of the screen
    set winhalf [expr {[winfo height $w(RightText)] / 2}]
    set result [find-diff [expr {int([$w(RightText) index @1,$winhalf])}]]
    move [lindex $result 0] 0 0

    if {$opts(autocenter)} {
        center
    }

    if {$g(showmerge)} {
        merge-center
    }
}

###############################################################################
# Toggle showing map or not
###############################################################################

proc do-show-map {{showMap {}}} {
    global opts
    global w

    if {$showMap != {}} {set opts(showmap) $showMap}

    if {$opts(showmap)} {
        grid $w(map) -row 1 -column 1 -stick ns
    } else {
        grid forget $w(map)
    }
}

###############################################################################
# Find the diff nearest to $line.
# Returns "$i $newtop" where $i is the index of the diff region
# and $newtop is the new top line in the window to the right.
###############################################################################

proc find-diff {line} {
    global g
    global w

    set top $line
    set newtop [expr {$top - int([$w(LeftText) index end]) + \
            int([$w(RightText) index end])}]

    for {set low 1; set high $g(count); set i [expr {($low + $high) / 2}]} \
            {$i >= $low}                                                 \
            {set i [expr {($low + $high) / 2}]} {

        foreach {line s1 e1 s2 e2 type} $g(scrdiff,$i) {}

        if {$s1 > $top} {
            set newtop [expr {$top - $s1 + $s2}]
            set high [expr {$i-1}]
        } else {
            set low [expr {$i+1}]
        }
    }

    # do some range checking...
    set i [max 1 [min $i $g(count)]]

    # If next diff is closer than the one found, use it instead
    if {$i > 0 && $i < $g(count)} {
        set nexts1 [lindex $g(scrdiff,[expr {$i + 1}]) 1]
        set e1 [lindex $g(scrdiff,$i) 2]
        if {$nexts1 - $top < $top - $e1} {
            incr i
        }
    }

    return [list $i $newtop]
}

###############################################################################
# Calculate number of lines in diff region
# pos       Diff number
# version   1 or 2, left or right window version
# screen    1 for screen size, 0 for original diff size
###############################################################################

proc diff-size {pos version {screen 0}} {
    global g

    if {$screen} {
        set diff scrdiff
    } else {
        set diff pdiff
    }
#    scan $g($diff,$pos) "%s %d %d %d %d %s" \
#        thisdiff s(1) e(1) s(2) e(2) type
    foreach {thisdiff s(1) e(1) s(2) e(2) type} $g($diff,$pos) {}

    set lines [expr {$e($version) - $s($version) + 1}]
    if {$type == "d" && $version == 2} {incr lines -1}
    if {$type == "a" && $version == 1} {incr lines -1}
    return $lines
}

###############################################################################
# Toggle showing merge preview or not
###############################################################################

proc do-show-merge {{showMerge ""}} {
    global g
    global w

    if {$showMerge != ""} {
        set g(showmerge) $showMerge
    }

    if {$g(showmerge)} {
        set-cursor
        wm deiconify $w(merge)
        $w(mergeText) configure -state disabled
        focus -force $w(mergeText)
        merge-center
        restore-cursor
    } else {
        wm withdraw $w(merge)
        restore-cursor
    }
}

###############################################################################
# Create Merge preview window
###############################################################################

proc merge-create-window {} {
    global opts
    global w
    global g

    set top .merge
    set w(merge) $top

    catch {destroy $top}

    toplevel $top
    set x [expr {[winfo rootx .] + 0}]
    set y [expr {[winfo rooty .] + 0}]
    wm geometry $top "+${x}+${y}"

    wm group $top .
    wm transient $top .

    wm title $top "$g(name) Merge Preview"

    frame $top.frame -bd 1 -relief sunken
    pack $top.frame -side top -fill both -expand y -padx 10 -pady 10

    set w(mergeText)     $top.frame.text
    set w(mergeVSB)      $top.frame.vsb
    set w(mergeHSB)      $top.frame.hsb
    set w(mergeDismiss)  $top.dismiss
    set w(mergeWrite)    $top.mergeWrite
    set w(mergeRecenter) $top.mergeRecenter

    # Window and scrollbars
    scrollbar $w(mergeHSB) \
            -orient horizontal \
            -command [list $w(mergeText) xview]
    scrollbar $w(mergeVSB) \
            -orient vertical \
            -command [list $w(mergeText) yview]

    text $w(mergeText) \
            -bd 0 \
            -takefocus 1 \
            -yscrollcommand [list $w(mergeVSB) set] \
            -xscrollcommand [list $w(mergeHSB) set]

    grid $w(mergeText) -row 0 -column 0 -sticky nsew
    grid $w(mergeVSB)  -row 0 -column 1 -sticky ns
    grid $w(mergeHSB)  -row 1 -column 0 -sticky ew

    grid rowconfigure $top.frame 0 -weight 1
    grid rowconfigure $top.frame 1 -weight 0

    grid columnconfigure $top.frame 0 -weight 1
    grid columnconfigure $top.frame 1 -weight 0

    # buttons
    button $w(mergeRecenter) \
            -width 8 \
            -text "ReCenter" \
            -underline 0 \
            -command merge-center

    button $w(mergeDismiss) \
            -width 8 \
            -text "Dismiss" \
            -underline 0 \
            -command [list do-show-merge 0]

    button $w(mergeWrite) \
            -width 8 \
            -text "Save..." \
            -underline 0 \
            -command [list popup-merge merge-write-file]

    pack $w(mergeDismiss) -side right -pady 5 -padx 10
    pack $w(mergeRecenter) -side right -pady 5 -padx 1
    pack $w(mergeWrite) -side right -pady 5 -padx 1

    eval $w(mergeText) configure $opts(textopt)
    foreach tag {difftag currtag} {
        eval $w(mergeText) tag configure $tag $opts($tag)
    }

    wm protocol $w(merge) WM_DELETE_WINDOW {do-show-merge 0}

    # adjust the tag priorities a bit...
    $w(mergeText) tag raise sel
    $w(mergeText) tag raise currtag difftag

    common-navigation $w(mergeText)


    wm withdraw $w(merge)
}

###############################################################################
# Read original file (Left window file) into merge preview window.
# Not so good if it has changed.
###############################################################################

proc merge-read-file {} {
    global finfo
    global w

    # hack; need to find a cleaner way...
    catch { destroy .merge }
    merge-create-window

    set hndl [open "$finfo(pth,1)" r]
    $w(mergeText) configure -state normal
    $w(mergeText) delete 1.0 end
    $w(mergeText) insert 1.0 [read $hndl]
    close $hndl

    # If last line doesn't end with a newline, add one. Important when
    # writing out the merge preview.
    if {![regexp {\.0$} [$w(mergeText) index "end-1lines lineend"]]} {
        $w(mergeText) insert end "\n"
    }
    $w(mergeText) configure -state disabled
}

###############################################################################
# Write merge preview to file
###############################################################################

proc merge-write-file {} {
    global g
    global w

    set hndl [open "$g(mergefile)" w]
    set text [$w(mergeText) get 1.0 end-1lines]
    puts -nonewline $hndl $text
    close $hndl
}

###############################################################################
# Add a mark where each diff begins and tag diff regions so they are visible.
# Assumes text is initially the bare original (Left) version.
###############################################################################
proc merge-add-marks {} {
    global g
    global w

    # mark all lines first, so selection won't mess up line numbers
    for {set i 1} {$i <= $g(count)} {incr i} {
        foreach [list thisdiff s1 e1 s2 e2 type] $g(pdiff,$i) {}
        set delta [expr {$type == "a" ? 1 : 0}]
        $w(mergeText) mark set mark$i $s1.0+${delta}lines
        $w(mergeText) mark gravity mark$i left
    }

    # select merged lines
    for {set i 1} {$i <= $g(count)} {incr i} {
        foreach [list thisdiff s1 e1 s2 e2 type] $g(pdiff,$i) {}

        if {$g(merge$i) == 1} {
            # (If it's an insert it's not visible)
            if {$type != "a"} {
                set lines [expr {$e1 - $s1 + 1}]
                $w(mergeText) tag add difftag mark$i mark$i+${lines}lines
            }
        } else {
            # Insert right window version
            merge-select-version $i 1 2
        }
    }

    # Tag current
    if {$g(count) > 0} {
        set pos $g(pos)
        set lines [diff-size $pos $g(merge$pos)]
        $w(mergeText) tag add currtag mark$pos "mark$pos+${lines}lines"
    }
}

###############################################################################
# Add a mark where each diff begins
# pos          diff index
# oldversion   1 or 2, previous merge choice
# newversion   1 or 2, new merge choice
###############################################################################

proc merge-select-version {pos oldversion newversion} {
    global g
    global w

    set newTextWin $w(LeftText)
    if {$newversion == 2} {set newTextWin $w(RightText)}

    catch {
        set oldlines [diff-size $pos $oldversion]
        $w(mergeText) configure -state normal
        $w(mergeText) delete mark$pos "mark${pos}+${oldlines}lines"
        $w(mergeText) configure -state disabled
    }

    # Screen coordinates
#    scan $g(scrdiff,$pos) "%s %d %d %d %d %s" \
#        thisdiff s(1) e(1) s(2) e(2) type
    foreach {thisdiff s(1) e(1) s(2) e(2) type} $g(scrdiff,$pos) {}

    # Get the text directly from window
    set newlines [diff-size $pos $newversion]

    set newtext [$newTextWin get $s($newversion).0 \
                     $s($newversion).0+${newlines}lines]
    # Insert it
    $w(mergeText) configure -state normal
    $w(mergeText) insert mark$pos $newtext diff
    $w(mergeText) configure -state disabled
    if {$pos == $g(pos)} {
        $w(mergeText) tag add currtag mark$pos "mark${pos}+${newlines}lines"
    }
}

###############################################################################
# Center the merge region in the merge window
###############################################################################

proc merge-center {} {
    global g
    global w

    # Size of diff in lines of text
    set difflines [diff-size $g(pos) $g(merge$g(pos))]
    set yview [$w(mergeText) yview]
    # Window height in percent
    set ywindow [expr {[lindex $yview 1] - [lindex $yview 0]}]
    # First line of diff
    set firstline [$w(mergeText) index mark$g(pos)]
    # Total number of lines in window
    set totallines [$w(mergeText) index end]

    if {$difflines / $totallines < $ywindow} {
        # Diff fits in window, center it
        $w(mergeText) yview moveto [expr {($firstline + $difflines / 2) \
                / $totallines - $ywindow / 2}]
    } else {
        # Diff too big, show top part
        $w(mergeText) yview moveto [expr {($firstline - 1) / $totallines}]
    }
}

###############################################################################
# Update the merge preview window with the current merge choice
# newversion   1 or 2, new merge choice
###############################################################################

proc do-merge-choice {newversion} {
    global g opts
    global w

    $w(mergeText) configure -state normal
    merge-select-version $g(pos) $g(merge$g(pos)) $newversion
    $w(mergeText) configure -state disabled

    set g(merge$g(pos)) $newversion
    if {$g(showmerge) && $opts(autocenter)} {
        merge-center
    }
}

###############################################################################
# Extract the start and end lines for file1 and file2 from the diff
# stored in "line".
###############################################################################

proc extract {line} {
    # the line darn well better be of the form <range><op><range>,
    # where op is one of "a","c" or "d". range will either be a
    # single number or two numbers separated by a comma.

    # is this a cool regular expression, or what? :-)
    regexp {([0-9]*)(,([0-9]*))?([a-z])([0-9]*)(,([0-9]*))?} $line \
            matchvar s1 x e1 op s2 x e2
    if {[string length $e1] == 0} {set e1 $s1}
    if {[string length $e2] == 0} {set e2 $s2}

    if {[info exists s1] && [info exists s2]} {
#        return "$line $s1 $e1 $s2 $e2 $op"
        return [list $line $s1 $e1 $s2 $e2 $op]
    } else {
        fatal-error "Cannot parse output from diff:\n$line"
    }

}

###############################################################################
# Insert blank lines to match added/deleted lines in other file
###############################################################################

proc add-lines {pos} {
    global g
    global w

    # Figure out which lines we need to address...
    foreach [list thisdiff s1 e1 s2 e2 type] $g(pdiff,$pos) {}

    set size(1) [expr {$e1 - $s1}]
    set size(2) [expr {$e2 - $s2}]

    incr s1 $g(delta,1)
    incr s2 $g(delta,2)

    # Figure out what kind of diff we're dealing with
    switch $type {
        "a" {
            set lefttext  "-" ;# insert
            set righttext "+"
            set idx 1
            set count [expr {$size(2) + 1}]

            incr s1
            incr size(2)
        }

        "d" {
            set lefttext  "+" ;# delete
            set righttext "-"
            set idx 2
            set count [expr {$size(1) + 1}]

            incr s2
            incr size(1)
        }

        "c" {
            set lefttext  "!" ;# change
            set righttext "!" ;# change
            set idx [expr {$size(1) < $size(2) ? 1 : 2}]
            set count [expr {abs($size(1) - $size(2))}]

            incr size(1)
            incr size(2)
        }

    }

    # Put plus signs in left info column
    if {$idx == 1} {
        set textWidget $w(LeftText)
        set infoWidget $w(LeftInfo)
        set cbWidget   $w(LeftCB)
#       set blank "++++++\n"
        set blank "      \n"
    } else {
        set textWidget $w(RightText)
        set infoWidget $w(RightInfo)
        set cbWidget   $w(RightCB)
        set blank "      \n"
    }

    # Insert blank lines to match other window
    set line [expr {$s1 + $size($idx)}]
    for {set i 0} {$i < $count} {incr i} {
        $textWidget insert $line.0 "\n"
        $infoWidget insert $line.0 $blank
        $cbWidget   insert $line.0 "\n"
    }

    incr size($idx) $count
    set e1 [expr {$s1 + $size(1) - 1}]
    set e2 [expr {$s2 + $size(2) - 1}]
    incr g(delta,$idx) $count

    # Insert change bars or text to show what has changed.
    $w(RightCB) configure -state normal
    $w(LeftCB) configure -state normal
    for {set i $s1} {$i <= $e1} {incr i} {
        $w(LeftCB)  insert $i.0 $lefttext
        $w(RightCB) insert $i.0 $righttext
    }

    # Save the diff block in window coordinates
    set g(scrdiff,$g(count)) [list $thisdiff $s1 $e1 $s2 $e2 $type]
}

###############################################################################
# Add a tag to a region.
###############################################################################

proc add-tag {wgt tag start end type new {exact 0}} {
    global g

    $wgt tag add $tag $start.0 [expr {$end + 1}].0

}

###############################################################################
# Change the tag for a diff region.
# 'pos' is the index in the diff array
# If 'oldtag' is present, first remove it from the region
# If 'setpos' is non-zero, make sure the region is visible.
# Returns the diff expression.
###############################################################################

proc set-tag {pos newtag {oldtag ""} {setpos 0}} {
    global g opts
    global w

    # Figure out which lines we need to address...
    if {![info exists g(scrdiff,$pos)]} {return}
    foreach {thisdiff s1 e1 s2 e2 dt} $g(scrdiff,$pos) {}

    # Remove old tag
    if {"$oldtag" != ""} {
        set e1next "[expr {$e1 + 1}].0"
        set e2next "[expr {$e2 + 1}].0"
        $w(LeftText)  tag remove $oldtag $s1.0 $e1next
        $w(LeftInfo)  tag remove $oldtag $s1.0 $e1next
        $w(RightText) tag remove $oldtag $s2.0 $e2next
        $w(RightInfo) tag remove $oldtag $s2.0 $e2next
        $w(LeftCB)    tag remove $oldtag $s1.0 $e1next
        $w(RightCB)   tag remove $oldtag $s2.0 $e2next
        catch {
            set lines [diff-size $pos $g(merge$pos)]
            $w(mergeText) tag remove $oldtag mark$pos "mark${pos}+${lines}lines"
        }
    }

    switch $dt {
        "d" { set coltag deltag; set rcbtag "-"; set lcbtag "+" }
        "a" { set coltag instag; set rcbtag "+"; set lcbtag "-" }
        "c" { set coltag chgtag; set rcbtag "!"; set lcbtag "!" }
    }

    # Add new tag
    if {$opts(tagtext)} {
        add-tag $w(LeftText)  $newtag $s1 $e1 $dt 1
        add-tag $w(RightText) $newtag $s2 $e2 $dt 1
        add-tag $w(RightText) $coltag $s2 $e2 $dt 1
    }
    if {$opts(tagcbs)} {
        if {$opts(colorcbs)} {
            add-tag $w(LeftCB)  $lcbtag $s1 $e1 $dt 1
            add-tag $w(RightCB) $rcbtag $s2 $e2 $dt 1
        } else {
            add-tag $w(LeftCB)  $newtag $s1 $e1 $dt 1
            add-tag $w(RightCB) $newtag $s2 $e2 $dt 1
            add-tag $w(RightCB) $coltag $s2 $e2 $dt 1
        }

    }
    if {$opts(tagln)} {
        add-tag $w(LeftInfo)  $newtag $s1 $e1 $dt 1
        add-tag $w(RightInfo) $newtag $s2 $e2 $dt 1
        add-tag $w(RightInfo) $coltag $s2 $e2 $dt 1
    }

    catch {
        set lines [diff-size $pos $g(merge$pos)]
        $w(mergeText) tag add $newtag mark$pos "mark${pos}+${lines}lines"
    }

    # Move the view on both text widgets so that the new region is
    # visible.
    if {$setpos} {
        if {$opts(autocenter)} {
            center
        } else {
            $w(LeftText) see $s1.0
            $w(RightText) see $s2.0
            $w(LeftText) mark set insert $s1.0
            $w(RightText) mark set insert $s2.0

            if {$g(showmerge)} {
                $w(mergeText) see mark$pos
            }
        }
    }

    # make sure the sel tag has the highest priority
    foreach window [list LeftText RightText LeftCB RightCB LeftInfo RightInfo] {
        $w($window) tag raise sel
    }

    return $thisdiff
}

###############################################################################
# moves to the diff nearest the insertion cursor or the mouse click,
# depending on $mode (which should be either "xy" or "mark")
###############################################################################

proc moveNearest {window mode args} {
    switch $mode {
        "xy" {
            set x [lindex $args 0]
            set y [lindex $args 1]
            set index [$window index @$x,$y]

            set line [expr {int($index)}]
            set diff [find-diff $line]
        }
        "mark" {
            set index [$window index [lindex $args 0]]
            set line [expr {int($index)}]
            set diff [find-diff $line]
        }
    }

    # ok, we have an index
    move [lindex $diff 0] 0 1
}

###############################################################################
###############################################################################

proc moveTo {window value} {
    global w
    global g
    # we know that the value is prefixed by the nunber/index of
    # the diff the user wants. So, just grab that out of the string
    regexp {([0-9]+) *:} $value matchVar index
    move $index 0
}

###############################################################################
# this is called when the user scrolls the map thumb interactively.
###############################################################################
proc map-seek {y} {
    global g
    global w

    incr y -2
    set yview [expr {(double($y) / double($g(mapheight)))}]

    # Show text corresponding to map;
    $w(RightText) yview moveto $yview
}


###############################################################################
# Move the "current" diff indicator (i.e. go to the next or previous diff
# region if "relative" is 1; go to an absolute diff number if "relative"
# is 0).
###############################################################################

proc move {value {relative 1} {setpos 1}} {
    global g
    global w

    if {$value == "first"} {set value 1; set relative 0}
    if {$value == "last"}  {set value $g(count); set relative 0}

    # Remove old 'curr' tag
    set-tag $g(pos) difftag currtag

    # Bump 'pos' (one way or the other).
    if {$relative} {
        set g(pos) [expr {$g(pos) + $value}]
    } else {
        set g(pos) $value
    }

    # Range check 'pos'.
    set g(pos) [max $g(pos) 1]
    set g(pos) [min $g(pos) $g(count)]

    # Set new 'curr' tag
    set g(currdiff) [set-tag $g(pos) currtag "" $setpos]

    # update the buttons..
    update-display

}

proc update-display {} {
    global g
    global w

    if {!$g(initOK)} {
        # disable darn near everything
        foreach widget [list combo prevDiff firstDiff nextDiff lastDiff \
                centerDiffs mergeChoice1 mergeChoice2 find mergeChoiceLabel \
                combo ] {
            $w($widget) configure -state disabled
        }
        foreach menu [list $w(popupMenu) $w(viewMenu)] {
            $menu entryconfigure "Previous*" -state disabled
            $menu entryconfigure "First*"    -state disabled
            $menu entryconfigure "Next*"     -state disabled
            $menu entryconfigure "Last*"     -state disabled
            $menu entryconfigure "Center*"   -state disabled
        }
        $w(popupMenu) entryconfigure "Find..."       -state disabled
        $w(popupMenu) entryconfigure "Find Nearest*" -state disabled
        $w(popupMenu) entryconfigure "Edit*"         -state disabled

        $w(editMenu)  entryconfigure "Find*"     -state disabled
        $w(editMenu)  entryconfigure "Edit File 1" -state disabled
        $w(editMenu)  entryconfigure "Edit File 2" -state disabled

        $w(fileMenu)  entryconfigure "Write*"        -state disabled
        $w(fileMenu)  entryconfigure "Recompute*"    -state disabled

        $w(mergeMenu) entryconfigure "Show*" -state disabled
        $w(mergeMenu) entryconfigure "Write*" -state disabled

	$w(markMenu) entryconfigure "Mark*" -state disabled
	$w(markMenu) entryconfigure "Clear*" -state disabled

    } else {
        # these are always enabled, assuming we have properly
        # diffed a couple of files
        $w(popupMenu) entryconfigure "Find..."      -state normal
        $w(popupMenu) entryconfigure "Find Nearest*" -state normal
        $w(popupMenu) entryconfigure "Edit*"         -state normal

        $w(mergeChoice1)     configure -state normal
        $w(mergeChoice2)     configure -state normal
        $w(mergeChoiceLabel) configure -state normal

        $w(editMenu)  entryconfigure "Find*"       -state normal
        $w(editMenu)  entryconfigure "Edit File 1" -state normal
        $w(editMenu)  entryconfigure "Edit File 2" -state normal

        $w(fileMenu)  entryconfigure "Write*"      -state normal
        $w(fileMenu)  entryconfigure "Recompute*"    -state normal

        $w(mergeMenu) entryconfigure "Show*" -state normal
        $w(mergeMenu) entryconfigure "Write*" -state normal

        $w(find) configure -state normal
        $w(combo) configure -state normal
    }

    # Update the toggles.
    if {$g(count)} {
        set g(toggle) $g(merge$g(pos))
    }

    # update the status line
    set g(statusCurrent) "$g(pos) of $g(count)"

    # update the combobox. We don't want it's command to fire, so
    # we'll disable it temporarily
    $w(combo) configure -commandstate "disabled"
    set i [expr {$g(pos) - 1}]
    $w(combo) configure -value [lindex [$w(combo) list get 0 end] $i]
    $w(combo) selection clear
    $w(combo) configure -commandstate "normal"

    # update the widgets
    if {$g(pos) <= 1} {
        $w(prevDiff) configure -state disabled
        $w(firstDiff) configure -state disabled
        $w(popupMenu) entryconfigure "Previous*" -state disabled
        $w(popupMenu) entryconfigure "First*"    -state disabled
        $w(viewMenu) entryconfigure "Previous*" -state disabled
        $w(viewMenu) entryconfigure "First*"    -state disabled
    } else {
        $w(prevDiff) configure -state normal
        $w(firstDiff) configure -state normal
        $w(popupMenu) entryconfigure "Previous*" -state normal
        $w(popupMenu) entryconfigure "First*"    -state normal
        $w(viewMenu) entryconfigure "Previous*" -state normal
        $w(viewMenu) entryconfigure "First*"    -state normal
    }

    if {$g(pos) >= $g(count)} {
        $w(nextDiff) configure -state disabled
        $w(lastDiff) configure -state disabled
        $w(popupMenu) entryconfigure "Next*"  -state disabled
        $w(popupMenu) entryconfigure "Last*" -state disabled
        $w(viewMenu) entryconfigure "Next*"  -state disabled
        $w(viewMenu) entryconfigure "Last*" -state disabled
    } else {
        $w(nextDiff) configure -state normal
        $w(lastDiff) configure -state normal
        $w(popupMenu) entryconfigure "Next*"  -state normal
        $w(popupMenu) entryconfigure "Last*" -state normal
        $w(viewMenu) entryconfigure "Next*"  -state normal
        $w(viewMenu) entryconfigure "Last*" -state normal
    }

    if {$g(count) > 0} {
        $w(centerDiffs) configure -state normal
        $w(popupMenu) entryconfigure "Center*" -state normal
        $w(viewMenu) entryconfigure "Center*" -state normal

        $w(mergeChoice1)     configure -state normal
        $w(mergeChoice2)     configure -state normal
        $w(mergeChoiceLabel) configure -state normal

	$w(markMenu) entryconfigure "Mark*" -state normal

    } else {
        $w(centerDiffs) configure -state disabled
        $w(popupMenu) entryconfigure "Center*" -state disabled
        $w(viewMenu) entryconfigure "Center*" -state disabled

        $w(mergeChoice1)     configure -state disabled
        $w(mergeChoice2)     configure -state disabled
        $w(mergeChoiceLabel) configure -state disabled

	$w(markMenu) entryconfigure "Mark*" -state disabled
    }

    # the mark clear button should only be enabled if there is 
    # presently a mark at the current diff record
    set widget $w(toolbar).mark$g(pos)
    if {[winfo exists $widget]} {
	$w(markMenu) entryconfigure "Clear*" -state normal
	$w(markClear) configure -state normal
    } else {
	$w(markMenu) entryconfigure "Clear*" -state disabled
	$w(markClear) configure -state disabled
    }
    
}

###############################################################################
# Center the top line of the CDR in each window.
###############################################################################

proc center {} {
    global g
    global w

#    scan $g(scrdiff,$g(pos)) "%s %d %d %d %d %s" dummy s1 e1 s2 e2 dt
    foreach {dummy s1 e1 s2 e2 dt} $g(scrdiff,$g(pos)) {}

    # Window requested height in pixels
    set opix [winfo reqheight $w(LeftText)]
    # Window requested lines
    set olin [$w(LeftText) cget -height]
    # Current window height in pixels
    set npix [winfo height $w(LeftText)]

    # Visible lines
    set winlines [expr {$npix * $olin / $opix}]
    # Lines in diff
    set diffsize [max [expr {$e1 - $s1 + 1}] [expr {$e2 - $s2 + 1}]]

    if {$diffsize < $winlines} {
        set h [expr {($winlines - $diffsize) / 2}]
    } else {
        set h 2
    }

    set o [expr {$s1 - $h}]
    if {$o < 0} { set o 0 }
    set n [expr {$s2 - $h}]
    if {$n < 0} { set n 0 }

    $w(LeftText)  mark set insert $s1.0
    $w(RightText) mark set insert $s2.0
    $w(LeftText) yview $o
    $w(RightText) yview $n

    if {$g(showmerge)} {
        merge-center
    }
}

###############################################################################
# Change the state on all of the diff-sensitive buttons.
###############################################################################

proc buttons {{newstate "normal"}} {
    global w
    $w(combo)       configure -state $newstate
    $w(prevDiff)    configure -state $newstate
    $w(nextDiff)    configure -state $newstate
    $w(firstDiff)   configure -state $newstate
    $w(lastDiff)    configure -state $newstate
    $w(centerDiffs) configure -state $newstate
}

###############################################################################
# Wipe the slate clean...
###############################################################################

proc wipe {} {
    global g
    global finfo

    set g(pos)      0
    set g(count)    0
    set g(diff)     ""
    set g(currdiff) ""

    set g(delta,1)    0
    set g(delta,2)    0
}

###############################################################################
# Wipe all data and all windows
###############################################################################

proc wipe-window {} {
    global g
    global w

    wipe

    foreach mod {Left Right} {
        $w(${mod}Text) configure -state normal
        $w(${mod}Text) tag remove difftag 1.0 end
        $w(${mod}Text) tag remove currtag 1.0 end
        $w(${mod}Text) delete 1.0 end

        $w(${mod}Info) configure -state normal
        $w(${mod}Info) delete 1.0 end
        $w(${mod}CB)   configure -state normal
        $w(${mod}CB) delete 1.0 end
    }

    catch {
        $w(mergeText) configure -state normal
        $w(mergeText) delete 1.0 end
        eval $w(mergeText) tag delete [$w(mergeText) tag names]
        $w(mergeText) configure -state disabled
    }

    if {[string length $g(destroy)] > 0} {
        eval $g(destroy)
        set g(destroy) ""
    }

    $w(combo) list delete 0 end
    buttons disabled

    diffmark clearall
}

###############################################################################
# Mark difference regions and build up the combobox
###############################################################################

proc mark-diffs {} {
    global g
    global w

    set numdiff [llength "$g(diff)"]

    set g(count) 0


    # ain't this clever? We want to update the display as soon as
    # we've marked enough diffs to fill the display so the user will
    # have the impression we're fast. But, we don't want this
    # want this code to slow us down too much, so we'll put the
    # code in a variable and delete it when its no longer needed.
    set hack {
        # for now, just pick a number out of thin air. Ideally
        # we'd compute the number of lines that are visible and
        # use that, but I'm too lazy today...
        if {$g(count) > 25} {
            update idletasks
            set hack {}
        }
    }

    foreach d $g(diff) {
        set result [extract $d]

        if {$result != ""} {
            incr g(count)
            set g(merge$g(count)) 1

            set g(pdiff,$g(count)) "$result"
            add-lines $g(count)

#            set-tag $g(count) difftag

            $w(combo) list insert end [format "%-6d: %s" $g(count) $d]

            eval $hack
        }

    }

    remark-diffs
    return $g(count)
}

###############################################################################
# start a new diff
###############################################################################
proc do-new-diff {args} {
    global argv argc
    global g

    if {[llength $args] == 0} {
        set args [newDiff popup]
        if {[llength $args] == 0} {
            return 0
        }
        set argv $args
        set argc [llength $args]
    }

    set-cursor
    set g(disableSyncing) 1 ;# turn off syncing until things settle down

    # remove all evidence of previous diff
    wipe-window
    update idletasks

    set result [catch init-files output]
    check-error $result $output
    if {$result} {
        # drat! Probably ought to display the newDiff dialog
        # or something.
        set ret 0

    } else {

        # do the diff
        do-diff

        move first

        set ret 1
    }

    restore-cursor

    update-display
    catch {unset g(disableSyncing)}

    return $ret
}

###############################################################################
# Remark difference regions...
###############################################################################

proc remark-diffs {} {
    global g
    global w
    global opts

    # delete all known tags.
    foreach window [list $w(LeftText) $w(LeftInfo) $w(LeftCB) \
            $w(RightText) $w(RightInfo) $w(RightCB) $w(mergeText)] {
        eval $window tag delete [$window tag names]
    }

    # reconfigure all the tags based on the current options
    # first, the common tags:
    foreach tag {difftag currtag deltag instag chgtag} {
        foreach win [list $w(LeftText)  $w(LeftInfo)  $w(LeftCB) \
                          $w(RightText) $w(RightInfo) $w(RightCB)] {
            if {[catch "$win tag configure $tag $opts($tag)"]} {
                do-error "Invalid settings\n\n$opts($tag)"
                eval "$win tag configure $tag $opts($tag)"
                return
            }
        }
    }

    # next, changebar-specific tags
    foreach widget [list $w(LeftCB) $w(RightCB)] {
        eval $widget tag configure + $opts(+)
        eval $widget tag configure - $opts(-)
        eval $widget tag configure ! $opts(!)
    }

    # ... and the merge text window
    foreach tag {difftag currtag} {
        eval $w(mergeText) tag configure $tag $opts($tag)
    }


    # now, reapply the tags to all the diff regions
    for {set i 1} {$i <= $g(count)} {incr i} {
        set-tag $i difftag
    }

    # finally, reset the current diff
    set-tag $g(pos) currtag "" 0

}


###############################################################################
# Put up some informational text.
###############################################################################

proc show-info {message} {
    global g

#    set g(currdiff) $message
    set g(statusInfo) $message
    update idletasks
}

###############################################################################
# Compute differences (start over, basically).
###############################################################################

proc rediff {} {
    global g
    global opts
    global finfo
    global tcl_platform
    global w

    buttons disabled

    # Read the files into their respective widgets & add line numbers.
     foreach mod {1 2} {
        if {$mod == 1} {set text $w(LeftText)} else {set text $w(RightText)}
        show-info "reading $finfo(pth,$mod)..."
        if {[catch {set hndl [open "$finfo(pth,$mod)" r]}]} {
            fatal-error "Failed to open file: $finfo(pth,$mod)"
        }
        $text insert 1.0 [read $hndl]
        close $hndl

        # Check if last line doesn't end with newline
        if {![regexp {\.0$} [$text index "end-1lines lineend"]]} {
            $text insert end "  <-- newline inserted by $g(name)\n"
        }
    }

    # Diff the two files and store the summary lines into 'g(diff)'.
    set diffcmd "$opts(diffcmd) {$finfo(pth,1)} {$finfo(pth,2)}"
    show-info "Executing \"$diffcmd\""


    set result [run-command "exec $diffcmd"]
    set stdout   [lindex $result 0]
    set stderr   [lindex $result 1]
    set exitcode [lindex $result 2]
    set g(returnValue) $exitcode

    # The exit code is 0 if there are no differences and 1 if there
    # are differences. Any other exit code means trouble and we abort.
    if {$exitcode < 0 || $exitcode > 1 || $stderr != ""} {
        fatal-error "diff failed:\n$stderr"
    }

    set g(diff) {}
    set lines [split $stdout "\n"]

    # If there is no output and we got this far the files are equal,
    # otherwise check if the first line begins with a line number. If
    # not there was trouble and we abort. For instance, using a binary
    # file results in the message "Binary files ..." etc on stdout,
    # exit code 1. The message may wary depending on locale.
    if {$lines != "" && [string match {[0-9]*} $lines] != 1} {
        fatal-error "diff failed:\n$stdout"
    }

    # Collect all lines containing line numbers
    foreach line $lines {
        if {[string match {[0-9]*} $line]} { lappend g(diff) $line }
    }

    # Mark up the two text widgets and go to the first diff (if there
    # is one).

    draw-line-numbers

    show-info "Marking differences..."

    $w(LeftInfo)  configure -state normal
    $w(RightInfo) configure -state normal
    $w(LeftCB)    configure -state normal
    $w(RightCB)   configure -state normal

    if {[mark-diffs]} {
        set g(pos) 1
        move 1 0
        buttons normal
    } else {
        after idle {show-info "Files are identical."}
        buttons disabled
    }

    # Prevent tampering in the line number widgets. The text
    # widgets are already taken care of
    $w(LeftInfo)  configure -state disabled
    $w(RightInfo) configure -state disabled
    $w(LeftCB)    configure -state disabled
    $w(RightCB)   configure -state disabled
}

###############################################################################
# Set the X cursor to "watch" for a window and all of its descendants.
###############################################################################

proc set-cursor {args} {
    global current
    global w

    . configure -cursor watch
    $w(LeftText) configure -cursor watch
    $w(RightText) configure -cursor watch
    $w(combo) configure -cursor watch
    update idletasks

}

###############################################################################
# Restore the X cursor for a window and all of its descendants.
###############################################################################

proc restore-cursor {args} {
    global current
    global w

    . configure -cursor {}
    $w(LeftText) configure -cursor {}
    $w(RightText) configure -cursor {}
    $w(combo) configure -cursor {}
    show-info ""
    update idletasks
}

###############################################################################
# Check if error was thrown by us or unexpected
###############################################################################

proc check-error {result output} {
    global g errorInfo

    if {$result && $output != "Fatal"} {
        error $result $errorInfo
    }
}


###############################################################################
# redo the current diff. Attempt to return to the same diff region,
# numerically speaking.
###############################################################################
proc recompute-diff {} {
    global g
    set current $g(pos)

    do-diff
    move $current 0

    update-display
}


###############################################################################
# Flash the "rediff" button and then kick off a rediff.
###############################################################################

proc do-diff {} {
    global g map errorInfo
    global opts

    set-cursor
    update idletasks

    wipe-window
    update idletasks
    set result [catch {
        if {$g(mapheight)} {
            map blank
        }
        init-files
        rediff
        merge-read-file
        merge-add-marks

        # If a map exists, recreate it
        if {$opts(showmap)} {
            set g(mapheight) -1
            map-resize
        }
    } output]

    check-error $result $output

    restore-cursor
}

###############################################################################
# Get things going...
###############################################################################

proc main {} {
    global argv
    global w
    global g errorInfo
    global startupError
    global opts

    wm withdraw .
    wm protocol . WM_DELETE_WINDOW do-exit
    wm title . "$g(name) $g(version)"

    wipe

    create-display
    update-display

    update

    merge-create-window

    do-show-linenumbers
    do-show-map

    # evaluate any custom code the user has
    if {[info exists opts(customCode)]} {
	if {[catch [list uplevel \#0 $opts(customCode)] error]} {
	    set startupError "Error in custom code: \n\n$error"
	} else {
	    update
	}
    }

    eval do-new-diff $argv

    move first

    wm deiconify .
    update idletasks

    if {[info exists startupError]} {
        tk_messageBox \
                -icon warning \
                -type ok \
                -title "$g(name) - Error in Startup File" \
                -message $startupError
    }
}


###############################################################################
# Erase tmp files (if necessary) and destroy the application.
###############################################################################

proc del-tmp {} {
    global g finfo

    if {$finfo(tmp,1)} {file delete $finfo(pth,1)}
    if {$finfo(tmp,2)} {file delete $finfo(pth,2)}
    foreach f $g(tempfiles) {file delete $f}
}

###############################################################################
# Throw up a window with formatted text
###############################################################################

proc do-text-info {w title text} {
    global g

    catch "destroy $w"
    toplevel $w
    wm title $w "$g(name) Help - $title"
    set x [expr {[winfo rootx .] + 0}]
    set y [expr {[winfo rooty .] + 0}]

    wm geometry $w "=55x29+${x}+${y}"
    wm group $w .
    wm transient $w .

    frame $w.f -bd 1 -relief sunken
    pack $w.f -side top -fill both -expand y

    text $w.f.title \
            -highlightthickness 0 \
            -bd 0 \
            -height 2 \
            -wrap word \
            -width 50 \
            -background white \
            -foreground black

    text $w.f.text \
            -wrap word \
            -setgrid true \
            -padx 20 \
            -highlightthickness 0 \
            -bd 0 \
            -width 50 \
            -height 20 \
            -yscroll [list $w.f.vsb set] \
            -background white\
            -foreground black
    scrollbar $w.f.vsb \
            -command [list $w.f.text yview] \
            -orient vertical

    pack $w.f.vsb -side right -fill y -expand n
    pack $w.f.title -side top -fill x -expand n
    pack $w.f.text -side left -fill both -expand y

    focus $w.f.text

    button $w.done -text Dismiss -command "destroy $w"
    pack $w.done -side right -fill none -pady 5 -padx 5

    put-text $w.f.title "<ttl>$title</ttl>"
    put-text $w.f.text $text
    $w.f.text configure -state disabled
}


###############################################################################
# centers window w over parent
###############################################################################
proc centerWindow {w {size {}}} {
    update
    set parent .

    if {[llength $size] > 0} {
        set wWidth [lindex $size 0]
        set wHeight [lindex $size 1]
    } else {
        set wWidth  [winfo reqwidth $w]
        set wHeight [winfo reqheight $w]
    }

    set pWidth  [winfo reqwidth $parent]
    set pHeight [winfo reqheight $parent]
    set pX      [winfo rootx $parent]
    set pY      [winfo rooty $parent]

    set centerX [expr {$pX + ($pWidth / 2)}]
    set centerY [expr {$pY + ($pHeight / 2)}]

    set x [expr {$centerX - ($wWidth / 2)}]
    set y [expr {$centerY - ($wHeight / 2)}]

    wm geometry $w "=${wWidth}x${wHeight}+${x}+${y}"
    update

}

###############################################################################
# all the code to handle the "New Diff" dialog
###############################################################################
proc newDiff {command args} {
    global g w
    global finfo

    set w(newDiffPopup) .newDiffPopup

    switch $command {
        "popup" {
            if {![winfo exists $w(newDiffPopup)]} {
                newDiff build
                centerWindow $w(newDiffPopup)
            }

            wm deiconify $w(newDiffPopup)
            raise $w(newDiffPopup)
            tkwait variable g(newDiffArgs)
            wm withdraw $w(newDiffPopup)

            # handle result...
            return $g(newDiffArgs)
        }

        "ok" {
            # normally we would retrieve the switch value based
            # on a radio button or option menu or some such on
            # the dialog, but for now we only support one type of
            # diff from the dialog...

            # handle the various permutations...
            switch 1 {
                1 {
                    set f1 [file nativename $g(newDiff,simple,original)]
                    set f2 [file nativename $g(newDiff,simple,revision)]
                    if {![file exists $f1]} {
                        tk_messageBox \
                                -icon warning \
                                -title "File does not exist" \
                                -message "The file $f1 does not exist" \
                                -type ok
                        return
                    }
                    if {![file exists $f2]} {
                        tk_messageBox \
                                -icon warning \
                                -title "File does not exist" \
                                -message "The file $f2 does not exist" \
                                -type ok
                        return
                    }
                    # setting this variable will cause popup
                    # to close the window...
                    set g(newDiffArgs) [list $f1 $f2]
                }
            }
        }

        "cancel" {
            set g(newDiffArgs) {}
            return
        }

        "browse" {
            # n.b.: args(0) is dialog title; args(1) is entry widget
            set title [lindex $args 0]
            set widget [lindex $args 1]
            set foo [$widget get]
            set initialdir [file dirname $foo]
            set initialfile [file tail $foo]
            set filename [tk_getOpenFile -title $title \
                    -initialfile $initialfile \
                    -initialdir  $initialdir]
            if {[string length $filename] > 0} {
                $widget delete 0 end
                $widget insert 0 $filename
                $widget selection range 0 end
                $widget xview end
                focus $widget
                return 1
            } else {
                after idle {raise $w(newDiffPopup)}
                return 0
            }
        }

        "build" {

            catch {destroy $w(newDiffPopup)}
            toplevel $w(newDiffPopup)

            wm group     $w(newDiffPopup) .
            wm transient $w(newDiffPopup) .
            wm title     $w(newDiffPopup) "New Diff"

            wm protocol  $w(newDiffPopup) WM_DELETE_WINDOW {newDiff cancel}

            wm withdraw  $w(newDiffPopup)

            set x [expr {[winfo rootx .] + 0}]
            set y [expr {[winfo rooty .] + 0}]

            # ultimately it might be nice to support all the
            # modes even though for now all we'll support is the
            # two-file mode. But, to make the transition easier
            # we'll put all of the widgets for this mode in its own
            # frame which can ultimately be controlled by a notebook
            # widget
            set simple [frame $w(newDiffPopup).simple -borderwidth 2 -relief groove]
            label $simple.l1 -text "Original File:"
            label $simple.l2 -text "Revised File:"

            entry $simple.e1 -textvariable g(newDiff,simple,original)
            entry $simple.e2 -textvariable g(newDiff,simple,revision)

            set g(newDiff,simple,original) $finfo(pth,1)
            set g(newDiff,simple,revision) $finfo(pth,2)

            # we want these buttons to be the same height as
            # the entry, so we'll try to force the issue...
            button $simple.b1 \
                    -borderwidth 1 \
                    -highlightthickness 0 \
                    -text "Browse..." \
                    -command [list newDiff browse "Original File" $simple.e1]
            button $simple.b2 \
                    -borderwidth 1 \
                    -highlightthickness 0 \
                    -text "Browse..." \
                    -command [list newDiff browse "Revised File" $simple.e2]

            # we'll use the grid geometry manager to get things lined up right...
            grid $simple.l1 -row 0 -column 0 -sticky e
            grid $simple.e1 -row 0 -column 1 -sticky nsew
            grid $simple.b1 -row 0 -column 2 -sticky nsew -pad 4

            grid $simple.l2 -row 1 -column 0 -sticky e
            grid $simple.e2 -row 1 -column 1 -sticky nsew
            grid $simple.b2 -row 1 -column 2 -sticky nsew -pad 4

            grid columnconfigure $simple 0 -weight 0
            grid columnconfigure $simple 1 -weight 1
            grid columnconfigure $simple 2 -weight 0

            # here are the buttons for this dialog...
            set commands [frame $w(newDiffPopup).buttons]
            button $commands.ok \
                    -text "Ok" \
                    -width 5 \
                    -command [list newDiff ok] \
                    -default active
            button $commands.cancel \
                    -text "Cancel" \
                    -width 5 \
                    -command [list newDiff cancel] \
                    -default normal

            pack $commands.ok $commands.cancel \
                    -side left \
                    -fill none \
                    -expand y \
                    -pady 4

            catch {$commands.ok -default 1}

            # pack this crud in...
            pack $simple \
                    -side top \
                    -fill both \
                    -expand y \
                    -ipady 20 \
                    -ipadx 20 \
                    -padx 5 \
                    -pady 5
            pack $commands -side bottom -fill x -expand n

            bind $w(newDiffPopup) <Return> [list $commands.ok invoke]
            bind $w(newDiffPopup) <Escape> [list $commands.cancel invoke]
        }

    }

}


###############################################################################
# all the code to handle the report writing dialog.
###############################################################################

proc write-report {command args} {
    global g
    global w
    global report
    global finfo

    set w(reportPopup) .reportPopup
    switch $command {
        popup {
            if {![winfo exists $w(reportPopup)]} {
                write-report build
            }
            set report(filename) [file join [pwd] $report(filename)]
            write-report update

            centerWindow $w(reportPopup)
            wm deiconify $w(reportPopup)
            raise $w(reportPopup)
        }

        cancel {
            wm withdraw $w(reportPopup)
        }

        update {

            set stateLeft  "disabled"
            set stateRight "disabled"
            if {$report(doSideLeft)} {set stateLeft "normal"}
            if {$report(doSideRight)} {set stateRight "normal"}

            $w(reportLinenumLeft) configure -state $stateLeft
            $w(reportCMLeft)      configure -state $stateLeft
            $w(reportTextLeft)    configure -state $stateLeft

            $w(reportLinenumRight) configure -state $stateRight
            $w(reportCMRight)      configure -state $stateRight
            $w(reportTextRight)    configure -state $stateRight

        }

        save {
            set leftLines  [lindex [split [$w(LeftText) index end-1lines] .] 0]
            set rightLines [lindex [split [$w(RightText) index end-1lines] .] 0]

            # number of lines of the largest window...
            set maxlines [max $leftLines $rightLines]

            # probably ought to catch this, in case it fails. Maybe later...
            set handle [open $report(filename) w]

            puts $handle "$g(name) $g(version) report"

            # write the file names
            if {$report(doSideLeft) == 1 && $report(doSideRight) == 1} {
                puts $handle "\nFile A: $finfo(lbl,1)\nFile B: $finfo(lbl,2)\n"
            } elseif {$report(doSideLeft) == 1} {
                puts $handle "\nFile: $finfo(lbl,1)"
            } else {
                puts $handle "\nFile: $finfo(lbl,2)"
            }

            puts $handle "number of diffs: $g(count)"

            set acount [set ccount [set dcount 0]]
            for {set i 1} {$i <= $g(count)} {incr i} {
#                scan $g(scrdiff,$i) "%s %d %d %d %d %s" line s1 e1 s2 e2 type
                foreach {line s1 e1 s2 e2 type} $g(scrdiff,$i) {}
                switch $type {
                    "d" { incr dcount }
                    "a" { incr acount }
                    "c" { incr ccount }
                }
            }

            puts $handle [format "    %6d regions were deleted" $dcount]
            puts $handle [format "    %6d regions were added"   $acount]
            puts $handle [format "    %6d regions were changed" $ccount]

            puts $handle "\n"
            for {set i 1} {$i <= $maxlines} {incr i} {
                set out(Left) [set out(Right) ""]
                foreach side {Left Right} {

                    if {$side == "Left"  && $i > $leftLines} break;
                    if {$side == "Right" && $i > $rightLines} break;

                    if {$report(doLineNumbers$side)} {
                        set widget $w(${side}Info)
                        set number [string trimright \
                                [$widget get "$i.0" "$i.0 lineend"]]

                        append out($side) [format "%6s " $number]
                    }

                    if {$report(doChangeMarkers$side)} {
                        set widget $w(${side}CB)
                        set data [$widget get "$i.0" "$i.1"]
                        append out($side) "$data "
                    }

                    if {$report(doText$side)} {
                        set widget $w(${side}Text)
                        append out($side) [string trimright \
                                [$widget get "$i.0" "$i.0 lineend"]]
                    }
                }

                if {$report(doSideLeft) == 1 && $report(doSideRight) == 1} {
                    set output [format "%-90s%-90s" $out(Left) $out(Right)]

                } elseif {$report(doSideRight) == 1} {
                    set output $out(Right)

                } elseif {$report(doSideLeft) == 1} {
                    set output $out(Left)

                } else {
                    # what a wasted effort!
                    set output ""
                }
                puts $handle [string trimright $output]
            }
            close $handle

            wm withdraw $w(reportPopup)
        }

        browse {
            set types {
                {{All Files}     {*}}
            }

            set path [tk_getSaveFile \
                    -defaultextension "" \
                    -filetypes $types \
                    -initialfile $report(filename)]

            if {[string length $path] > 0} {
                set report(filename) $path
            }
        }

        build {
            catch {destroy $w(reportPopup)}
            toplevel $w(reportPopup)
            wm group $w(reportPopup) .
            wm transient $w(reportPopup) .
            wm title $w(reportPopup) "$g(name) - Generate Report"
            wm protocol $w(reportPopup) WM_DELETE_WINDOW \
                    [list write-report cancel]
            wm withdraw $w(reportPopup)

            set cf [frame $w(reportPopup).clientFrame -bd 2 -relief groove]
            set bf [frame $w(reportPopup).buttonFrame -bd 0]
            pack $cf -side top    -fill both -expand y -padx 5 -pady 5
            pack $bf -side bottom -fill x -expand n

            # buttons...
            set w(reportSave) $bf.save
            set w(reportCancel) $bf.cancel

            button $w(reportSave) \
                    -text "Save" \
                    -underline 0 \
                    -command [list write-report save] \
                    -width 6
            button $w(reportCancel) \
                    -text "Cancel" \
                    -underline 0 \
                    -command [list write-report cancel] \
                    -width 6

            pack $w(reportCancel) -side right -pady 5 -padx 5
            pack $w(reportSave)   -side right -pady 5

            # client area.
            set col(Left) 0; set col(Right) 1
            foreach side  [list Left Right] {
                set choose  [checkbutton $cf.choose$side]
                set linenum [checkbutton $cf.linenum$side]
                set cm      [checkbutton $cf.changemarkers$side]
                set text    [checkbutton $cf.text$side]

                $choose configure \
                        -text "$side Side" \
                        -variable report(doSide$side) \
                        -command [list write-report update]

                $linenum configure \
                        -text "Line Numbers" \
                        -variable report(doLineNumbers$side)
                $cm configure \
                        -text "Change Markers" \
                        -variable report(doChangeMarkers$side)
                $text configure \
                        -text "Text" \
                        -variable report(doText$side)

                grid $choose  -row 0 -column $col($side) -sticky w
                grid $linenum -row 1 -column $col($side) -sticky w -padx 10
                grid $cm      -row 2 -column $col($side) -sticky w -padx 10
                grid $text    -row 3 -column $col($side) -sticky w -padx 10

                # save the widget paths for later use...
                set w(reportChoose$side)  $choose
                set w(reportLinenum$side) $linenum
                set w(reportCM$side)      $cm
                set w(reportText$side)    $text
            }

            # the entry, label and button for the filename will get
            # stuffed into a frame for convenience...
            frame $cf.fileFrame -bd 0
            grid $cf.fileFrame -row 4 -columnspan 2 -sticky ew -padx 5

            label $cf.fileFrame.l -text "File:"
            entry $cf.fileFrame.e \
                    -textvariable report(filename) \
                    -width 30
            button $cf.fileFrame.b \
                    -text "Browse..." \
                    -pady 0 \
                    -highlightthickness 0 \
                    -borderwidth 1 \
                    -command [list write-report browse]

            pack $cf.fileFrame.l -side left -pady 4
            pack $cf.fileFrame.b -side right -pady 4 -padx 2
            pack $cf.fileFrame.e -side left -fill x -expand y -pady 4

            grid rowconfigure $cf 0 -weight 0
            grid rowconfigure $cf 1 -weight 0
            grid rowconfigure $cf 2 -weight 0
            grid rowconfigure $cf 3 -weight 0

            grid columnconfigure $cf 0 -weight 1
            grid columnconfigure $cf 1 -weight 1

            # make sure the widgets are in the proper state
            write-report update
        }
    }
}

###############################################################################
# Throw up an "about" window.
###############################################################################

proc do-about {} {
    global g

    set title "About $g(name)"
    set text {
<hdr>$g(name) $g(version)</hdr>

<itl>$g(name)</itl> is a Tcl/Tk front-end to <itl>diff</itl> for Unix and NT, and is Copyright (C) 1994-1998 by John M. Klassa.

Many of the toolbar icons were created by Dean S. Jones and used with his permission. The icons have the following copyright:

Copyright(C) 1998 by Dean S. Jones
dean@gallant.com
http://www.gallant.com/icons.htm 
http://www.javalobby.org/jfa/projects/icons/

<bld>This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA</bld>

    }

    set text [subst -nobackslashes -nocommands $text]
    do-text-info .about $title $text
}

###############################################################################
# Throw up a "command line usage" window.
###############################################################################

proc do-usage {} {
    global g

    set title "The $g(name) Command Line"
    set text {
<hdr>Startup</hdr>

<itl>$g(name)</itl> may be started in any of the following ways:

    Interactive selection of files to compare:
<cmp>	tkdiff</cmp>

    Plain files:
<cmp>	tkdiff FILE1 FILE2</cmp>

    Plain file with conflict markers:
<cmp>	tkdiff -conflict FILE</cmp>

    Source control RCS/CVS/SCCS/PVCS/Perforce:
<cmp>	tkdiff FILE	</cmp>(same as -r)
<cmp>	tkdiff -r FILE
	tkdiff -rREV FILE
	tkdiff -rREV -r FILE
	tkdiff -rREV1 -rREV2 FILE</cmp>

$g(name) detects and supports RCS, CVS and SCCS by looking for a directory with the same name.  It detects and supports PVCS by looking for a vcs.cfg file. It detects and supports Perforce by looking for an environment variable named P4CLIENT.

In the first form, tkdiff will present a dialog to allow you to choose the files to diff interactively. At present this dialog only supports a diff between two files that already exist. There is no way to do a diff against a file under souce code control (unless the previous versions can be found on disk via a standard file selection dialog).

In the second form, at least one of the arguments must be the name of a plain text file.  Symbolic links are acceptable, but at least one of the filename arguments must point to a real file rather than to a directory.

In the remaining forms, <cmp>REV</cmp> (or <cmp>REV1</cmp> and <cmp>REV2</cmp>) must be a valid revision number for <cmp>FILE</cmp>.  Where RCS, CVS, SCCS, PVCS or Perforce is implied but no revision number is specified, <cmp>FILE</cmp> is compared with the the revision most recently checked in.

To merge a file with conflict markers generated by "<cmp>merge</cmp>", "<cmp>cvs</cmp>", or "<cmp>vmrg</cmp>", use "<cmp>tkdiff -conflict FILE</cmp>".  The file is split into two temporary files which you can merge as usual (see below).

Note that "<cmp>tkdiff FILE</cmp>" is the same as "<cmp>tkdiff -r FILE</cmp>".  The CVS version has priority, followed by the SCCS version -- i.e. if a CVS directory is present, CVS; if not and an SCCS directory is present, SCCS is assumed; otherwise, if a CVS.CFG file is found, PVCS is assumed; otherwise RCS is assumed. If none of the above apply and the Perforce environment variable P4CLIENT is found, perforce is used.

Note also that the "<cmp>tkdiff -rREV -r FILE</cmp>" form results in a comparison between revision <cmp>REV</cmp> and the head of the RCS, CVS, SCCS, PVCS or Perforce revision tree.

Note further that anything with a leading dash that isn't recognized as a $g(name) option is passed through to diff.  This permits you to temporarily alter the way diff is called, without resorting to a change in your preferences file.
}

    set text [subst -nobackslashes -nocommands $text]
    do-text-info .usage $title $text
}

###############################################################################
# Throw up a help window.
###############################################################################

proc do-help {} {
    global g

    set title "How to use the $g(name) GUI"
    set text {
<hdr>Layout</hdr>

The top row contains the File, Edit, View, Mark, Merge and Help menus. The second row contains the labels which identify the contents of each text window. Below that is a toolbar which contains navigation and merge selection tools.

The left-most text widget displays the contents of <cmp>FILE1</cmp>, the most recently checked-in revision, <cmp>REV</cmp> or <cmp>REV1</cmp>, respectively (as per the startup options described in the "On Command Line" help). The right-most widget displays the contents of <cmp>FILE2</cmp>, <cmp>FILE</cmp> or <cmp>REV2</cmp>, respectively. Clicking the right mouse button over either of these windows will give you a context sensitive menu with actions that will act on the window you clicked over. For example, if you click right over the right hand window and select "Edit", the file displayed on the right hand side will be loaded into a text editor.

All difference regions (DRs) are highlighted to set them apart from the surrounding text. The <itl>current difference region</itl>, or <bld>CDR</bld>, is further set apart so that it can be correlated to its partner in the other text widget (that is, the CDR on the left matches the CDR on the right).

<hdr>Changing the CDR</hdr>

The CDR can be changed in a sequential manner by means of the <btn>Next</btn> and <btn>Previous</btn> buttons. The <btn>First</btn> and <btn>Last</btn> buttons allow you to quickly navigate to the first or last CDR, respectively. For random access to the DRs, use the dropdown listbox in the toolbar or the diff map, described below.

By clicking right over a window and using the popup menu you can select <btn>Find Nearest Diff</btn> to find the diff record nearest the point where you clicked.

You may also select any highlighted diff region as the current diff region by double-clicking on it.

<hdr>Operations</hdr>

1. From the <btn>File</btn> menu:

The <btn>New...</btn> button displays a dialog where you may choose two files to compare. Selecting "Ok" from the dialog will diff the two files. The <btn>Recompute Diffs</btn> button recomputes the differences between the two files whose names appear at the top of the <itl>$g(name)</itl> window. The <btn>Write Report...</btn> lets you create a report file that contains the information visible in the windows. Lastly, the <btn>Exit</btn> button terminates <itl>$g(name)</itl>.

2. From the <btn>Edit</btn> menu:

<btn>Copy</btn> copies the currently selected text to the system clipboard. <btn>Find</btn> pops up a dialog to let you search either text window for a specified text string.  <btn>Edit File 1</btn> and <btn>Edit File 2</btn> launch an editor on the files displayed in the left- and right-hand panes.  <btn>Preferences</btn> pops up a dialog box from which display (and other) options can be changed and saved.

3. From the <btn>View</btn> menu:

<btn>Show Line Numbers</btn> toggles the display of line numbers in the text widgets. If <btn>Synchronize Scrollbars</btn> is on, the left and right text widgets are synchronized i.e. scrolling one of the windows scrolls the other. If <btn>Auto Center</btn> is on, pressing the Next or Prev buttons centers the new CDR automatically. The <btn>Show Diff Map</btn> toggles the display of the diff map (see below) on or off. <btn>Show Merge Preview</btn> shows or hides the merge preview (see below).

4. From the <btn>Mark</btn> menu:

The <btn>Mark Current Diff</btn> creates a new toolbar button that will jump to the current diff region. The <btn>Clear Current Diff Mark</btn> will remove the toolbar mark button associated with the current diff region, if one exists.

5. From the <btn>Merge</btn> menu:

The <btn>Show Merge Window</btn> button pops up a window with the current merged version of the two files. The <btn>Write Merge File</btn> button will allow you to save the contents of that window to a file.

6. From the <btn>Help</btn> menu:

The <btn>About $g(name)</btn> button displays copyright and author information. The <btn>On GUI</btn> button generates this window. The <btn>On Command Line</btn> button displays help on the $g(name) command line options. The <btn>On Preferences</btn> button displays help on the user-settable preferences.

7. From the toolbar:

The first tool is a dropdown list of all of the differences in a standard diff-type format. You may use this list to go directly to any diff record. The <btn>Next</btn> and <btn>Previous</btn> buttons take you to the "next" and "previous" DR, respectively. The <btn>First</btn> and <btn>Last</btn> buttons take you to the "first" and "last" DR. The <btn>Center</btn> button centers the CDRs in their respective text windows. You can set <btn>Auto Center</btn> in <btn>Preferences</btn> to do this automatically for you as you navigate through the diff records.

<hdr>Keyboard Navigation</hdr>

When a text widget has the focus, you may use the following shortcut keys:
<cmp>
        f       First diff
        c       Center current diff
        l       Last diff
        n       Next diff
        p       Previous diff
        1       Merge Choice 1
        2       Merge Choice 2
</cmp>

The cursor, Home, End, PageUp and PageDown keys work as expected, adjusting the view in whichever text window has the focus. Note that if <btn>Synchronize Scrollbars</btn> is set in <btn>Preferences</btn>, both windows will scroll at the same time.

<hdr>Scrolling</hdr>

To scroll the text widgets independently, make sure <btn>Synchronize Scrollbars</btn> in <btn>Preferences</btn> is off. If it is on, scrolling any text widget scrolls all others. Scrolling does not change the current diff record (CDR).

<hdr>Diff Marks</hdr>

You can set "markers" at specific diff regions for easier navigation. To do this, click on the <btn>Set Mark</btn> button. It will create a new toolbar button that will jump back to this diff region. To clear a diff mark, go to that diff record and click on the <btn>Clear Mark</btn> button.

<hdr>Diff Map</hdr>

The diff map is a map of all the diff regions. It is shown in the middle of the main window if "Diff Map" on the View menu is on. The map is a miniature of the file's diff regions from top to bottom. Each diff region is rendered as a patch of color, Delete as red, Insert as green and Change as blue. The height of each patch corresponds to the relative size of the diff region. A thumb lets you interact with the map as if it were a scrollbar.

All diff regions are drawn on the map even if too small to be visible. For large files with small diff regions, this may result in patches overwriting each other.

<hdr>Merging</hdr>

To merge the two files, go through the difference regions (via "Next", "Prev" or whatever other means you prefer) and select "Left" or "Right" (next to the "Merge Choice:" label) for each. Selecting "Left" means that the the left-most file's version of the difference will be used in creating the final result; choosing "Right" means that the right-most file's difference will be used. Each choice is recorded, and can be changed arbitrarily many times. To commit the final, merged result to disk, choose "Write Merge File" from the <btn>Merge</btn> menu.

<hdr>Merge Preview</hdr>

To see a preview of the file that would be written by "Write Merge File", select "Show Merge Window" in the View menu. A separate window is shown containing the preview. It is updated as you change merge choices. It is synchronized with the other text widgets if "Synchronize Scrollbars" is on.

<hdr>Credits</hdr>

Thanks to Wayne Throop for beta testing, and for giving valuable suggestions (and code!) along the way. Thanks (and credit) to John Heidemann for his window tags routines, which I shamelessly stole (with permission) out of his great Tk-based Solitaire game, <itl>Klondike</itl>. Thanks to D. Elson (author of <itl>tkCVS</itl>) for writing the code that extends the RCS support to include CVS. Thanks to John Brown for writing the code that extends the revision control support to SCCS.

<bld>Major</bld> thanks to Warren Jones (wjones@tc.fluke.com) and Peter Brandstrom (qraprbm@era-lvk.ericsson.se) for going way above and beyond the call. Warren added support for NT and cleaned up the Unix code as well. Peter, independently, did the same thing and then added the new interface. The end result was the 2.x series...  Many, many thanks to you both!

<bld>Major</bld> thanks also to Bryan Oakley (oakley@channelpoint.com), who made the GUI even more appealing...  Bryan did a <itl>ton</itl> of work, the result of which was the 3.x series.  Dorothy Robinson provided helpful comments and patches for 3.x, too.  Thanks, Bryan and Dorothy!

Thanks to Dean Jones (dean@gallant.com) for permission to use his icons in the toolbar. 

Many, many thanks also to the many others who have written and provided ideas and encouragement and code since <itl>$g(name)</itl> was first released!  I haven't done much coding since the 1.x series; almost every new feature that has come about since then has been the result of volunteer efforts.  Thanks, folks!

<hdr>Comments</hdr>

Questions and comments should be sent to John Klassa at <itl>klassa@ipass.net</itl>.

    }

    set text [subst -nobackslashes -nocommands $text]
    do-text-info .help $title $text
}

######################################################################
# display help on the preferences
######################################################################
proc do-help-preferences {} {
    global g
    global pref

    customize-initLabels

    set title "$g(name) Preferences"
    set text {
<hdr>Overview</hdr>

Preferences are stored in a file in your home directory (identified by the environment variable <cmp>HOME</cmp>. If the environment variable <cmp>HOME</cmp> is not set the platform-specific variant of "/" will be used. If you are on a Windows platform the file will be named <cmp>_tkdiff.rc</cmp> and will have the attribute "hidden". For all other platforms the file will be named ".tkdiffrc". You may override the name and location of this file  by setting the environment variable <cmp>TKDIFFRC</cmp> to whatever filename you wish.

Preferences are organized into three categories: General, Display and Appearance.

<hdr>General</hdr>

<bld>$pref(diffcmd)</bld>

This is the command (with arguments) to run to generate a diff of the two files. Typically this will be "diff". If you are using gnu diff you might want to set it to "diff --ignore-space-change" to ignore changes in whitespace. When this command is run, the names of two files to be diffed will be added as the last to arguments on the command line.


<bld>$pref(tmpdir)</bld>

The name of a directory for files that are temporarily created while $g(name) is running.


<bld>$pref(editor)</bld>

The name of an external editor program to use when editing a file (ie: when you select "Edit" from the popup menu). If this value is blank, a simple editor built in to $g(name) will be used. For windows users you might want to set this to "notepad". Unix users may want to set this to "xterm -e vi" or perhaps "gnuclient". When run, the name of the file to edit will be appened as the last argument on the command line.

<bld>$pref(geometry)</bld>

This defines the default size, in characters of the two text windows. The format should be <cmp>WIDTHxHEIGHT</cmp>. For example, "80x40".


<bld>$pref(fancyButtons)</bld>

If set, toolbar buttons will mimic the visual behavior of typical Microsoft Windows applications. Buttons will initially be flat until the cursor moves over them, at which time they will be raised.

If unset, toolbar buttons will always appear raised.


<bld>$pref(toolbarIcons)</bld>

If set, the toolbar buttons will use icons instead of text labels.

If unset, the toolbar buttons will use text labels instead of icons.


<bld>$pref(autocenter)</bld>

If set, whenever a new diff record becomes the current diff record (for example, when pressing the next or previous buttons), the diff record will be automatically centered on the screen.

If unset, no automatic scrolling will occur.


<bld>$pref(syncscroll)</bld>

If set, scrolling either text window will result in both windows scrolling.

If not set, the windows will scroll independent of each other.


<bld>$pref(autoselect)</bld>

If set, automatically select the nearest visible diff region when scrolling.

If not set, the current diff region will not change during scrolling.

This only takes effect if <bld>$pref(syncscroll)</bld> is set.


<hdr>Display</hdr>

<bld>$pref(showln)</bld>

If set, line numbers will be displayed alongside each line of each file.

If not set, no line numbers will appear.


<bld>$pref(tagln)</bld>

If set, line numbers are highlighted with the options defined in the Appearance section of the preferences.

If not set, line numbers won't be highlighted.


<bld>$pref(showcbs)</bld>

If set, change bars will be displayed alongside each line of each file.

If not set, no change bars will appear.


<bld>$pref(tagcbs)</bld>

If set, change indicators will be highlighted. If <itl>$pref(colorcbs)</itl> is set they will appear as solid colored bars that match the colors used in the diff map. If <itl>$pref(colorcbs)</itl> is not set, the change indicators will be highlighted according to the options defined in the Appearance section of preferences.


<bld>$pref(showmap)</bld>

If set, colorized, graphical "diff map" will be displayed between the two files, showing regions that have changed. Red is used to show deleted lines, green for added lines, and blue for changed lines.

If not set, the diff map will not be shown.


<bld>$pref(tagtext)</bld>

If set, the file contents will be highlighted with the options defined in the Appearance section of the preferences.

If not set, the file contents won't be highlighted.


<bld>$pref(colorcbs)</bld>

If set, the change bars will display as solid bars of color that match the colors used by the diff map.

If not set, the change bars will display a "+" for lines that exist in only one file, a "-" for lines that are missing from only one file, and "!" for lines that are different between the two files.



<hdr>Appearance</hdr>

<bld>$pref(textopt)</bld>

This is a list of Tk text widget options that are applied to each of the two text windows in the main display. If you have Tk installed on your machine these will be documented in the "Text.n" man page.


<bld>$pref(difftag)</bld>

This is a list of Tk text widget tag options that are applied to all diff regions. Use this option to make diff regions stand out from regular text.


<bld>$pref(deltag)</bld>

This is a list of Tk text widget tag options that are applied to the current diff region. These options have a higher priority than those for all diff regions. So, for example, if you set the forground for all diff regions to be black and set the foreground for the current diff region to be blue, the current diff region foreground color will be used.


<bld>$pref(instag)</bld>

This is a list of Tk text widget tag options that are applied to regions that have been inserted. These options have a higher priority than those for all diff regions.


<bld>$pref(chgtag)</bld>

This is a list of Tk text widget tag options that are applied to regions that have been changed. These options have a higher priority than those for all diff regions.


<bld>$pref(currtag)</bld>

This is a list of Tk text widget tag options that are applied to the current diff region. These tags have a higher priority than those for all diff regions, and a higher priority than the change, inserted and deleted diff regions.



    }

    # since we have embedded references to the preference labels in
    # the text, we need to perform substitutions. Because of this, if
    # you edit the above text, be sure to properly escape any dollar
    # signs that are not meant to be treated as a variable reference

    set text [subst -nobackslashes -nocommands $text]
    do-text-info .help-preferences $title $text
}

######################################################################
#
# text formatting routines derived from Klondike
# Reproduced here with permission from their author.
#
# Copyright (C) 1993,1994 by John Heidemann <johnh@ficus.cs.ucla.edu>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of John Heidemann may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY JOHN HEIDEMANN ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL JOHN HEIDEMANN BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
######################################################################

proc put-text {tw txt} {
    global tk_version

    if {$tk_version >= 8.0} {
        $tw configure -font {Helvetica 10}

        $tw tag configure bld -font {Helvetica 10 bold}
        $tw tag configure cmp -font {Courier 10 bold}
        $tw tag configure hdr -font {Helvetica 14 bold} -underline 1
        $tw tag configure itl -font {Times 10 italic}

        $tw tag configure btn \
            -font {Courier 9} \
            -foreground black -background white \
            -relief groove -borderwidth 2

        $tw tag configure ttl \
                -font {Helvetica 14 italic} \
                -foreground blue \
                -justify center

    } else {
        $tw configure -font -*-Helvetica-Medium-R-Normal-*-14-*

        $tw tag configure bld -font -*-Helvetica-Bold-R-Normal-*-14-*
        $tw tag configure cmp -font -*-Courier-Medium-R-Normal-*-14-*
        $tw tag configure hdr -font -*-Helvetica-Bold-R-Normal-*-18-* \
            -underline 1
        $tw tag configure itl -font -*-Times-Medium-I-Normal-*-14-*

        $tw tag configure btn \
            -font -*-Courier-Medium-R-Normal-*-12-* \
            -foreground black -background white \
            -relief groove -borderwidth 2

        $tw tag configure ttl \
                -font -*-Helvetica-Bold-R-Normal-*-18-* \
                -foreground blue \
                -justify center

    }
    $tw tag configure rev -foreground white -background black

    $tw mark set insert 0.0

    set t $txt

    while {[regexp -indices {<([^@>]*)>} $t match inds] == 1} {

        set start [lindex $inds 0]
        set end [lindex $inds 1]
        set keyword [string range $t $start $end]

        set oldend [$tw index end]

        $tw insert end [string range $t 0 [expr {$start - 2}]]

        purge-all-tags $tw $oldend insert

        if {[string range $keyword 0 0] == "/"} {
            set keyword [string trimleft $keyword "/"]
            if {[info exists tags($keyword)] == 0} {
                error "end tag $keyword without beginning"
            }
            $tw tag add $keyword $tags($keyword) insert
            unset tags($keyword)
        } else {
            if {[info exists tags($keyword)] == 1} {
                error "nesting of begin tag $keyword"
            }
            set tags($keyword) [$tw index insert]
        }

        set t [string range $t [expr {$end + 2}] end]
    }

    set oldend [$tw index end]
    $tw insert end $t
    purge-all-tags $tw $oldend insert
}

proc purge-all-tags {w start end} {
    foreach tag [$w tag names $start] {
        $w tag remove $tag $start $end
    }
}

proc do-edit {} {
    global g
    global opts
    global finfo
    global w

    if {$g(activeWindow) == $w(LeftText)} {
        set fileno 1
    } elseif {$g(activeWindow) == $w(RightText)} {
        set fileno 2
    } else {
        set fileno 1
    }

    if {$finfo(tmp,$fileno)} {
        do-error "This file is not editable."
    } else {
        if {[string length [string trim $opts(editor)]] == 0} {
            simpleEd open $finfo(pth,$fileno)
        } else {
            eval exec $opts(editor) "{$finfo(pth,$fileno)}" &
        }
    }
}


##########################################################################
# A simple editor, from Bryan Oakley.
##########################################################################
proc simpleEd {command args} {
    global font

    switch $command {
        open {
            set filename [lindex $args 0]

            set w .editor
            set count 0
            while {[winfo exists ${w}$count]} {
                incr count 1
            }
            set w ${w}$count

            toplevel $w -borderwidth 2 -relief sunken
            wm title $w "$filename - Simple Editor"
            wm group $w .

            menu $w.menubar
            $w configure -menu $w.menubar

            $w.menubar add cascade -label "File" -menu $w.menubar.fileMenu
            $w.menubar add cascade -label "Edit" -menu $w.menubar.editMenu

            menu $w.menubar.fileMenu
            menu $w.menubar.editMenu

            $w.menubar.fileMenu add command -label "Save" \
                    -underline 1 -command [list simpleEd save $filename $w]
            $w.menubar.fileMenu add command -label "Save As..." \
                    -underline 1 -command [list simpleEd saveAs $filename $w]
            $w.menubar.fileMenu add separator
            $w.menubar.fileMenu add command -label "Exit" \
                    -underline 1 -command [list simpleEd exit $w]

            $w.menubar.editMenu add command -label "Cut" \
                    -command [list event generate $w.text <<Cut>>]
            $w.menubar.editMenu add command -label "Copy" \
                    -command [list event generate $w.text <<Copy>>]
            $w.menubar.editMenu add command -label "Paste" \
                    -command [list event generate $w.text <<Paste>>]

            text $w.text -wrap none \
                    -xscrollcommand [list $w.hsb set] \
                    -yscrollcommand [list $w.vsb set] \
                    -borderwidth 0 -font $font
            scrollbar $w.vsb -orient vertical -command [list $w.text yview]
            scrollbar $w.hsb -orient horizontal -command [list $w.text xview]

            grid $w.text -row 0 -column 0 -sticky nsew
            grid $w.vsb  -row 0 -column 1 -sticky ns
            grid $w.hsb  -row 1 -column 0 -sticky ew

            grid columnconfigure $w 0 -weight 1
            grid columnconfigure $w 1 -weight 0
            grid rowconfigure    $w 0 -weight 1
            grid rowconfigure    $w 1 -weight 0

            set fd [open $filename]
            $w.text insert 1.0 [read $fd]
            close $fd
        }

        save {
            set filename [lindex $args 0]
            set w [lindex $args 1]
            set fd [open $filename w]
            puts $fd [$w.text get 1.0 "end-1c"]
            close $fd
        }

        saveAs {
            set filename [lindex $args 0]
            set w [lindex $args 1]
            set filename [tk_getSaveFile -initialfile $filename]
            if {$filename != ""} {
                simpleEd save $filename $w
            }
        }

        exit {
            set w [lindex $args 0]
            destroy $w
        }
    }

}

# end of simpleEd

#################################################################
# combobox.tcl reproduced here with permission from its author.
#################################################################
# Copyright (c) 1998, Bryan Oakley
# All Rights Reservered
#
# Bryan Oakley
# oakley@channelpoint.com
#
# combobox v1.07 October 9, 1998
#
# a combobox / dropdown listbox (pick your favorite name) widget
# written in pure tcl
#
# this code is freely distributable without restriction, but is
# provided as-is with no waranty expressed or implied.
#
# thanks to the following people who provided beta test support or
# patches to the code (in no particular order):
#
# Scott Beasley     Alexandre Ferrieux      Todd Helfter
# Matt Gushee       Laurent Duperval        John Jackson
# Fred Rapp         Christopher Nelson
# Eric Galluzzo     Jean-Francois Moine

# A special thanks to Martin M. Hunt who provided several good ideas,
# and always with a patch to implement them. Jean-Francois Moine,
# Todd Helfter and John Jackson were also kind enough to send in some
# code patches.

package require Tk 8.0
package provide combobox 1.07

namespace eval ::combobox {

    # this is the public interface
    namespace export combobox

    # get the scrollbar width. Because we try to be clever and draw our
    # own button instead of using a tk widget, we need to know what size
    # button to create. This little hack tells us the width of a scroll
    # bar.
    #
    # NB: we need to be sure and pick a window  that doesn't already
    # exist...
    set sbtest ".sbtest"
    set count 0
    while {[winfo exists $sbtest]} {
        set sbtest ".sbtest$count"
        incr count
    }
    scrollbar $sbtest
    set sb_width [winfo reqwidth $sbtest]
    destroy $sbtest

    # the image used for the button...
    image create bitmap ::combobox::bimage -data  {
        #define down_arrow_width 15
        #define down_arrow_height 15
        static char down_arrow_bits[] = {
            0x00,0x80,0x00,0x80,0x00,0x80,0x00,0x80,
            0x00,0x80,0xf8,0x8f,0xf0,0x87,0xe0,0x83,
            0xc0,0x81,0x80,0x80,0x00,0x80,0x00,0x80,
            0x00,0x80,0x00,0x80,0x00,0x80
        }
    }
}

# this is the command that gets exported, and creates a new
# combobox widget. It works like other widget commands in that
# it takes as its first argument a widget path, and any remaining
# arguments are option/value pairs for the widget
proc ::combobox::combobox {w args} {

    # build it...
    eval build $w $args

    # set some bindings...
    setBindings $w

    # and we are done!
    return $w
}


# builds the combobox...
proc ::combobox::build {w args } {
    if {[winfo exists $w]} {
        error "window name \"$w\" already exists"
    }

    # create the namespace for this instance, and define a few
    # variables
    namespace eval ::combobox::$w {

        variable ignoreTrace 0
        variable oldFocus    {}
        variable oldGrab     {}
        variable oldValue    {}
        variable options
        variable this
        variable widgets

    }

    # import the widgets and options arrays into this proc so
    # we don't have to use fully qualified names, which is a
    # pain.
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options

    # we need these to be defined, regardless if the user defined
    # them for us or not...
    array set options [list \
            -height       0 \
            -maxheight    10 \
            -command      {} \
            -image        {} \
            -textvariable {} \
            -editable     1 \
            -commandstate normal \
            -state          normal \
            -xscrollcommand {} \
    ]

    # this lets us reference the actual widget name from within
    # the namespace of the widget.
    namespace eval ::combobox::$w "set this $w"

    # the basic, always-visible parts of the combobox. We do these
    # here, because we want to query some of them for their default
    # values, which we want to juggle to other widgets. I suppose
    # I could use the options database, but for simplicity I choose
    # not to...
    set widgets(this)   [frame  $w -class Combobox -takefocus 0]
    set widgets(entry)  [entry  $w.entry -takefocus 1]
    set widgets(button) [label  $w.button -takefocus 0]

    # we will later rename the frame's widget proc to be our
    # own custom widget proc. We need to keep track of this
    # new name, so we'll define and store it here...
    set widgets(frame) ::combobox::${w}::$w

    # gotta do this sooner or later. Might as well do it now
    pack $widgets(entry)  -side left  -fill both -expand yes
    pack $widgets(button) -side right -fill y    -expand no

    # now, steal some attributes from the entry widget and store
    # them in our own options array
    foreach option [list -background -foreground -relief \
            -borderwidth -highlightthickness -highlightbackground \
            -font -width -selectbackground -selectborderwidth \
            -selectforeground -takefocus] {
        set options($option) [$widgets(entry) cget $option]
    }

    # I should probably do this in a catch, but for now it's
    # good enough... What it does, obviously, is put all of
    # the option/values pairs into an array. Make them easier
    # to handle later on...
    array set options $args

    # now, the dropdown list... the same renaming nonsense
    # must go on here as well...
    set widgets(popup)   [toplevel  $w.top]
    set widgets(listbox) [listbox   $w.top.list]
    set widgets(vsb)     [scrollbar $w.top.vsb]

    pack $widgets(listbox) -side left -fill both -expand y

    # fine tune the widgets based on the options (and a few
    # arbitrary values...)

    # NB: we are going to use the frame to handle the relief
    # of the widget as a whole, so the entry widget will be
    # flat. This makes the button which drops down the list
    # to appear "inside" the entry widget.

    $widgets(vsb) configure \
            -command "$widgets(listbox) yview" \
            -highlightthickness 0

    $widgets(button) configure \
            -highlightthickness 0 \
            -borderwidth 1 \
            -relief raised \
            -width [expr {[winfo reqwidth $widgets(vsb)] - 2}]

    $widgets(entry) configure \
            -borderwidth 0 \
            -relief flat \
            -textvariable ::combobox::${w}::entryTextVariable \
            -highlightthickness 0

    $widgets(popup) configure \
            -borderwidth 1 \
            -relief sunken

    $widgets(listbox) configure \
            -selectmode browse \
            -background [$widgets(entry) cget -bg] \
            -yscrollcommand "$widgets(vsb) set" \
            -borderwidth 0


    trace variable ::combobox::${w}::entryTextVariable w \
            [list ::combobox::entryTrace $w]

    # do some window management foo on the dropdown window
    wm overrideredirect $widgets(popup) 1
    wm transient        $widgets(popup) [winfo toplevel $w]
    wm group            $widgets(popup) [winfo parent $w]
    wm resizable        $widgets(popup) 0 0
    wm withdraw         $widgets(popup)

    # this moves the original frame widget proc into our
    # namespace and gives it a handy name
    rename ::$w $widgets(frame)

    # now, create our widget proc. Obviously (?) it goes in
    # the global namespace. All combobox widgets will actually
    # share the same widget proc to cut down on the amount of
    # bloat.
    proc ::$w {command args} \
            "eval ::combobox::widgetProc $w \$command \$args"

    # ok, the thing exists... let's do a bit more configuration.
    foreach opt [array names options] {
        ::combobox::configure $widgets(this) set $opt $options($opt)
    }


}

# this is called whenever the contents of the entry widget changes;
# it's main purpose is to update the public textvariable, if
# any
proc ::combobox::entryTrace {w args} {
    upvar ::combobox::${w}::options options
    upvar ::combobox::${w}::ignoreTrace ignoreTrace

    if {[string length $options(-textvariable)]} {
        set ignoreTrace 1
        uplevel \#0 [list set $options(-textvariable) \
                [set ::combobox::${w}::entryTextVariable]]
        unset ignoreTrace
    }
}

# here's where we do most of the binding foo. I think there's probably
# a few bindings I ought to add that I just haven't thought about...
#
# I'm not convinced these are the proper bindings. Ideally all bindings
# should be on "Combobox", but because of my juggling of bindtags I'm
# not convinced thats what I want to do. But, it all seems to work, its
# just not as robust as it could be.
proc ::combobox::setBindings {w} {
    namespace eval ::combobox::$w {
        variable widgets
        variable options

        # juggle the bindtags. The basic idea here is to associate the
        # widget name with the entry widget, so if a user does a bind
        # on the combobox it will get handled properly since it is
        # the entry widget that has keyboard focus.
        bindtags $widgets(entry) \
                [concat $widgets(this) [bindtags $widgets(entry)]]

        bindtags $widgets(button) \
                [concat $widgets(this) [bindtags $widgets(button)]]

        # make sure we clean up after ourselves...
        bind $widgets(entry) <Destroy> [list ::combobox::destroyHandler $this]

        # this closes the listbox if we get hidden
        bind $widgets(this) <Unmap> "$widgets(this) close"

        # this helps (but doesn't fully solve) focus issues. The general
        # idea is, whenever the frame gets focus it gets passed on to
        # the entry widget
        bind $widgets(this) <FocusIn> \
                "tkTabToWindow $widgets(entry)"

        # override the default bindings for tab and shift-tab. The
        # focus procs take a widget as their only parameter and we
        # want to make sure the right window gets used (for shift-
        # tab we want it to appear as if the event was generated
        # on the frame rather than the entry. I

        bind $widgets(entry) <Tab> \
                "tkTabToWindow \[tk_focusNext $widgets(entry)\]; break"
        bind $widgets(entry) <Shift-Tab> \
                "tkTabToWindow \[tk_focusPrev $widgets(this)\]; break"

        # this makes our "button" (which is actually a label)
        # do the right thing
        bind $widgets(button) <ButtonPress-1> [list $widgets(this) toggle]

        # this lets the autoscan of the listbox work, even if they
        # move the cursor over the entry widget.
        bind $widgets(entry) <B1-Enter> "break"

        # this will (hopefully) close (and lose the grab on) the
        # listbox if the user clicks anywhere outside of it. Note
        # that on Windows, you can click on some other app and
        # the listbox will still be there, because tcl won't see
        # that button click
        bind Combobox <Any-ButtonPress>  [list $widgets(this) close]
        bind Combobox <Any-ButtonRelease> [list $widgets(this) close]

        bind $widgets(listbox) <ButtonRelease-1> \
                "::combobox::select $widgets(this) \[$widgets(listbox) nearest %y\]; break"

        bind $widgets(vsb) <ButtonPress-1> {continue}
        bind $widgets(vsb) <ButtonRelease-1> {continue}

        bind $widgets(listbox) <Any-Motion> {
            %W selection clear 0 end
            %W activate @%x,%y
            %W selection anchor @%x,%y
            %W selection set @%x,%y @%x,%y
            # need to do a yview if the cursor goes off the top
            # or bottom of the window... (or do we?)
        }

        # these events need to be passed from the entry
        # widget to the listbox, or need some sort of special
        # handling....
        foreach event [list <Up> <Down> <Tab> <Return> <Escape> \
                <Next> <Prior> <Double-1> <1> <Any-KeyPress> \
                <FocusIn> <FocusOut>] {
            bind $widgets(entry) $event \
                    "::combobox::handleEvent $widgets(this) $event"
        }

    }
}

# this proc handles events from the entry widget that we want handled
# specially (typically, to allow navigation of the list even though
# the focus is in the entry widget)
proc ::combobox::handleEvent {w event} {
    upvar ::combobox::${w}::widgets  widgets
    upvar ::combobox::${w}::options  options
    upvar ::combobox::${w}::oldValue oldValue

    # for all of these events, if we have a special action we'll
    # do that and do a "return -code break" to keep additional
    # bindings from firing. Otherwise we'll let the event fall
    # on through.
    switch $event {

        "<Any-KeyPress>" {
            # if the widget is editable, clear the selection.
            # this makes it more obvious what will happen if the
            # user presses <Return> (and helps our code know what
            # to do if the user presses return)
            if {$options(-editable)} {
                $widgets(listbox) see 0
                $widgets(listbox) selection clear 0 end
                $widgets(listbox) selection anchor 0
                $widgets(listbox) activate 0
            }
        }

        "<FocusIn>" {
            set oldValue [$widgets(entry) get]
        }

        "<FocusOut>" {
            if {[winfo ismapped $widgets(popup)]} {
                return -code break

            } else {
                # did the value change?
                set newValue [set ::combobox::${w}::entryTextVariable]
                if {$oldValue != $newValue} {
                    callCommand $widgets(this) $newValue
                }
            }
        }

        "<1>" {
            set editable [::combobox::getBoolean $options(-editable)]
            if {!$editable} {
                if {[winfo ismapped $widgets(popup)]} {
                    $widgets(this) close
                    return -code break;

                } else {
                    if {$options(-state) != "disabled"} {
                        $widgets(this) open
                        return -code break;
                    }
                }
            }
        }

        "<Double-1>" {
            if {$options(-state) != "disabled"} {
                $widgets(this) toggle
                return -code break;
            }
        }

        "<Tab>" {
            if {[winfo ismapped $widgets(popup)]} {
                ::combobox::find $widgets(this)
                return -code break;
            } else {
                ::combobox::setValue $widgets(this) [$widgets(this) get]
            }
        }

        "<Escape>" {
            $widgets(entry) delete 0 end
            $widgets(entry) insert 0 $oldValue
            if {[winfo ismapped $widgets(popup)]} {
                $widgets(this) close
                return -code break;
            }
        }

        "<Return>" {
            # did the value change?
            set newValue [set ::combobox::${w}::entryTextVariable]
            if {$oldValue != $newValue} {
                callCommand $widgets(this) $newValue
            }

            if 0 {
            if {$options(-editable)} {
                # if there is something in the list that is selected,
                # we'll pick it. Otherwise, use whats in the
                # entry widget...
                set index [$widgets(listbox) curselection]
                if {[winfo ismapped $widgets(popup)] && \
                        [llength $index] > 0} {

                    ::combobox::select $widgets(this) \
                            [$widgets(listbox) curselection]
                    return -code break;

                } else {
                    # the value doesn't change in this case, but we
                    # do need to arrange for the -command to be called
                    callCommand $widgets(this) \
                            [set ::combobox::${w}::entryTextVariable]
                    $widgets(this) close

                    return
                }
            }
            }

            if {[winfo ismapped $widgets(popup)]} {
                ::combobox::select $widgets(this) \
                        [$widgets(listbox) curselection]
                return -code break;
            }

        }

        "<Next>" {
            $widgets(listbox) yview scroll 1 pages
            set index [$widgets(listbox) index @0,0]
            $widgets(listbox) see $index
            $widgets(listbox) activate $index
            $widgets(listbox) selection clear 0 end
            $widgets(listbox) selection anchor $index
            $widgets(listbox) selection set $index

        }

        "<Prior>" {
            $widgets(listbox) yview scroll -1 pages
            set index [$widgets(listbox) index @0,0]
            $widgets(listbox) activate $index
            $widgets(listbox) see $index
            $widgets(listbox) selection clear 0 end
            $widgets(listbox) selection anchor $index
            $widgets(listbox) selection set $index
        }

        "<Down>" {
            if {[winfo ismapped $widgets(popup)]} {
                tkListboxUpDown $widgets(listbox) 1
                return -code break;

            } else {
                if {$options(-state) != "disabled"} {
                    $widgets(this) open
                    return -code break;
                }
            }
        }
        "<Up>" {
            if {[winfo ismapped $widgets(popup)]} {
                tkListboxUpDown $widgets(listbox) -1
                return -code break;

            } else {
                if {$options(-state) != "disabled"} {
                    $widgets(this) open
                    return -code break;
                }
            }
        }
    }
}

# this cleans up the mess that is left behind when the widget goes away
# at least, that's the theory.
proc ::combobox::destroyHandler {w} {

    # kill any trace we may have started...
    namespace eval ::combobox::$w {
        variable options
        variable widgets

        # kill any trace we have for the user's -textvariable
        catch {
            if {[info exists options(-textvariable)]} {
                if {[string length $options(-textvariable)]} {
                    trace vdelete $options(-textvariable) w \
                            [list ::combobox::vTrace $widgets(this)]
                }
            }
        }
    }

    # kill the namespace
    catch {namespace delete ::combobox::$w}
}

# finds something in the listbox that matches the pattern in the
# entry widget
#
# I'm not convinced this is working the way it ought to. It works,
# but is the behavior what is expected? I've also got a gut feeling
# that there's a better way to do this, but I'm too lazy to figure
# it out...
proc ::combobox::find {w {exact 0}} {
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options

    ## *sigh* this logic is rather gross and convoluted. Surely
    ## there is a more simple, straight-forward way to implement
    ## all this. As the saying goes, I lack the time to make it
    ## shorter...

    # use what is already in the entry widget as a pattern
    set pattern [$widgets(entry) get]

    if {[string length $pattern] == 0} {
        # clear the current selection
        $widgets(listbox) see 0
        $widgets(listbox) selection clear 0 end
        $widgets(listbox) selection anchor 0
        $widgets(listbox) activate 0
        return
    }

    # we're going to be searching this list...
    set list [$widgets(listbox) get 0 end]

    # if we are doing an exact match, try to find,
    # well, an exact match
    if {$exact} {
        set exactMatch [lsearch -exact $list $pattern]
    }

    # search for it. We'll try to be clever and not only
    # search for a match for what they typed, but a match for
    # something close to what they typed. We'll keep removing one
    # character at a time from the pattern until we find a match
    # of some sort.
    set index -1
    while {$index == -1 && [string length $pattern]} {
        set index [lsearch -glob $list "$pattern*"]
        if {$index == -1} {
            regsub {.$} $pattern {} pattern
        }
    }

    # this is the item that most closely matches...
    set thisItem [lindex $list $index]

    # did we find a match? If so, do some additional munging...
    if {$index != -1} {

        # we need to find the part of the first item that is
        # unique wrt the second... I know there's probably a
        # simpler way to do this...

        set nextIndex [expr {$index + 1}]
        set nextItem [lindex $list $nextIndex]

        # we don't really need to do much if the next
        # item doesn't match our pattern...
        if {[string match $pattern* $nextItem]} {
            # ok, the next item matches our pattern, too
            # now the trick is to find the first character
            # where they *don't* match...
            set marker [string length $pattern]
            while {$marker <= [string length $pattern]} {
                set a [string index $thisItem $marker]
                set b [string index $nextItem $marker]
                if {[string compare $a $b] == 0} {
                    append pattern $a
                    incr marker
                } else {
                    break
                }
            }
        } else {
            set marker [string length $pattern]
        }

    } else {
        set marker end
        set index 0
    }

    # ok, we know the pattern and what part is unique;
    # update the entry widget and listbox appropriately
    if {$exact && $exactMatch == -1} {
        $widgets(listbox) selection clear 0 end
        $widgets(listbox) see $index
    } else {
        $widgets(entry) delete 0 end
        $widgets(entry) insert end $thisItem
        $widgets(entry) selection clear
        $widgets(entry) selection range $marker end
        $widgets(listbox) activate $index
        $widgets(listbox) selection clear 0 end
        $widgets(listbox) selection anchor $index
        $widgets(listbox) selection set $index
        $widgets(listbox) see $index
    }
}

# selects an item from the list and sets the value of the combobox
# to that value
proc ::combobox::select {w index} {
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options

    catch {
        set data [$widgets(listbox) get [lindex $index 0]]
        ::combobox::setValue $widgets(this) $data
        $widgets(entry) selection range 0 end
    }

    $widgets(this) close
}

proc ::combobox::handleScrollbar {w {action "unknown"}} {
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options

    if {$options(-height) == 0} {
        set hlimit $options(-maxheight)
    } else {
        set hlimit $options(-height)
    }

    switch $action {
        "grow" {
            if {$hlimit > 0 && [$widgets(listbox) size] > $hlimit} {
                pack $widgets(vsb) -side right -fill y -expand n
            }
        }

        "shrink" {
            if {$hlimit > 0 && [$widgets(listbox) size] <= $hlimit} {
                pack forget $widgets(vsb)
            }
        }

        "crop" {
            # this means the window was cropped and we definitely
            # need a scrollbar no matter what the user wants
            pack $widgets(vsb) -side right -fill y -expand n
        }

        default {
            if {$hlimit > 0 && [$widgets(listbox) size] > $hlimit} {
                pack $widgets(vsb) -side right -fill y -expand n
            } else {
                pack forget $widgets(vsb)
            }
        }
    }
}

# computes the geometry of the popup list based on the size of the
# combobox...
proc ::combobox::computeGeometry {w} {
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options

    if {$options(-height) == 0 && $options(-maxheight) != "0"} {
        # if this is the case, count the items and see if
        # it exceeds our maxheight. If so, set the listbox
        # size to maxheight...
        set nitems [$widgets(listbox) size]
        if {$nitems > $options(-maxheight)} {
            # tweak the height of the listbox
            $widgets(listbox) configure -height $options(-maxheight)
        } else {
            # un-tweak the height of the listbox
            $widgets(listbox) configure -height 0
        }
        update idletasks
    }

    # compute height and width of the dropdown list
    set bd [$widgets(popup) cget -borderwidth]
    set height [expr {[winfo reqheight $widgets(popup)] + $bd + $bd}]
    set width [winfo width $widgets(this)]

    # figure out where to place it on the screen, trying to take into
    # account we may be running under some virtual window manager
    set screenWidth  [winfo screenwidth $widgets(this)]
    set screenHeight [winfo screenheight $widgets(this)]
    set rootx        [winfo rootx $widgets(this)]
    set rooty        [winfo rooty $widgets(this)]
    set vrootx       [winfo vrootx $widgets(this)]
    set vrooty       [winfo vrooty $widgets(this)]

    # the x coordinate is simply the rootx of our widget, adjusted for
    # the virtual window. We won't worry about whether the window will
    # be offscreen to the left or right -- we want the illusion that it
    # is part of the entry widget, so if part of the entry widget is off-
    # screen, so will the list. If you want to change the behavior,
    # simply change the if statement... (and be sure to update this
    # comment!)
    set x  [expr {$rootx + $vrootx}]
    if {0} {
        set rightEdge [expr {$x + $width}]
        if {$rightEdge > $screenWidth} {
            set x [expr {$screenWidth - $width}]
        }
        if {$x < 0} {set x 0}
    }

    # the y coordinate is the rooty plus vrooty offset plus
    # the height of the static part of the widget plus 1 for a
    # tiny bit of visual separation...
    set y [expr {$rooty + $vrooty + [winfo reqheight $widgets(this)] + 1}]
    set bottomEdge [expr {$y + $height}]

    if {$bottomEdge >= $screenHeight} {
        # ok. Fine. Pop it up above the entry widget isntead of
        # below.
        set y [expr {($rooty - $height - 1) + $vrooty}]

        if {$y < 0} {
            # this means it extends beyond our screen. How annoying.
            # Now we'll try to be real clever and either pop it up or
            # down, depending on which way gives us the biggest list.
            # then, we'll trim the list to fit and force the use of
            # a scrollbar

            # (sadly, for windows users this measurement doesn't
            # take into consideration the height of the taskbar,
            # but don't blame me -- there isn't any way to detect
            # it or figure out its dimensions. The same probably
            # applies to any window manager with some magic windows
            # glued to the top or bottom of the screen)

            if {$rooty > [expr {$screenHeight / 2}]} {
                # we are in the lower half of the screen --
                # pop it up. Y is zero; that parts easy. The height
                # is simply the y coordinate of our widget, minus
                # a pixel for some visual separation. The y coordinate
                # will be the topof the screen.
                set y 1
                set height [expr {$rooty - 1 - $y}]

            } else {
                # we are in the upper half of the screen --
                # pop it down
                set y [expr {$rooty + $vrooty + \
            [winfo reqheight $widgets(this)] + 1}]
                set height [expr {$screenHeight - $y}]

    }

            # force a scrollbar
            handleScrollbar $widgets(this) crop
        }
    }

    if {$y < 0} {
        # hmmm. Bummer.
        set y 0
        set height $screenheight
    }

    set geometry [format "=%dx%d+%d+%d" $width $height $x $y]
    return $geometry
}

# perform an internal widget command, then mung any error results
# to look like it came from our megawidget. A lot of work just to
# give the illusion that our megawidget is an atomic widget
proc ::combobox::doInternalWidgetCommand {w subwidget command args} {
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options

    set subcommand $command
    set command [concat $widgets($subwidget) $command $args]
    if {[catch $command result]} {
        # replace the subwidget name with the megawidget name
        regsub $widgets($subwidget) $result $widgets(this) result

        # replace specific instances of the subwidget command
        # with out megawidget command
        switch $subwidget,$subcommand {
            listbox,index  {regsub "index"  $result "list index"  result}
            listbox,insert {regsub "insert" $result "list insert" result}
            listbox,delete {regsub "delete" $result "list delete" result}
            listbox,get    {regsub "get"    $result "list get"    result}
            listbox,size   {regsub "size"   $result "list size"   result}
        }
        error $result

    } else {
        return $result
    }
}


# this is the widget proc that gets called when you do something like
# ".checkbox configure ..."
proc ::combobox::widgetProc {w command args} {
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options
    upvar ::combobox::${w}::oldFocus oldFocus
    upvar ::combobox::${w}::oldFocus oldGrab

    # this is just shorthand notation...
    set doWidgetCommand \
            [list ::combobox::doInternalWidgetCommand $widgets(this)]

    if {$command == "list"} {
        # ok, the next argument is a list command; we'll
        # rip it from args and append it to command to
        # create a unique internal command
        #
        # NB: because of the sloppy way we are doing this,
        # we'll also let the user enter our secret command
        # directly (eg: listinsert, listdelete), but we
        # won't document that fact
        set command "list[lindex $args 0]"
        set args [lrange $args 1 end]
    }

    # many of these commands are just synonyms for specific
    # commands in one of the subwidgets. We'll get them out
    # of the way first, then do the custom commands.
    switch $command {
        bbox            {eval $doWidgetCommand entry bbox $args}
        delete          {eval $doWidgetCommand entry delete $args}
        get             {eval $doWidgetCommand entry get $args}
        icursor         {eval $doWidgetCommand entry icursor $args}
        index           {eval $doWidgetCommand entry index $args}
        insert          {eval $doWidgetCommand entry insert $args}
        scan            {eval $doWidgetCommand entry scan $args}
        selection       {eval $doWidgetCommand entry selection $args}
        xview           {eval $doWidgetCommand entry xview $args}
        listget         {eval $doWidgetCommand listbox get $args}
        listindex       {eval $doWidgetCommand listbox index $args}
        listsize        {eval $doWidgetCommand listbox size $args}

        subwidget {
            set knownWidgets [list button entry listbox popup vsb]
            if {[llength $args] == 0} {
                return $knownWidgets
            }

            set name [lindex $args 0]
            if {[lsearch $knownWidgets $name] != -1} {
                return $widgets($name)
            } else {
                error "unknown subwidget $name"
            }
        }

        listinsert {
            eval $doWidgetCommand listbox insert $args
            handleScrollbar $w "grow"
        }

        listdelete {
            eval $doWidgetCommand listbox delete $args
            handleScrollbar $w "shrink"
        }

        toggle {
            # ignore this command if the widget is disabled...
            if {$options(-state) == "disabled"} return

            # pops down the list if it is not, hides it
            # if it is...
            if {[winfo ismapped $widgets(popup)]} {
                $widgets(this) close
            } else {
                $widgets(this) open
            }
        }

        open {

            # if this is an editable combobox, the focus should
            # be set to the entry widget
            if {$options(-editable)} {
                focus $widgets(entry)
                $widgets(entry) select range 0 end
                $widgets(entry) icur end
            }

            # if we are disabled, we won't allow this to happen
            if {$options(-state) == "disabled"} {
                return 0
            }

            # compute the geometry of the window to pop up, and set
            # it, and force the window manager to take notice
            # (even if it is not presently visible).
            #
            # this isn't strictly necessary if the window is already
            # mapped, but we'll go ahead and set the geometry here
            # since its harmless and *may* actually reset the geometry
            # to something better in some weird case.
            set geometry [::combobox::computeGeometry $widgets(this)]
            wm geometry $widgets(popup) $geometry
            update idletasks

            # if we are already open, there's nothing else to do
            if {[winfo ismapped $widgets(popup)]} {
                return 0
            }

            # save the widget that currently has the focus; we'll restore
            # the focus there when we're done
            set oldFocus [focus]

            # ok, tweak the visual appearance of things and
            # make the list pop up
            $widgets(button) configure -relief sunken
            wm deiconify $widgets(popup)
            raise $widgets(popup) [winfo parent $widgets(this)]

            # force focus to the entry widget so we can handle keypress
            # events for traversal
            focus -force $widgets(entry)

            # select something by default, but only if its an
            # exact match...
            ::combobox::find $widgets(this) 1

            # save the current grab state for the display containing
            # this widget. We'll restore it when we close the dropdown
            # list
            set status "none"
            set grab [grab current $widgets(this)]
            if {$grab != ""} {set status [grab status $grab]}
            set oldGrab [list $grab $status]
            unset grab status

            # *gasp* do a global grab!!! Mom always told not to
            # do things like this, but these are desparate times.
            grab -global $widgets(this)

            # fake the listbox into thinking it has focus. This is
            # necessary to get scanning initialized properly in the
            # listbox.
            event generate $widgets(listbox) <B1-Enter>

            return 1
        }

        close {
            # if we are already closed, don't do anything...
            if {![winfo ismapped $widgets(popup)]} {
                return 0
            }

            # restore the focus and grab, but ignore any errors...
            # we're going to be paranoid and release the grab before
            # trying to set any other grab because we really really
            # really want to make sure the grab is released.
            catch {focus $oldFocus} result
            catch {grab release $widgets(this)}
            catch {
                set status [lindex $oldGrab 1]
                if {$status == "global"} {
                    grab -global [lindex $oldGrab 0]
                } elseif {$status == "local"} {
                    grab [lindex $oldGrab 0]
                }
                unset status
            }

            # hides the listbox
            $widgets(button) configure -relief raised
            wm withdraw $widgets(popup)

            # select the data in the entry widget. Not sure
            # why, other than observation seems to suggest that's
            # what windows widgets do.
            set editable [::combobox::getBoolean $options(-editable)]
            if {$editable} {
                $widgets(entry) selection range 0 end
                $widgets(button) configure -relief raised
            }


            # magic tcl stuff (see tk.tcl in the distribution
            # lib directory)
            tkCancelRepeat

            return 1
        }

        cget {
            # tries to mimic the standard "cget" command
            if {[llength $args] != 1} {
                error "wrong # args: should be \"$widgets(this) cget option\""
            }
            set option [lindex $args 0]
            return [::combobox::configure $widgets(this) cget $option]
        }

        configure {
            # trys to mimic the standard "configure" command
            if {[llength $args] == 0} {
                # this isn't the same format as "real" widgets,
                # but for now its good enough
                foreach item [lsort [array names options]] {
                    lappend result [list $item $options($item)]
                }
                return $result

            } elseif {[llength $args] == 1} {
                # they are requesting configure information...
                set option [lindex $args 0]
                return [::combobox::configure $widgets(this) get $option]
            } else {
                array set tmpopt $args
                foreach opt [array names tmpopt] {
                    ::combobox::configure $widgets(this) set $opt $tmpopt($opt)
                }
            }
        }
        default {
            error "bad option \"$command\""
        }
    }
}

# handles all of the configure and cget foo
proc ::combobox::configure {w action {option ""} {newValue ""}} {
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options
    set namespace "::combobox::${w}"

    if {$action == "get"} {
        # this really ought to do more than just get the value,
        # but for the time being I don't fully support the configure
        # command in all its glory...
        if {$option == "-value"} {
            return [list "-value" [$widgets(entry) get]]
        } else {
            return [list $option $options($option)]
        }

    } elseif {$action == "cget"} {
        if {$option == "-value"} {
            return [$widgets(entry) get]
        } else {
            return $options($option)
        }

    } else {

        if {[info exists options($option)]} {
            set oldValue $options($option)
            set options($option) $newValue
        } else {
            set oldValue ""
            set options($option) $newValue
        }

        # some (actually, most) options require us to
        # do something, like change the attributes of
        # a widget or two. Here's where we do that...
        switch -- $option {
            -background {
                $widgets(frame)   configure -background $newValue
                $widgets(entry)   configure -background $newValue
                $widgets(listbox) configure -background $newValue
                $widgets(vsb)     configure -background $newValue
                $widgets(vsb)     configure -troughcolor $newValue
            }

            -borderwidth {
                $widgets(frame) configure -borderwidth $newValue
            }

            -command {
                # nothing else to do...
            }

            -commandstate {
                # do some value checking...
                if {$newValue != "normal" && $newValue != "disabled"} {
                    set options($option) $oldValue
                    error "bad state value \"$newValue\"; must be normal or disabled"
                }
            }

            -cursor {
                $widgets(frame) configure -cursor $newValue
                $widgets(entry) configure -cursor $newValue
                $widgets(listbox) configure -cursor $newValue
            }

            -editable {
                if {$newValue} {
                    # it's editable...
                    $widgets(entry) configure -state normal
                } else {
                    $widgets(entry) configure -state disabled
                }
            }

            -font {
                $widgets(entry) configure -font $newValue
                $widgets(listbox) configure -font $newValue
            }

            -foreground {
                $widgets(entry)   configure -foreground $newValue
                $widgets(button)  configure -foreground $newValue
                $widgets(listbox) configure -foreground $newValue
            }

            -height {
                $widgets(listbox) configure -height $newValue
                handleScrollbar $w
            }

            -highlightbackground {
                $widgets(frame) configure -highlightbackground $newValue
            }

            -highlightcolor {
                $widgets(frame) configure -highlightcolor $newValue
            }

            -highlightthickness {
                $widgets(frame) configure -highlightthickness $newValue
            }

            -image {
                if {[string length $newValue] > 0} {
                    $widgets(button) configure -image $newValue
                } else {
                    $widgets(button) configure -image ::combobox::bimage
                }
            }

            -maxheight {
                # computeGeometry may dork with the actual height
                # of the listbox, so let's undork it
                $widgets(listbox) configure -height $options(-height)
                handleScrollbar $w
            }

            -relief {
                $widgets(frame) configure -relief $newValue
            }

            -selectbackground {
                $widgets(entry) configure -selectbackground $newValue
                $widgets(listbox) configure -selectbackground $newValue
            }

            -selectborderwidth {
                $widgets(entry) configure -selectborderwidth $newValue
                $widgets(listbox) configure -selectborderwidth $newValue
            }

            -selectforeground {
                $widgets(entry) configure -selectforeground $newValue
                $widgets(listbox) configure -selectforeground $newValue
            }

            -state {
                if {$newValue == "normal"} {
                    # it's enabled
                    set editable [::combobox::getBoolean \
                            $options(-editable)]
                    if {$editable} {
                        $widgets(entry) configure -state normal
                        $widgets(entry) configure -takefocus 1
                    }
                } elseif {$newValue == "disabled"}  {
                    # it's disabled
                    $widgets(entry) configure -state disabled
                    $widgets(entry) configure -takefocus 0

                } else {
                    set options($option) $oldValue
                    error "bad state value \"$newValue\"; must be normal or disabled"
                }

            }

            -takefocus {
                $widgets(entry) configure -takefocus $newValue
            }

            -textvariable {
                # destroy our trace on the old value, if any
                if {[string length $oldValue] > 0} {
                    trace vdelete $oldValue w \
                            [list ::combobox::vTrace $widgets(this)]
                }
                # set up a trace on the new value, if any. Also, set
                # the value of the widget to the current value of
                # the variable

                set variable ::$newValue
                if {[string length $newValue] > 0} {
                    if {[info exists $variable]} {
                        ::combobox::setValue $widgets(this) [set $variable]
                    }
                    trace variable $variable w \
                            [list ::combobox::vTrace $widgets(this)]
                }
            }

            -value {
                ::combobox::setValue $widgets(this) $newValue
            }

            -width {
                $widgets(entry) configure -width $newValue
                $widgets(listbox) configure -width $newValue
            }

            -xscrollcommand {
                $widgets(entry) configure -xscrollcommand $newValue
            }

            default {
                error "unknown option \"$option\""
            }
        }
    }
}

# this proc is called whenever the user changes the value of
# the -textvariable associated with a widget
proc ::combobox::vTrace {w args} {
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options
    upvar ::combobox::${w}::ignoreTrace ignoreTrace

    if {[info exists ignoreTrace]} return
    ::combobox::setValue $widgets(this) [set ::$options(-textvariable)]
}

# sets the value of the combobox and calls the -command, if defined
proc ::combobox::setValue {w newValue {index -1}} {
    upvar ::combobox::${w}::widgets     widgets
    upvar ::combobox::${w}::options     options
    upvar ::combobox::${w}::ignoreTrace ignoreTrace
    upvar ::combobox::${w}::oldValue    oldValue

    # set our internal textvariable; this will cause any public
    # textvariable (ie: defined by the user) to be updated as
    # well
    set ::combobox::${w}::entryTextVariable $newValue

    # redefine our concept of the "old value". Do it before running
    # any associated command so we can be sure it happens even
    # if the command somehow fails.
    set oldValue $newValue

    # call the associated command. The proc will handle whether or
    # not to actually call it, and with what args
    callCommand $w $newValue
}

# call the associated command, if any
proc ::combobox::callCommand {w newValue} {
    upvar ::combobox::${w}::widgets widgets
    upvar ::combobox::${w}::options options

    # call the associated command, if defined and -commandstate is
    # set to "normal"
    if {$options(-commandstate) == "normal" && \
            [string length $options(-command)] > 0} {
        set args [list $widgets(this) $newValue]
        uplevel \#0 $options(-command) $args
    }
}


# returns the value of a (presumably) boolean string (ie: it should
# do the right thing if the string is "yes", "no", "true", 1, etc
proc ::combobox::getBoolean {value {errorValue 1}} {
    if {[catch {expr {([string trim $value])?1:0}} res]} {
        return $errorValue
    } else {
        return $res
    }
}

# computes the combobox widget name based on the name of one of
# it's children widgets.. Not presently used, but might come in
# handy...
proc ::combobox::widgetName {w} {
    while {$w != "."} {
        if {[winfo class $w] == "Combobox"} {
            return $w
        }
        set w [winfo parent $w]
    }
    error "internal error: $w is not a child of a combobox"
}


# end of combobox.tcl

######################################################################
# icon image data. 
######################################################################
image create photo findImage -format gif -data {
R0lGODdhFAAUAPf/AAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1P/isf/Ujv/G
a/+4SP+qJf+qANySALl6AJZiAHNKAFAyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAQAjUAAMIHEiwoEF3
AOQpXMiQIQB3ARC6a6fO3buHAiVWfAcPYwB1AN6pa/fQnUkAIy+qEwiy3bp07DqaPPmS3TqS
Kz/SA8ATQDyB8XoCoJczI4B2F+VBjCjvocyBCNOVS9cxAE+rUqliRHhznbunEY96dbl15kyC
Zs8OrDgzJ1uTRVnSYzcO5M8AQeu6I0oQ5DukAOAJlglPJVR5gBMifNjUqTyoAM6NK1f1auTJ
YDuuOxdTKM/NneGFHVkRLEKKE0GeFGzRdODWMhd7Xipb6FKDuAsGBAA7
}

image create photo centerDiffsImage -format gif -data {
R0lGODlhFAAUAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1P/isf/Ujv/G
a/+4SP+qJf+qANySALl6AJZiAHNKAFAyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAAAiUAAMIHBjAHYCD
ANwRHHjOncOHBgkRSgjRYUOEGAEYMpQRoUMA/8SJFGdwY0JyKFFSBGCuZcuSHN25bLmyo0aO
Nj+GJAkg0caNiU6q/DjToE9DQWW6rNkxUdCcBneONHhy5FCDM106zErzo82vB3XuTEm27Equ
aJd6BQsVpFSRZcmeTYuWKduM7hpW3Lv33MK/gAUGBAA7
}

image create photo firstDiffImage -format gif -data {
R0lGODlhFAAUAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1P/isf/Ujv/G
a/+4SP+qJf+qANySALl6AJZiAHNKAFAyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAAAiUAAMIdFevoMGD
Bd0JXBig3j9ChAxJnDixHkOBDilqlGjxIkGEIBVevHjOnbtzI1MKLAkAwEmVJN0BIKTIJUqY
AVgS+neo5kuVOv9J7Gkzpc5BFIn+XHg06SGlN1fKbDlTYiKqRRmWNFnV0FWTS7XqtGoz6six
XrMClRkxbdizbMm+jQngUKK7ao1OxTo3JliTZgUGBAA7
}

image create photo prevDiffImage -format gif -data {
R0lGODdhFAAUAPf/AAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1P/isf/Ujv/G
a/+4SP+qJf+qANySALl6AJZiAHNKAFAyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAQAiGAAMIHCjwnDt3
5wgqLHjQHQBChgwlAtAw4cIABh9GnIjwIsOH/yIeUkTR4sWMECWW9DgQJcmOJx0SGhRR5KGR
Kxei3JjT406VMH06BECUaFCWGXsilfkP51GCKGnWdGryY9GUE4s+xfiT47mqCrsq1SmT51ao
ZYGCDevwUKK3Y8k2PLg2IAA7
}

image create photo nextDiffImage -format gif -data {
R0lGODdhFAAUAPf/AAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1P/isf/Ujv/G
a/+4SP+qJf+qANySALl6AJZiAHNKAFAyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAQAiGAAMIHHjOncGD
5wYqVFgQACFDhhIBcJdwIUN3DgsdUjSxokWBDR9G7PixIYCTIiWeJGmx4T9ChA6x/BggJESJ
FGnWtDmSoseLGSFC3DizJMaiNE2uRLrQ5U2mQFNCJYhRak6dPHH+vGjQ4VOETasWEmrokFmO
V6OOLYt2a1iHbXWGTbswIAA7
}

image create photo lastDiffImage -format gif -data {
R0lGODlhFAAUAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1P/isf/Ujv/G
a/+4SP+qJf+qANySALl6AJZiAHNKAFAyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAAAiTAAMIHHjOncGD
5wYqVFgQgMOH7hIuZOgOwD9ChA4BiDiRokVDhhJtlNgxQENCIEVyLGmyIsqQI1meO5lyJEmK
BgG8VGnwZsuHOmtCvHmyEEiQh5IqiumRkNGjh5auXFgUqVSfTQtFZSrT5VWWHrmCFVhwakl3
9dKqXZvW3cR6F18enVvv7b+5eEHWXYiWrV+3AgMCADs=
}

image create photo rediffImage -format gif -data {
R0lGODdhFAAUAPf/AAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1P/isf/Ujv/G
a/+4SP+qJf+qANySALl6AJZiAHNKAFAyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQCrPQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAQAicAAMIHEiwoMF0
7AD0euVKl8OHrhjqAgDvnDsAGDOmG2jR3TmDIAVaxFiRoMJXKF/1ypgR5UqPIWOCTIfQnc2b
ABpS/Bgg3cmUQIOqBHBxIUpYADYKLEqUp8ynUKMatFgy5LmrWEdOrDoQIcuvrnSWPJfQqFCg
YhPCAtqrrduUL8/9fIWUJs2LQ2EGmFt34MWmBNPdvKlUquEAAQEAOw==
}

image create photo markSetImage -format gif -data {
R0lGODlhFAAUAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1Pjisd/UjtHJ
a8O4SL2qJcWqAK+SAJN6AGJiAEpKADIyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAAAiZAAMIHEhQoLqD
CAsqFAigIQB3Dd0tNKjOXSxXrmABWBABgLqCByECuAir5EYJHimKvOgqFqxXrzZ2lBhgJUaY
LV/GOpkSIqybOF3ClPlQIEShMF/lfLVzAcqPRhsKXRqTY1GCFaUy1ckTKkiRGhtapTkxa82u
ExUSJZs2qtOUbQ2ujTsQ4luvbdXNpRtA712+UeEC7ou3YEAAADt=
}

image create photo markClearImage -format gif -data {
R0lGODlhFAAUAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1Pjisd/UjtHJ
a8O4SL2qJcWqAK+SAJN6AGJiAEpKADIyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAAAiwAAMIHEhQoLqD
CAsCWKhwIbyFANwNXBiD4UF3sVw9rLhQXQCKNTguzLgxZMePMWqo5OgqVkmVNwAIXHhDpUl3
7gCkhMkwJ02bHHfWiCkzQM5YP1cKJepRoM+kNoculEhQXc6cNW3GzNm0oFWdUSviLDgRbFST
RRsuzYpWrVaoHMsujYgVKMOPUYkCWPCQbY2iP/UuiACgr9S0NDvulQBAXd+7ZYv6bPowLdmB
By8LDAgAOw==
}

image create photo mergeChoice1Image -format gif -data {
R0lGODdhFAAUAPf/AAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1P/isf/Ujv/G
a/+4SP+qJf+qANySALl6AJZiAHNKAFAyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAQAiIAAMIHEiwYMFz
7gAQ+meoIaGHECEeAuDuoDt35wxqFIgQAMWMGzkmVHRooseTKD1WPAgy5MCOhAZRvEizJsaR
hxrq3LkzEcWXIz+eG0qUqMujSJMixJg0AEyhRYuKVDjIUMqrMxUy5MnVkM+bAEgaOpSorNmz
X6eSnGmzZkunCT825fh2btKAADt=
}

image create photo mergeChoice2Image -format gif -data {
R0lGODdhFAAUAPf/AAAAAIAAAACAAICAAAAAgIAAgACAgMDAwMDcwKbK8P/w1P/isf/Ujv/G
a/+4SP+qJf+qANySALl6AJZiAHNKAFAyAP/j1P/Hsf+rjv+Pa/9zSP9XJf9VANxJALk9AJYx
AHMlAFAZAP/U1P+xsf+Ojv9ra/9ISP8lJf4AANwAALkAAJYAAHMAAFAAAP/U4/+xx/+Oq/9r
j/9Ic/8lV/8AVdwASbkAPZYAMXMAJVAAGf/U8P+x4v+O1P9rxv9IuP8lqv8AqtwAkrkAepYA
YnMASlAAMv/U//+x//+O//9r//9I//8l//4A/twA3LkAuZYAlnMAc1AAUPDU/+Kx/9SO/8Zr
/7hI/6ol/6oA/5IA3HoAuWIAlkoAczIAUOPU/8ex/6uO/49r/3NI/1cl/1UA/0kA3D0AuTEA
liUAcxkAUNTU/7Gx/46O/2tr/0hI/yUl/wAA/gAA3AAAuQAAlgAAcwAAUNTj/7HH/46r/2uP
/0hz/yVX/wBV/wBJ3AA9uQAxlgAlcwAZUNTw/7Hi/47U/2vG/0i4/yWq/wCq/wCS3AB6uQBi
lgBKcwAyUNT//7H//47//2v//0j//yX//wD+/gDc3AC5uQCWlgBzcwBQUNT/8LH/4o7/1Gv/
xkj/uCX/qgD/qgDckgC5egCWYgBzSgBQMtT/47H/x47/q2v/j0j/cyX/VwD/VQDcSQC5PQCW
MQBzJQBQGdT/1LH/sY7/jmv/a0j/SCX/JQD+AADcAAC5AACWAABzAABQAOP/1Mf/sav/jo//
a3P/SFf/JVX/AEncAD25ADGWACVzABlQAPD/1OL/sdT/jsb/a7j/SKr/Jar/AJLcAHq5AGKW
AEpzADJQAP//1P//sf//jv//a///SP//Jf7+ANzcALm5AJaWAHNzAFBQAPLy8ubm5tra2s7O
zsLCwra2tqqqqp6enpKSkoaGhnp6em5ubmJiYlZWVkpKSj4+PjIyMiYmJhoaGg4ODv/78KCg
pICAgP8AAAD/AP//AAAA//8A/wD//////yH5BAEAAAEALAAAAAAUABQAQAiNAAMIHEiwYEF3
AP79GzSIkMOHhAwZKkQIgLtzBguec3cxo8eNACxiHIgwpMmTIQ8dUiTSo8aRBDdynEkTIcWW
ARBGlMizJ8+VFgOcG0q0KEKWHV0qXcp0qUyYA4tKBVkxaU6UWAFMrIoR4SCfYCXe5AjgUKKz
aNMeMgT0osyaNMsihfqxpNWmQ5s2DQgAOw==
}

image create photo nullImage 

# run the main proc
main
