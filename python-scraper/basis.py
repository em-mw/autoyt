import requests, json

def retrieve_messages(channel_id: str):
    headers = {
        'authorization': 'NzQ0OTY1NzM2MjU4MjA3ODk2.GCcZAP.1cpxjlXAP7z5dcV7phQ_Ga3KrZuSREC_SGZfhU'
    }

    r = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers)
    jsonn = json.loads(r.text)
    for value in jsonn[::-1]:
        content = value.get('content', '')  # Retrieve text content (if available)
        attachments = value.get('attachments', [])  # Retrieve image attachments (if available)
        print(content, end='')
        
        # Iterate over image attachments and print their URLs
        for attachment in attachments:
            attachment_type = attachment.get('content_type', '').lower()
            attachment_url = attachment.get('url')
            #print('Image URL:', attachment_url)
            if 'image' in attachment_type:
                print('Image URL:', attachment_url, end='')
            elif 'video' in attachment_type:
                print('Video URL:', attachment_url, end='')
        #note the \n might not be accurate if the user has multiple attachments in his post
        print('\n')

#retrieve_messages('1130423540630433792')
retrieve_messages('934062419733536768')

'''
Notes:
## For the r/Memes Discord server
- do not use if the value from jsonn has 'referenced_message'
- do not use video if it is more than 30 seconds long
- you can use images if there is text above or below it and respects the previous rules
- if there is an image that is a reply to something, include the image that was replied to and then the new image

'''