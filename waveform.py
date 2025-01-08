import argparse
import matplotlib.pyplot as plt
import numpy as np
import librosa


def plot_waveform(file_path, duration=5):
    """
    Plots the waveform of an audio file for a specified duration.

    Parameters:
        file_path (str): Path to the audio file.
        duration (int): Duration in seconds to plot.
    """
    # Load audio file
    signal, sample_rate = librosa.load(file_path, sr=None)

    # Calculate the number of samples to plot based on the desired duration
    max_samples = duration * sample_rate
    signal_to_plot = signal[:max_samples]  # Take only the first 'duration' seconds

    # Create time array for the x-axis
    time = np.linspace(0, len(signal_to_plot) / sample_rate, num=len(signal_to_plot))

    # Plotting
    plt.figure(figsize=(15, 5))
    plt.plot(time, signal_to_plot)
    plt.title(f'Audio Waveform - First {duration} Seconds')
    plt.ylabel('Amplitude')
    plt.xlabel('Time (s)')
    plt.xlim(0, duration)  # Limit x-axis to the specified duration
    plt.grid()
    plt.show()


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Show waveform of an MP3.")
    parser.add_argument('file', type=str, help='The mp3 file.')

    # Parse arguments
    args = parser.parse_args()

    # Organizing
    plot_waveform(args.file, 1)


if __name__ == "__main__":
    main()


