#!/usr/bin/env python
# coding: utf-8

# # YouTube transcripts
# 
# >[YouTube](https://www.youtube.com/) is an online video sharing and social media platform created by Google.
# 
# This notebook covers how to load documents from `YouTube transcripts`.

# In[ ]:


from langchain_community.document_loaders import YoutubeLoader


# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  youtube-transcript-api')


# In[ ]:


loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=QsYGlZkevEg", add_video_info=False
)


# In[ ]:


loader.load()


# ### Add video info

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  pytube')


# In[ ]:


loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=QsYGlZkevEg", add_video_info=True
)
loader.load()


# ### Add language preferences
# 
# Language param : It's a list of language codes in a descending priority, `en` by default.
# 
# translation param : It's a translate preference, you can translate available transcript to your preferred language.

# In[ ]:


loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=QsYGlZkevEg",
    add_video_info=True,
    language=["en", "id"],
    translation="en",
)
loader.load()


# ### Get transcripts as timestamped chunks
# 
# Get one or more `Document` objects, each containing a chunk of the video transcript.  The length of the chunks, in seconds, may be specified.  Each chunk's metadata includes a URL of the video on YouTube, which will start the video at the beginning of the specific chunk.
# 
# `transcript_format` param:  One of the `langchain_community.document_loaders.youtube.TranscriptFormat` values.  In this case, `TranscriptFormat.CHUNKS`.
# 
# `chunk_size_seconds` param:  An integer number of video seconds to be represented by each chunk of transcript data.  Default is 120 seconds.

# In[ ]:


from langchain_community.document_loaders.youtube import TranscriptFormat

loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=TKCMw0utiak",
    add_video_info=True,
    transcript_format=TranscriptFormat.CHUNKS,
    chunk_size_seconds=30,
)
print("\n\n".join(map(repr, loader.load())))


# ## YouTube loader from Google Cloud
# 
# ### Prerequisites
# 
# 1. Create a Google Cloud project or use an existing project
# 1. Enable the [Youtube Api](https://console.cloud.google.com/apis/enableflow?apiid=youtube.googleapis.com&project=sixth-grammar-344520)
# 1. [Authorize credentials for desktop app](https://developers.google.com/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application)
# 1. `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib youtube-transcript-api`
# 
# ### 🧑 Instructions for ingesting your Google Docs data
# By default, the `GoogleDriveLoader` expects the `credentials.json` file to be `~/.credentials/credentials.json`, but this is configurable using the `credentials_file` keyword argument. Same thing with `token.json`. Note that `token.json` will be created automatically the first time you use the loader.
# 
# `GoogleApiYoutubeLoader` can load from a list of Google Docs document ids or a folder id. You can obtain your folder and document id from the URL:
# Note depending on your set up, the `service_account_path` needs to be set up. See [here](https://developers.google.com/drive/api/v3/quickstart/python) for more details.

# In[ ]:


# Init the GoogleApiClient
from pathlib import Path

from langchain_community.document_loaders import GoogleApiClient, GoogleApiYoutubeLoader

google_api_client = GoogleApiClient(credentials_path=Path("your_path_creds.json"))


# Use a Channel
youtube_loader_channel = GoogleApiYoutubeLoader(
    google_api_client=google_api_client,
    channel_name="Reducible",
    captions_language="en",
)

# Use Youtube Ids

youtube_loader_ids = GoogleApiYoutubeLoader(
    google_api_client=google_api_client, video_ids=["TrdevFK_am4"], add_video_info=True
)

# returns a list of Documents
youtube_loader_channel.load()

