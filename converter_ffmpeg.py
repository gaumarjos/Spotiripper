import subprocess


def convert_to_mp3(infile, outfile):
    try:
        subprocess.call(['ffmpeg',
                         '-channel_layout',
                         'stereo',
                         '-i', f'{infile}',
                         '-af',
                         'volume=4.0',
                         f'{outfile}'])
        '''
        '-loglevel',
        'quiet',
        '''
    except Exception as e:
        print('Error during conversion: {}'.format(e))
        return 0
    else:
        return 1
