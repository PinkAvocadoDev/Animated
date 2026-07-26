<img src="/data/icons/hicolor/scalable/apps/io.github.PinkAvocadoDev.Animated.svg" width=256 style="margin:auto"></img>
# Animated

### _Turn any MP4 into a GIF!_

Animated is a ``` GTK 4  ``` and ``` Libadwaita ``` application written in Python and packaged as a Flatpak. It lets you convert `.mp4` video files into `GIFs` with custom settings for duration, resolution, and frame rate.

By default, converted `GIFs` are saved to your Videos directory as `output.gif` (or to any custom path set in Preferences). Keep in mind that existing files with the same name will be overwritten.

## ⚠️ Performance Notice

Video encoding can be resource-heavy. Processing long videos or using high FPS and resolution settings will use a significant amount of RAM and CPU power. Keep an eye on your conversion settings if you're working on a lighter system!

## Technologies used

Animated is built with Python using the following main dependencies:

-  MoviePy – Handles the core video processing and conversion.

- FFmpeg – Backend driving MoviePy.

- NumPy – Used for frame manipulation.

- PyYAML – Manages  settings.

