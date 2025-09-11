# ToHeart PSE Tools
Tools for modifying the script, executable, and assets (planned) of ToHeart PSE (2003)

## Script
Progress: <1% done (0/1168)
Note that not all script files have actual text and the script files themselves are of varying length so this percentage is likely lower than what is actually done.

The ToHeart PSE script is stored as a series of .DAT files wrapped up in **scn.pak**.
The **extract** and **pack** utilities from [the 97 fantl project](https://github.com/waybeforenow/toheart-tools/tree/master/PSE) are used to access the individual .DAT files. Each .pak file has eight bytes to spell out "LEAFPACK" followed by a 233 byte rotating key.
The main utility for this is **dat_text_replacer**, which correctly formats text into the expected format:
### PSE script details
Each DAT file stores control commands and text data as one long stream, with all displayed text data stored as CP932 encoded full width (zenkaku) with the bytes flipped. For example, Ａ (full width A) with the hex code 0x8260 is stored as 0x6082. 
**dat_text_replacer** loads in a folder of original, unmodified DAT files, a mapper folder, and an output folder.
### Remake script details
The remake script is stored in Binary/Text/text.ttb.
It is full of a bunch of control characters at the beginning (presumably similar to the ones in PSE, just seperated out to support multiple languages), followed by the entire Japanese script, the entire English script, and the entire Chinese script. There is no easy way to map each languages lines 1-1 with each other as the text does not seem to be formatted in a fixed way. This is supported by the fact that you cannot switch language unless you are on the title screen.
### Mapper files
Mapper files are python files that are named the same as and correspond to each DAT file, with it consisting of an array of two element tuples. Here is an example from the beginning of the game:
'[
    ("ピピピピ、",
    "\*beep-beep-beep-beep\*      "),
    ("ピピピピ、",
    "\*beep-beep-beep-beep\*          "),
    ("ピピピピ…。",
    " \*beep-beep-beep-beep\*"),
]'
The text (both original and replacement) is converted from UTF-8 to SJIS at runtime, so editing is easy.
Note that there is currently no way to edit control commands, in order to preserve flags and not break the game, so all spacing is done manually.

## Executable
`ToHeart.exe` does not seem to serve much purpose other than to open `psth.exe` which contains the actual game logic, so currently that is the focus of modifications.
### Notes on text drawing
The game seems to have two seperate routines for text drawing. One of these is used by the menus/UI and a different one is used by the script files. Text for menus is stored directly in SJIS in the executable without byte flipping.
### Half Width hack
Through editing the text in the exe, it was discovered that the game contains an entire set of unused half width text characters and a corresponding text drawing routine. However, nowhere in the game (menus or scripts) is this used, as all menu latin text is full width and trying to use ASCII in the script files themselves will usually just cause the game to crash, as these are interpreted as control commands.
To solve this issue, I developed a patch that adds instructions right before the text drawing functions to subtract 0x1F from any full width characters, which results in them being passed to the half width drawing function instead, as well as replacing all references to the full width text spacing with half width spacing. The latter is slightly bugged as this now breaks half width text drawing (which worked fine), as there are 49 references to this address and I do not know which ones are for the menus and which ones are for the scripts. This should be able to be fixed eventually.
There is also an issue with the currently drawn line in the scripts having the bottom of the text cut off. It is fixed when the next line is drawn. Since the half width text was likely never tested in the scripts this is probably why this behavior occurs. It remains to be seen if this can be fixed, but the advantages in mapping full width to half width largely outweigh this small bug in my opinion, especially since much more text can fit on each page meaning there is a much lower chance of having to move lines to the following page. 
The script translation is playable without the modded exe, but it will be largely untested and may look off.

# UI Assets
UI Assets are stored in **sys.pak**. They consist of LFB formatted images, which are LZSS compressed bitmaps. [ExtractData](https://github.com/lioncash/ExtractData) can extract and convert these though the use of [Susie plugins](https://f.blicky.net/f.php?h=0Nj7TH-n), specifically AX_LF21.spi. The format can probably be reverse engineered into CLI tools through creating a fork of ExtractData that prints out format information.
Some of these images have text that needs to be translated, while others could have the option to be replaced by PS1 versions (which are slightly different)

# Soundtrack
The soundtrack is stored in **bgmfile.pak** in OGG format. While there is no real need for it to be replaced (it is virtually the same as the [original 1997 OST](https://www.youtube.com/watch?v=wqw_cCsPBFc&list=PLuw2FaP0vGRIYvrqM80Grh97FfO4HJC65&index=2)), a future enhancement would be the option to use the [sequenced PS1 OST](https://www.youtube.com/watch?v=B7Iy8FqO1G4&list=PLu5M2xP1uHMH3N46-O-PUkc5De6yLysEX&index=2) or even the [GBC demake OST](https://www.youtube.com/watch?v=m2PS5x_7Blc&list=PLHCCCJmgJm-bIRvwOOwnA8ei1haHtzMJB&index=2)
The majority of the songs are split into A and B tracks, with A being the intro that only plays once and B being the main bulk of the song that repeats.