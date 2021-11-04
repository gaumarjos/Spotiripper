from pydub import AudioSegment


def convert_to_mp3(infile, outfile, gaindb=0):
    try:
        # Remove initial noise and convert
        # For some reason the initial 160ms of the recording are sometimes a very high volume "white" noise
        sound = AudioSegment.from_file(infile, format="wav")
        # start_trim = detect_leading_silence(sound)
        # end_trim = detect_leading_silence(sound.reverse())
        start_trim = 200
        trimmed_sound = sound[start_trim:]
        output = AudioSegment.empty()
        output = trimmed_sound
        output.apply_gain(gaindb)
        output.export(outfile, format="mp3")
    except Exception as e:
        print('Error during conversion: {}'.format(e))
        return 0
    else:
        return 1


# convert_to_mp3("dev/pydub_fallisce2.wav", "dev/pydub_fallisce2.mp3")
