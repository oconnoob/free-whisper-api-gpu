# Transcripts

Each folder contains a JSON file of data for a transcription on that type of hardware, one file for each model size. This data has been compiled into a `.csv` in the folder as well, and a couple graphs that display it. Additionally, there is a graph on the cost to run Whisper, taken from [this article](https://www.assemblyai.com/blog/how-to-run-openais-whisper-speech-recognition-model/).

Note that these numbers are a reflection of the **default configuration** of using Whisper. That means that the CPU used **FP32 precision for CPU** and **FP16 precision for GPUs**. Additionally, each value represents a single inference call and is not an average or aggregate in any way of multiple calls, which may account for the discrepancy in GPU performance for the `tiny` model.