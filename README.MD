# Competition Links

[Challenge Details](https://roboticvisionorg.github.io/carlie_docs/competitions/robovis2020_vision_challenge_details.html)

# Example Documentation
Below is an example of the documentation we are looking for as part of your submission. Due by 5.00pm (AEST) Tuesday 24th.

## Image Preprocessing Steps
The teach and repeat phase image preprocessing steps are:

1. Convert to grayscale
2. Normalize between 0 and 255.
3. Resolution reduction to 64x48 

<figure float="center" style="margin-bottom: 2em; display: block; text-align: center">
    <img src="figures/frame_000000.png" width="35%">
    <img src="figures/frame_000000_processed.png" width="35%">
    <caption><br>Example of original frame and the frame after preprocessing</caption>
</figure>

## Best Teach Frame Matching Algorithm
The core of our approach is based on normalised cross-correlation (NCC). We compare the preprocessed repeat image to a subset of the teach phase dataset. The subset consists of teach images within a +/- window of the previously best matched teach frame. Our algorithm is as follows:

1. Preprocess repeat image
2. We create an ensemble of 3 cropped repeat frames, which we spread horizontally over the image at 50% of the initial image width and the entire image height (see Figure below). We shall refer to these cropped portions as templates.
3. If the previous template matching score was below 0.5 (bad match), the teaching frame search window is +/- 5 images. Otherwise, it is +/- 3 images. Get the teach frame subset using this window size.
4. Compare the 3 cropped templates to each image in the teach frame subset using NCC
    - keep track of the current best teach match (maximum score).
5. The matched teach frame is the one with the maximum score. Now find the match within this image relative to only the center cropped template. This allows for a smoother control signal, once we have already found the correct frame with our ensemble template method.


<figure float="center" style="margin-bottom: 2em; display: block; text-align: center">
    <img src="figures/carlie.png" width="70%">
    <caption><br>Ensemble of three cropped repeat frames.</caption>
</figure>

The preprocessing steps are done on lines 209 to 213. The comparison is performed within a for loop, lines 220 to 233. The image is converted to grayscale, then normalized to a range of 0-255, then resized to 64x48.

## Estimating Current Pose of Carlie
After determining the best match teach frame for the current repeat image we estimate the position of Carlie. This is done by estimating the repeat image position relative to the best matched teach frame. As we utilise NCC, which outputs the position of the template within the compared image, we can utilise this to determine the y-offset (lateral deviation from the path) by using the horizontal pixel position of the template within the best matched teach image. We assume that the x-offset and yaw-offset are both zero. We multiply the horizontal pixel offset by a tuned parameter to estimate the y-offset in metres. This offset, plus 0 offsets for x and yaw, and then passed into the controller to determine command values. The algorithm is as follows:

1. Get the location of the template within the best matched teach frame (performed as part of the NCC process).
2. Determine the horizontal offset, in pixels, of this location. (horizontal offset) = (template width) / 2 - (x location of template in teach image)
3. Multiply the horizontal offset by a tuned parameter to estimate y-offset in metres.
4. Pass [0, y-offset, 0] to the controller to determine command values.

Remember, we only use the center cropped frame for generating the offset with the NCC teach match. 

Lines 242 to 248.

## Controller Tweaks
There were no tweaks/changes made to the controller algorithm (you do not need to state changes in parameter values).
