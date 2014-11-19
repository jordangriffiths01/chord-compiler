'''GUITAR CHORDS/LYRICS COMPILER
Takes a text document containing a list of songs and artists, and searches
ultimate guitar for the highest rated version of each song. If it exists,
the clear-text version of the chords/lyrics is saved to a text file in a
created output directory.

Jordan Griffiths
November 2014'''

import time
import sys
import os
import re
import urllib.request
from bs4 import BeautifulSoup

DOMAIN = "http://tabs.ultimate-guitar.com/"
STARTFLAG = '+ --------------------------------------------------------------------- +'
ENDFLAG = '/* Ultimate-Guitar - Tab Pages */'
FOLDERNAME = 'outfile' + time.strftime("%I_%M_%S")
OUTFOLDER = os.path.abspath('bin/' + FOLDERNAME)
SEARCH_URL = 'http://www.ultimate-guitar.com/search.php?search_type=title&value='
LOGFILE = OUTFOLDER + '/aaa_log.txt'
ERRORFILE = OUTFOLDER + '/aaa_errors.txt'

def main():
    
    try:
        songs = loadsongs()
    except Exception as e:
        print('Error loading songs from file:', e)
        
    else:
        os.makedirs(OUTFOLDER)
        
        start = 'STARTED AT ' + time.strftime("%I_%M_%S")
        print(start)
        log = open(LOGFILE, 'a')
        log.write(start + '\n\n')
        log.close()     
        
        for song in songs:
            try:
                html = get_html(song[0], song[1])
                plaintext = get_plaintext(html)
                add_to_file(song, plaintext)
                log = open(LOGFILE, 'a')
                log.write('SUCCESSFULY RETRIEVED\n\n')
                log.close()
                
            except Exception as e:
                log = open(LOGFILE, 'a')
                log.write('\tERROR:\t' + str(e) + '\n\n')
                log.close()
                errors = open(ERRORFILE, 'a')
                errors.write('{}\t{}\n'.format(song[0], song[1]))
                errors.close()
                
        end = 'FINISHED AT ' + time.strftime("%I_%M_%S")
        print(end)
        log = open(LOGFILE, 'a')
        log.write(end)
        log.close()    

def loadsongs():
    '''loads songs from text file into a list of tuples (song, artist)'''
    
    infile_name = get_filename_from_user()
    songs = []
    try:
        f = open(infile_name, 'r', encoding='utf-8')
    except:
        raise IOError('File Not Found')
    lines = f.readlines()
    for line in lines:
        line = line.strip().split('\t')
        songs.append((line[0], line[1]))
        
    f.close()
    return songs

def get_filename_from_user():
    '''gets a valid filename from user input, 'q' raises I/O exception'''
    
    filename = input('Enter Filename (q to quit): ')
    if filename == 'q':
        raise IOError('Input Terminated')
    while type(filename) != str or not filename.endswith('.txt'):
        filename = input('Invalid Filename -- Enter Filename (q to quit): ')
        if filename == 'q':
            raise IOError('Input Terminated')        
    return filename


def add_to_file(song, plaintext):
    '''Creates a new text file in the ouput directory with the chords/lyrics
    of the given song'''
    
    filename = OUTFOLDER + '/' + song[0] +'.txt'
    f = open(filename, 'w', encoding='utf-8')
    f.write('**************** {} by {} ****************\n'.format(song[0], song[1]))
    f.write(plaintext)
    f.close()
    

def get_html(song, artist):
    '''Returns the HTML source code for the highest rated page for the given
    song'''
    
    version = find_highest_rating_version(song, artist)
    url = get_url(song, artist, version)
    log = open(LOGFILE, 'a')
    log.write('**** accessing ' + url + '\n')
    log.close()
    f = urllib.request.urlopen(url)
    source = f.read()
    f.close()
    return source


def get_url(song, artist, version):
    '''Converts a given song, artist and version number into a url in the
    standard ultimate guitar format'''
    
    song_words = song.split()
    artist_words = artist.split()
    var_song = ''
    for word in song_words:
        word = fix_word(word)
        var_song += word + '_'
    var_song = var_song.strip('_')
    var_artist = ''
    for word in artist_words:
        word = fix_word(word)
        var_artist += word + '_'
    var_artist = var_artist.strip('_')
        
    url = DOMAIN + var_artist[0] + '/' + var_artist + '/' + var_song
    if version > 1:
        url += '_ver' + str(version)
    url += '_crd.htm' 
    
    return url
    
def fix_word(word):
    '''remove superflouous characters and replace non-standard characters
    with their equivalent standard counterparts'''
    
    word = re.sub(r'[\'\",]', '', word)
    word = re.sub(r'&', 'and', word)
    return word
    
    

def get_plaintext(html):
    '''Returns the plaintext version of chords/lyrics from the given html
    source code of the ultimate guitar page'''
    
    soup = BeautifulSoup(html)     
    text = soup.get_text()

    start = text.find(STARTFLAG)
    start = text.find(STARTFLAG, start+1)
    start += len(STARTFLAG)
    end = text.find(ENDFLAG, start)
    return text[start:end].strip()


def find_highest_rating_version(song, artist):
    '''Given a song and artist, returns the version number for the highest
    rated version of the song on record'''
    
    search_startflag = get_url(song, artist, 1).lower()[:-4]
    search_partflag = search_startflag[:-9]
    
    html = str(get_search_html(song, artist))
    index = html.find(search_startflag)
    exists = index != -1
    
    if not exists:
        raise Exception(song + ':  No Chords Exist')
    else:
        version = 1
        count = 0
        rating_i = html.find('ratdig', index) + 8
        max_rating = int(html[rating_i:rating_i + 6].strip('</b> '))
        while index != -1 and check_next_listing_chords(html, index, search_partflag):
            count += 1
            index = html.find(search_partflag, index + 1)
            rating_i = html.find('ratdig', index) + 8
            new_rating = int(html[rating_i:rating_i + 6].strip('</b> '))
            if new_rating > max_rating:
                version += count
                count = 0
                max_rating = new_rating
        
        return version

    
    
def check_next_listing_chords(html, index, search_partflag):
    '''helper function for find_highest_rating_version, checks whether the
    next link in the html file is still for a valid chord file'''
    
    index = html.find(search_partflag, index + 1)
    index = html.find('ratdig', index)
    index = html.find('<td><strong>', index)
    return html[index + 12:index + 18] == 'chords'
    
    
def get_search_html(song, artist):
    '''returns the html source code for the search results page for the
    given song/artist (helper function for find_highest_rating_version'''
    
    url = SEARCH_URL
    for word in song.split():
        word = fix_word(word)
        url += word + '+'
    for word in artist.split():
        word = fix_word(word)
        url += word + '+'
    url = url[:-1]
    log = open(LOGFILE, 'a')
    log.write('searching ' + url + '\n')
    log.close()
    f = urllib.request.urlopen(url)
    s = f.read()
    f.close()
    return s


if __name__ == '__main__':    
    main()