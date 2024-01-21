import requests, json, downloader, logging
from os import getcwd, sep, remove, listdir
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
from random import randint
from argparse import ArgumentParser

import upload_video

def retrieve_media(AUTH_ID: str, channel_id: str, LIMIT: int = 100) -> list:
    #For Debug
    logging.basicConfig(level=logging.DEBUG)
    ##################################################
    
    MAX_DURATION = 30.9 #the .9 acts as a bufferzone
    headers = {'authorization': AUTH_ID}
    
    #the limit here is 100 (max allowed by discord i think), 
    #if you want to load the previous messages you will have to do:
    #https://discord.com/api/v9/channels/{channel_id}/messages?limit=100&before={message_id}
    r = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={LIMIT}', headers=headers)
    jsonn = json.loads(r.text)
    video_metadata = []
    
    total_duration = 0
    if not jsonn:exit("No media found")
    for value in jsonn[::-1]:
        content = value.get('content', '')  # Retrieve text content/text (if available)
        attachments = value.get('attachments', [])  # Retrieve image/video attachments (if available)

        #print(content, end='\n') #prints text
        
        # Iterate over image attachments and print their URLs
        
        for attachment in attachments:
            attachment_type = attachment.get('content_type', '').lower()
            attachment_url = attachment.get('url')
            #print('Image URL:', attachment_url)
            try:downloader.duration(attachment_url)
            except:continue
            if ('video' in attachment_type) and downloader.duration(attachment_url) <= MAX_DURATION:
                print('Video URL:', attachment_url, end='\n')
                
                '''
                - adds the header metadata along with some other custom metadata
                - it also deletes multiple attachments and just puts them into copies
                of the samething except with one attachment
                - the .update method houses the custom entries 
                - downloader.download() downloads the media
                '''
                metadata = value.copy()
                del metadata['attachments']
                metadata.update(
                    {
                        'attachments': attachment,
                        'duration': downloader.duration(attachment_url), 
                        'local_directory': downloader.download(attachment_url)
                    }
                )
                video_metadata.append(metadata)

                logging.debug("downloading...") #debug
                try:total_duration += downloader.duration(attachment_url)
                except:
                    remove(f"{getcwd()}{sep}media{sep}{value['filename']}") #remove the file in the media dir
                    video_metadata.pop(len(video_metadata)-1)
                logging.debug(f"length (in seconds): {total_duration}") #debug
    
    #video_metadata.append({'total_duration': total_duration})
    return video_metadata
        
        #print('\n')

# DO NOT EDIT VIDEO METADATA, MAKE A COPY IF YOU WANT TO DO SO
def video_gen(video_metadata: list): #this is focused on only videos
    try:
        with open(getcwd()+sep+"outputs"+sep+"metadata1.txt", "r") as video_metadata_file:video_metadata = json.load(video_metadata_file)
    except:
        try:
            with open(getcwd()+sep+"outputs"+sep+"metadata2.txt", "r") as video_metadata_file:video_metadata = json.load(video_metadata_file)
        except:pass
    logging.debug(video_metadata) #debug
    videos = [VideoFileClip(i['local_directory']) for i in video_metadata]
    combined_videos = []
    transition = VideoFileClip(f"{getcwd()}{sep}effects{sep}transition.mp4").resize((1920, 1080))
    dur = 0
    for video in range(len(videos)):
        #resizing
        videos[video] = videos[video].resize(min(1920 / videos[video].w, 1080 / videos[video].h))
        #b/c I am lazy and don't want to double check
        if videos[video].h > 1080: videos[video] = videos[video].resize(height=1080)
        if videos[video].w > 1920: videos[video] = videos[video].resize(width=1920)

        #centering the video
        videos[video] = videos[video].set_position('center', 'center')
        
        #setting the duration for compositing
        videos[video] = videos[video].set_start(dur)
        video_metadata[video].update({'start': dur, 'duration': videos[video].duration}) #updates in video_metadata
        dur += videos[video].duration
        videos[video] = videos[video].set_end(dur)
        video_metadata[video].update({'end': dur}) #updates in video_metadata
        
        #adding the video and transition into the final list
        combined_videos.append(videos[video])

        #same thing but for the transition and without video_metadata updates
        transition = transition.set_start(dur)
        dur += transition.duration
        transition = transition.set_end(dur)

        combined_videos.append(transition)
    
    #combined_videos.insert(0, ImageClip(f"{getcwd()}{sep}effects{sep}background.png").set_duration(dur)) #adds image in the beginning as the background
    #final_clip = CompositeVideoClip(combined_videos, use_bgclip=True, size=(1920, 1080)) #uncomment to use the image as the background
    final_clip = CompositeVideoClip(combined_videos, bg_color=(0, 0, 0), size=(1920, 1080))
    final_clip.write_videofile(f"{getcwd()}{sep}outputs{sep}final.mp4")
    final_clip.close()

