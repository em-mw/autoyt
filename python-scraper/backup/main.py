import requests, json, downloader, logging
from os import getcwd, sep
import moviepy.editor
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip

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
    for value in jsonn[::-1]:
        content = value.get('content', '')  # Retrieve text content/text (if available)
        attachments = value.get('attachments', [])  # Retrieve image/video attachments (if available)

        #print(content, end='\n') #prints text
        
        # Iterate over image attachments and print their URLs
        
        for attachment in attachments:
            attachment_type = attachment.get('content_type', '').lower()
            attachment_url = attachment.get('url')
            #print('Image URL:', attachment_url)
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

                logging.debug("downloaded") #debug
                total_duration += downloader.duration(attachment_url)
                logging.debug(f"length (in seconds): {total_duration}") #debug
    
    #video_metadata.append({'total_duration': total_duration})
    return video_metadata
        
        #print('\n')

# DO NOT EDIT VIDEO METADATA, MAKE A COPY IF YOU WANT TO DO SO
def video_gen(video_metadata: list, BG_COLOR: tuple): #this is focused on only videos
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
        videos[video] = videos[video].set_start(dur)
        dur += videos[video].duration
        videos[video] = videos[video].set_end(dur)
        #adding the video and transition into the final list
        combined_videos.append(videos[video])

        transition = transition.set_start(dur)
        dur += transition.duration
        transition = transition.set_end(dur)

        combined_videos.append(transition)
    
    combined_videos.insert(0, ImageClip(f"{getcwd()}{sep}effects{sep}background.png").set_duration(dur))
    final_clip = CompositeVideoClip(combined_videos, use_bgclip=True, size=(1920, 1080))
    final_clip.write_videofile(f"{getcwd()}{sep}outputs{sep}first.mp4")
    final_clip.close()
def yt_upload():
    pass
#Channel IDs stored in a dictionary
if __name__ == '__main__':
    SERVERS = {
        'Memes': '934062419733536768',
        'Idle_Miner_Shitpost': '744805633710358548',
        'Rifty_memebistro': '831711630491385887'
        }

    video_gen(retrieve_media('NzQ0OTY1NzM2MjU4MjA3ODk2.GCcZAP.1cpxjlXAP7z5dcV7phQ_Ga3KrZuSREC_SGZfhU', SERVERS['Memes'], 20), (255, 255, 255))
'''
Notes:
## For the r/Memes Discord server
- do not use if the value from jsonn has 'referenced_message'
- do not use video if it is more than 30 seconds long
- you can use images if there is text above or below it and respects the previous rules
- if there is an image that is a reply to something, include the image that was replied to and then the new image

'''