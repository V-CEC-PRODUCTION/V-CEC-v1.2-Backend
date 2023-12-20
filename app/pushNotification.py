from moviepy.editor import VideoFileClip
from fractions import Fraction

def get_video_aspect_ratio(video_path):
    # Load the video clip
    clip = VideoFileClip(video_path)
    
    # Get the width and height
    width, height = clip.size
    
    # Calculate the aspect ratio
    aspect_ratio = Fraction(width, height)
    
    # Close the video clip
    clip.close()
    
    return aspect_ratio, width, height

def simplify_fraction(fraction):
    return fraction.numerator, fraction.denominator

# Replace 'your_video.mp4' with the path to your video file
video_path = 'video (2160p).mp4'
aspect_ratio, width, height = get_video_aspect_ratio(video_path)

# Simplify the aspect ratio
simplified_ratio = simplify_fraction(aspect_ratio)

print(f"The aspect ratio of the video is: {aspect_ratio}\nThe width is {width} and the height is {height}")
print(f"Simplified aspect ratio: {simplified_ratio[0]}:{simplified_ratio[1]}")
