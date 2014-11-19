chord_compiler
==============
Takes a text document containing a list of songs and artists, and searches
ultimate guitar for the highest rated version of each song. If it exists,
the clear-text version of the chords/lyrics is saved to a text file in a
created /bin output directory.

Input file consits of one tab seperated song entry on each line, in the format '{song}\t{artist}\n'
Input is case insensitive

Output folder consists of a seperate text file for each song, in the format '{song}.txt'
Output folder also contains a log file of the run 'aaa_log.txt' and a file 'aaa_errors.txt'
which contains a list of songs not successfully retrieved, in a format that can later be
used as an input file

Ouput folders are named by the time the run began

NB: Requires bs4 package to be installed

Jordan Griffiths
2014
