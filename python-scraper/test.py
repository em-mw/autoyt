import moviepy.editor as mp
import cv2

def check_video_time_dilation(video_path, tolerance=0.05):
    # Step 1: Get video metadata
    video = mp.VideoFileClip(video_path)
    reported_duration = video.duration

    # Step 2: Analyze frames
    frame_count = int(video.fps * reported_duration)
    if frame_count == 0:
        print("No frames found in the video.")
        return False, None

    frame_times = []
    cap = cv2.VideoCapture(video_path)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        frame_times.append(frame_time)

    cap.release()

    # Step 3: Check frame rate consistency
    frame_rate = (frame_times[-1] - frame_times[0]) / frame_count
    expected_frame_rate = 1 / video.fps

    # Step 4: Calculate time dilation if there are at least two frames
    dilation_factor = None
    if len(frame_times) >= 2:
        input(frame_times)
        input(reported_duration)
        dilation_factor = reported_duration / (frame_times[-1] - frame_times[0])

    # Step 5: Compare time dilation with tolerance
    is_dilated = abs(1 - dilation_factor) > tolerance if dilation_factor is not None else False

    return is_dilated, dilation_factor

def main():
    video_path = "C:\\Users\\annab\\OneDrive\\Desktop\\python_scraper\\media\\fnaf.mp4"
    is_dilated, dilation_factor = check_video_time_dilation(video_path)

    if is_dilated:
        print("Video time dilation detected.")
        print(f"Dilation factor: {dilation_factor:.3f}")
    else:
        print("Video appears to be normal.")

if __name__ == "__main__":
    main()




# if __name__ == '__main__':
#     x = """
# Hello, this is a message from the one and only mr pres

# I hereby the elf on the shelf declare that I will need the 
# compasodfjlasdflkjasdf asdfjlkasjdfljasldf asdfjlasdf
# asdflasdjfl asdfkjasldkfjlads flasd
# f
# asdfasdlfhlksadlfjlksajfdlkasd
# fsa
# dfadshfljsladfj lasdjf
# asdf
# asd

# --asdfsadf
# """

 #   print(x)


# from moviepy.editor import VideoFileClip, concatenate_videoclips

# x = VideoFileClip("C:\\Users\\annab\\OneDrive\\Desktop\\python_scraper\\media\\Connection_term.mov")









'''from pytube import YouTube

x = YouTube("https://www.youtube.com/watch?v=5qWyvwrd-1Y")

x.streams.get_highest_resolution().download()
'''





'''import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def my_function():
    logging.debug('This is a debug message')
    logging.info('This is an info message')
    logging.warning('This is a warning message')

my_function()
'''