def short_gen(video_metadata: list):
    try:
        with open(getcwd()+sep+"outputs"+sep+"metadata1.txt", "r") as video_metadata_file:video_metadata = json.load(video_metadata_file)
    except:
        try:
            with open(getcwd()+sep+"outputs"+sep+"metadata2.txt", "r") as video_metadata_file:video_metadata = json.load(video_metadata_file)
        except:pass
    video_metadata = video_metadata.copy()
    print(video_metadata)
    logging.debug(video_metadata) #debug
    videos = [VideoFileClip(i['local_directory']) for i in video_metadata]
    transition = VideoFileClip(f"{getcwd()}{sep}effects{sep}transition.mp4").resize((1080, 1920))
    trans_dur = transition.duration
    #filters out the videos that are longer than a min
    map_dur = {}
    video = 0
    while video < len(videos):
        if videos[video].duration > 60:
            video_metadata.pop(video)
            videos.pop(video)
            continue
        map_dur.update({videos[video].duration: video})
        video += 1

    for video in range(len(videos)):
        #resizing
        videos[video] = videos[video].resize(min(1920 / videos[video].h, 1080 / videos[video].w))
        #b/c I am lazy and don't want to double check
        if videos[video].w > 1080: videos[video] = videos[video].resize(width=1080)
        if videos[video].h > 1920: videos[video] = videos[video].resize(height=1920)

        #centering the video
        videos[video] = videos[video].set_position('center', 'center')
        
    #combines the videos into multiple videos 
    combined_videos = [[]]
    total_dur = 0
    dur = 0
    comb = 0
    while len(videos) > 0:
        combined_videos[comb].append(videos[0].set_start(dur).set_end(videos[0].duration+dur))
        dur += videos[0].duration
        total_dur += dur
        videos.pop(0)
        if len(videos) <= 0:break
        if dur+trans_dur+videos[0].duration > 60:
            comb += 1
            dur = 0
            #this sets the maximum shorts that you want
            if comb < 5:combined_videos.append([])
            else:break
        else:
            combined_videos[comb].append(transition.set_start(dur).set_end(trans_dur+dur))
            dur += trans_dur
            total_dur += dur
        
    logging.warning(f"file_clip:{combined_videos}")
    for clip in range(len(combined_videos)):
        final_clip = CompositeVideoClip(combined_videos[clip], bg_color=(0, 0, 0), size=(1080, 1920))
        final_clip.write_videofile(f"{getcwd()}{sep}shorts{sep}final{clip+1}.mp4")
        final_clip.close()

def description(VIDEO_METADATA: list, MESSAGE: str=""):
    description ="\nEnjoy the memes! :) \n\nlike and subscribe to @BigDog_Memes for more funny vids!\n\n"
    if MESSAGE: description += MESSAGE
    description += (
'''Copyright Disclaimer, Under Section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes such as criticism, comment, news reporting, teaching, scholarship, and research. Fair use is a use permitted by copyright statute that might otherwise be infringing. Non-profit, educational or personal use tips the balance in favor of fair use.''')
    
    description += MESSAGE + "\n\nCredit (people from discord):\n"
    for video in VIDEO_METADATA:
        minutes = int(video.get("start", 0))//60
        seconds = "0" + str(int(video.get("start", 0))%60) if len(str(int(video.get("start", 0))%60)) < 2 else str(int(video.get("start", 0))%60)
        description += f'{minutes}:{seconds} - @{video.get("author").get("username", "")}\n'
    
    description += "\n\n\n"
    description += "#memes #dankmemes #compilation #funny #funnyvideos"
    with open(getcwd()+sep+"outputs"+sep+"description.txt", "w") as description_file: description_file.write(description)
    return description

def title() -> str:
    titles = [
    "😂 Best Memes of All Time! 😂",
    "🔥 Hilarious Meme Compilation! 🔥",
    "😆 Ultimate Funny Memes! 😆",
    "🤣 Laugh Challenge: Memes Edition! 🤣",
    "😄 Top Memes that Went Viral! 😄",
    "😅 Meme Madness: Try Not to Laugh! 😅",
    "🤩 The Funniest Internet Memes! 🤩",
    "😎 Memes that Will Brighten Your Day! 😎",
    "😜 Non-Stop Meme Fest! 😜",
    "😝 You Can't Watch Without Laughing! 😝",
    "🤪 Craziest Memes on the Internet! 🤪",
    "😁 Get Ready to ROFL! 😁",
    "🤭 Memes that Sum Up Life! 🤭",
    "😏 Memes Only Legends Will Understand! 😏",
    "😇 Wholesome Memes to Make You Smile! 😇",
    "🥳 Celebrating with Memes! 🥳",
    "😂 Memes for a Good Time! 😂",
    "😆 When Memes Are Life! 😆",
    "🤣 Hilarious Memes: Can't Stop Laughing! 🤣",
]
    return titles[randint(0, len(titles)-1)]

#Channel IDs stored in a dictionary
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--noauth_local_webserver", action="store_true")
    noauth_local_webserver = parser.parse_args().noauth_local_webserver
    noauth_local_webserver = True
    SERVERS = {
        'Memes': '934062419733536768',
        'Idle_Miner_Shitpost': '744805633710358548'
        }
    video_metadata = []
    for server in SERVERS.values():
        for i in retrieve_media('NzQ0OTY1NzM2MjU4MjA3ODk2.GCcZAP.1cpxjlXAP7z5dcV7phQ_Ga3KrZuSREC_SGZfhU', server):
            video_metadata.append(i)
    with open(getcwd()+sep+"outputs"+sep+"metadata1.txt", "w") as video_metadata_file: json.dump(video_metadata, video_metadata_file)
    short_gen(video_metadata)
    video_gen(video_metadata) #changes video metadata
    with open(getcwd()+sep+"outputs"+sep+"metadata2.txt", "w") as video_metadata_file: json.dump(video_metadata, video_metadata_file)
    print(description(video_metadata))
    upload_video.start(f"{getcwd()}{sep}outputs{sep}final.mp4", noauth_local_webserver, description=description(video_metadata), title=title(), privacyStatus="public")
    for short in listdir(f"{getcwd()}{sep}shorts"):
        upload_video.start(f"{getcwd()}{sep}shorts{sep}{short}", noauth_local_webserver, title=title(), privacyStatus="public")
'''
Notes:
## For the r/Memes Discord server
- do not use if the value from jsonn has 'referenced_message'
- do not use video if it is more than 30 seconds long
- you can use images if there is text above or below it and respects the previous rules
- if there is an image that is a reply to something, include the image that was replied to and then the new image

'''
