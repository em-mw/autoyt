import requests
from os import getcwd, sep, name, mkdir, path
from moviepy.editor import VideoFileClip #for duration

#aka wget
def download(file_url: str, folder: str='media') -> str:
    #file_url = 'https://cdn.discordapp.com/attachments/934062419733536768/1130050636440940605/HG1ia2mcS4EVP5U0.mp4'
    #if folder: folder = sep + folder #adds the dir sep from `os` lib
    filename = file_url[file_url.rfind('/')+1:] #finds the name of the file
    
    # This sends a get request for the media file
    req = requests.get(file_url)

    with open(getcwd()+sep+folder+sep+filename, 'wb') as file_save:
        for chunk in req.iter_content(chunk_size=8192):
            if chunk:
                file_save.write(chunk)
    return getcwd()+sep+folder+sep+filename

'''
    #video_url = 'https://example.com/video.mp4'
    # Downloads a portion of the video file
    # returns the duration in (seconds)
    return VideoFileClip(file_url).duration #(seconds)
'''
if name == 'nt':
    duration = lambda file_url: VideoFileClip(file_url).duration
else:
    def duration(file_url: str) -> float:
        if not path.isdir("tmp"):
            mkdir("tmp")
        temp = VideoFileClip(download(file_url, "tmp")).duration
        #rmtree(getcwd()+sep+"tmp") #this does not work
        return temp


