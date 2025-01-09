import argparse
import matplotlib.pyplot as plt
import numpy as np
import librosa
import sys
import os
import subprocess


def plot_waveform(original_filename, duration=5):
    """Plots the waveform of an audio file for a specified duration and allows interaction."""
    # Load audio file
    signal, sample_rate = librosa.load(original_filename, sr=None)

    # Calculate the number of samples to plot based on the desired duration
    max_samples = duration * sample_rate
    signal_to_plot = signal[:max_samples]  # Take only the first 'duration' seconds

    # Create time array for the x-axis
    time = np.linspace(0, len(signal_to_plot) / sample_rate, num=len(signal_to_plot))

    # Plotting
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(time, signal_to_plot)
    ax.set_title(f'Audio Waveform - First {duration} Seconds')
    ax.set_ylabel('Amplitude')
    ax.set_xlabel('Time (s)')
    ax.set_xlim(0, duration)  # Limit x-axis to the specified duration
    ax.grid()

    # Vertical line for cursor tracking
    vline = ax.axvline(x=0, color='r', linestyle='--')

    # Create a textbox for displaying custom text
    text_box = ax.text(0.1, 0.9, '', transform=ax.transAxes, fontsize=12, color='red')

    def on_mouse_move(event):
        """Update vertical line position based on mouse movement."""
        if event.inaxes == ax and event.xdata is not None:  # Check if xdata is valid
            vline.set_xdata([event.xdata])
            text_box.set_position((event.xdata + 0.01, 0.8))  # Move textbox slightly right of the line
            text_box.set_text(f'Click to trim at time {event.xdata:.2f} s')  # Custom text showing time
            fig.canvas.draw_idle()

    def on_click(event):
        """Callback function when the plot is clicked."""
        if event.inaxes == ax:
            clicked_time = event.xdata
            # print(f'Clicked at: {clicked_time:.2f} seconds')
            # Call your custom function here with clicked_time as argument
            onclick_callback(clicked_time)

            plt.close(fig)  # Close the plot window
            sys.exit()  # Terminate the program

    def trim_start(trim_seconds, input_file, output_file):
        """Trims a media file using FFmpeg."""
        # Construct the FFmpeg command
        command = [
            'ffmpeg',
            '-ss', str(trim_seconds),  # Start time for trimming
            '-i', input_file,  # Input file
            '-c', 'copy',  # Copy codec
            output_file  # Output file
        ]

        try:
            # Execute the command
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f'Error occurred: {e}')

    def rename(original):
        name, ext = os.path.splitext(original)
        renamed = f"{name}_old{ext}"
        try:
            os.rename(original, renamed)
            print(f'Successfully renamed "{original}" to "{renamed}".')
        except FileNotFoundError:
            print(f'Error: The file "{original}" does not exist.')
        except Exception as e:
            print(f'An error occurred: {e}')

        return renamed

    def onclick_callback(time):
        """Callback function to handle click events."""

        # Rename the file
        renamed_filename = rename(original_filename)
        trim_start(time, renamed_filename, original_filename)

    # Connect events to handlers
    fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
    fig.canvas.mpl_connect('button_press_event', on_click)

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
