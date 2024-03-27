# Semi-automated edition of mp4 videos

this repository presents a number of scripts to help edit mp4 files.
In particular:

 - adding a colored rectangle on a video (to hide something in the frame for example)
 - detecting moments of silence in the video
 - splitting a big video in smaller parts, while cutting out some other parts


We use jupyter notebook scripts because their interactivity offers some opportunity for the user to monitor the process as they go.

## dependencies

 * A working python3 distribution with [jupyter notebook](https://jupyter.org/install#jupyter-notebook) installed.
 * [ffmpeg](https://ffmpeg.org/download.html)

And the following python libraries:

 * [numpy](https://numpy.org/install/)
 * [pandas](https://pandas.pydata.org/docs/getting_started/install.html#installing-from-pypi)
 * [matplotlib](https://matplotlib.org/stable/#install)
 * [imageio](https://pypi.org/project/imageio/)
 * [audiosegment](https://pypi.org/project/audiosegment/)




## usage

The notebooks starts with parameters pointing to files present in the `toy_data/` folder, to provide a simple example of usage.


### `add_black_rectangle_to_video.ipynb` 

It is used to place a rectangle on a video.

The script starts by loading a frame from the middle of the video and plots it so the user can 
adjust where to place a rectangle over it.

Once the position of the rectangle has been defined, the script generate and then run the appropriate ffmpeg command.

### `annotate_silence_stretches.ipynb`

This scripts analyse the audio track of a video and searches for stretches of silence which last 5 seconds or more (this duration is, of course, an adjustable parameter).

It then outputs these silences in a format that can be used with the following scripts to cut out theses silences from the video.


### `cut_videos.ipynb`

This script uses a csv file containing information on how one or more source video file should be split or merged into one or several destination files.

This csv is expected to have the following columns:
 - source : source mp4 file (eg, the raw recording )
 - start : a timepoint in the format hh:mm:ss
 - stop : a timepoint in the format hh:mm:ss
 - destination : to which resulting video this clip should go, or "OUT" to simply remove this clip out of the resulting videos

Each line corresponds to a clip from the <source> video, starting at <start> and ending at <stop>, and which should go to the <destination>, or be cutout from the result if destination is OUT.



Here is an example:

| source     | start    | stop     | destination   |
|------------|----------|----------|---------------|
| vid1.mp4   | 00:00:00 | 01:30:45 | part1         |
| vid1.mp4   | 01:31:00 | 02:02:00 | part2         |
| vid2.mp4   | 00:02:12 | 01:00:00 | part2         |
| vid2.mp4   | 01:01:00 | 01:12:00 | part3_overlap |
| vid2.mp4   | 01:10:00 | 01:15:00 | part3_overlap |
| vid1.mp4   | 00:10:00 | 00:25:30 | OUT           |
| vid1.mp4   | 01:29:00 | 01:32:00 | OUT           |
| vid2.mp4   | 00:00:00 | 00:01:00 | OUT           |
| vid1.mp4   | 01:28:00 | 01:30:00 | OUT           |


In this (complex) example, there is 2 source videos : `vid1.mp4` and `vid2.mp4`
and
we want to create 3 destination videos: part1, part2, part3_overlap.

The first line of the table specify that the clip from 00:00:00 to 01:30:45 from `vid1.mp4` should go to video `part1.mp4`.

Lines 2 and 3 of the table specify that a clip from `vid1.mp4` and a clip from `vid2.mp4` should both go to `part2.mp4`. 
In that case the order of the lines matter: `part2.mp4` will be made of, first the clip from `vid1.mp4`, then the clip from `vid2.mp4`.

The next two lines (lines 4 and 5) show a special case where 2 overlapping clips from the same source go the same destination : the first clip ends at 01:12:00 while the second one starts at 01:10:00.
In that case the overlapping segment will be repeated in the resulting video, so beware of these cases (the `cut_videos.ipynb` notebook issues a warning when it detects such a case).

Finally, the following lines are cutout lines. These can be anywhere and in any order in the table: they will be collected and applied in such a way that the clips specified there are absent from the resulting videos.






