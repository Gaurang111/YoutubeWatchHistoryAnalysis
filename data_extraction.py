import os
import pickle
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
credentials = None


# if os.path.exists('token.pickle'):
#     os.remove('token.pickle')
    
# token.pickle stores the user's credentials from previously successful logins
if os.path.exists('token.pickle'):
    print('Loading Credentials From File...')
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

# If there are no valid credentials available, then either refresh the token or log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing Access Token...')
        credentials.refresh(Request())
    else:
        print('Fetching New Tokens...')
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=[
                'https://www.googleapis.com/auth/youtube.readonly'
            ]
        )

        flow.run_local_server(port=8080, prompt='consent',
                              authorization_prompt_message='')
        credentials = flow.credentials

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)

youtube = build('youtube', 'v3', credentials=credentials)




df_dict = {'VideoId':[], 'PublishedAt':[], 'ChannelId':[], 'Title':[], 'Describtion':[], 'Thumbnail':[], 'ChannelTitle':[], 'Tags':[], 'CategoryId':[]}

# Retrieve the watch history
request = youtube.activities().list(
    part="contentDetails",
    mine=True,
    maxResults=500,  # Adjust as needed
)
response = request.execute()

# Print the video IDs from the watch history
for activity in response["items"]:
    print(activity)
    try:
        video_id = activity['contentDetails']['playlistItem']['resourceId']['videoId']
    except KeyError as e:
        video_id = activity['contentDetails']['upload']['videoId']

    video_request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    video_response = video_request.execute()
    print(video_response)

    video_info = video_response["items"][0]["snippet"]

    # Populate df_dict
    df_dict['VideoId'].append(video_id)
    df_dict['PublishedAt'].append(video_info['publishedAt'])
    df_dict['ChannelId'].append(video_info['channelId'])
    df_dict['Title'].append(video_info['title'])
    df_dict['Describtion'].append(video_info['description'])
    df_dict['Thumbnail'].append(video_info['thumbnails']['maxres']['url'] if 'maxres' in video_info['thumbnails'] else '')
    df_dict['ChannelTitle'].append(video_info['channelTitle'])
    df_dict['Tags'].append(video_info.get('tags', []))
    df_dict['CategoryId'].append(video_info['categoryId'])



df = pd.DataFrame(df_dict)
print(df.to_string())

df.to_csv("Mydata.csv")
