## Shoutcast Server and Transcoder Python Utility
Useful for the following tasks:

* Start/Stop shoucast server and transcoder(s)
* Generate new playlists
* Reload playlists (useful for shuffling the playlist without turning on shuffle)
* Flush log files (clears console output)
* Next Song (can be passed a transcoder number if multiple are running)
* Shuffle enables shuffle on a specified transcoder
* Stop a specified transcoder
* Kill all instances of sc_serv and sc_trans
* List all processes for sc_serv and sc_trans

## Config file
/usr/local/etc/scroll.config
  
  [paths]
  
  srcPATH = /path/to/music/source/ (for generating new playlists)
  
  transPATH = /path/to/transcoder/
  
  plistPATH = /path/to/playlist/folder/
  
  [numbers]
  
  srmCOUNT = 5 (number of streams you want to run)

For srcPATH I use /home/music/source/out/ and then there are subfolders for each stream 1-5

## Usage

  $ python scroll.py -s (starts server and transcoders)
  
  $ python scroll.py -g 4 
  
  (checks /home/music/source/out/4/ for mp3's and adds them to stream 4 playlist)
  
  $ python scroll.py -h (show all available options)

TODO:

Config File, possibly shared between sc_serv, sc_trans and music-scraper
