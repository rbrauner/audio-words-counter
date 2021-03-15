import pyaudio
import speech_recognition as sr


class OutputSoruce(sr.AudioSource):
    def __init__(self, device_index=None, sample_rate=None, chunk_size=1024):
        assert device_index is None or isinstance(
            device_index, int), "Device index must be None or an integer"
        assert sample_rate is None or (isinstance(
            sample_rate, int) and sample_rate > 0), "Sample rate must be None or a positive integer"
        assert isinstance(
            chunk_size, int) and chunk_size > 0, "Chunk size must be a positive integer"

        audio = pyaudio.PyAudio()
        try:
            count = audio.get_device_count()
            if device_index is not None:  # ensure device index is in range
                assert 0 <= device_index < count, "Device index out of range ({} devices available; device index should be between 0 and {} inclusive)".format(
                    count, count - 1)
            if sample_rate is None:  # automatically set the sample rate to the hardware's default sample rate if not specified
                device_info = audio.get_device_info_by_index(
                    device_index) if device_index is not None else audio.get_default_input_device_info()
                assert isinstance(device_info.get("defaultSampleRate"), (float, int)
                                  ) and device_info["defaultSampleRate"] > 0, "Invalid device info returned from PyAudio: {}".format(device_info)
                sample_rate = int(device_info["defaultSampleRate"])
        finally:
            audio.terminate()

        self.device_index = device_index
        self.format = pyaudio.paInt16  # 16-bit int sampling
        self.SAMPLE_WIDTH = pyaudio.get_sample_size(
            self.format)  # size of each sample
        self.SAMPLE_RATE = sample_rate  # sampling rate in Hertz
        self.CHUNK = chunk_size  # number of frames stored in each buffer

        self.audio = None
        self.stream = None

    def __enter__(self):
        assert self.stream is None, "This audio source is already inside a context manager"
        self.audio = pyaudio.PyAudio()
        try:
            # chunk = 1024  # Record in chunks of 1024 samples
            # sample_format = pyaudio.paInt16  # 16 bits per sample
            # channels = 2
            # fs = 44100  # Record at 44100 samples per second
            # p = pyaudio.PyAudio()
            # stream = p.open(format=sample_format,
            #                 channels=channels,
            #                 rate=fs,
            #                 frames_per_buffer=chunk,
            #                 input=True)

            self.stream = OutputSoruce.OutputSourceStream(
                self.audio.open(
                    format=self.format, channels=1, rate=self.SAMPLE_RATE, frames_per_buffer=self.CHUNK, input=True,
                )
            )
        except Exception:
            self.audio.terminate()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.stream.close()
        finally:
            self.stream = None
            self.audio.terminate()

    class OutputSourceStream(object):
        def __init__(self, pyaudio_stream):
            self.pyaudio_stream = pyaudio_stream

        def read(self, size):
            return self.pyaudio_stream.read(size, exception_on_overflow=False)

        def close(self):
            try:
                # sometimes, if the stream isn't stopped, closing the stream throws an exception
                if not self.pyaudio_stream.is_stopped():
                    self.pyaudio_stream.stop_stream()
            finally:
                self.pyaudio_stream.close()


def main():
    r = sr.Recognizer()
    stream = OutputSoruce()
    # stream = sr.AudioFile("test.wav")
    with stream as source:
        print(1)
        audio = r.record(source, duration=5)
        print(2)
        sentence = r.recognize_google(audio, language="pl-PL")
        print(3)
        print(sentence)


if __name__ == "__main__":
    main()
