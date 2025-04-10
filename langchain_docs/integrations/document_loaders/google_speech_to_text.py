#!/usr/bin/env python
# coding: utf-8

# # Google Speech-to-Text Audio Transcripts
# 
# The `SpeechToTextLoader` allows to transcribe audio files with the [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text) and loads the transcribed text into documents.
# 
# To use it, you should have the `google-cloud-speech` python package installed, and a Google Cloud project with the [Speech-to-Text API enabled](https://cloud.google.com/speech-to-text/v2/docs/transcribe-client-libraries#before_you_begin).
# 
# - [Bringing the power of large models to Google Cloud’s Speech API](https://cloud.google.com/blog/products/ai-machine-learning/bringing-power-large-models-google-clouds-speech-api)

# ## Installation & setup
# 
# First, you need to install the `google-cloud-speech` python package.
# 
# You can find more info about it on the [Speech-to-Text client libraries](https://cloud.google.com/speech-to-text/v2/docs/libraries) page.
# 
# Follow the [quickstart guide](https://cloud.google.com/speech-to-text/v2/docs/sync-recognize) in the Google Cloud documentation to create a project and enable the API.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-google-community[speech]')


# ## Example
# 
# The `SpeechToTextLoader` must include the `project_id` and `file_path` arguments. Audio files can be specified as a Google Cloud Storage URI (`gs://...`) or a local file path.
# 
# Only synchronous requests are supported by the loader, which has a [limit of 60 seconds or 10MB](https://cloud.google.com/speech-to-text/v2/docs/sync-recognize#:~:text=60%20seconds%20and/or%2010%20MB) per audio file.

# In[2]:


from langchain_google_community import SpeechToTextLoader

project_id = "<PROJECT_ID>"
file_path = "gs://cloud-samples-data/speech/audio.flac"
# or a local file path: file_path = "./audio.wav"

loader = SpeechToTextLoader(project_id=project_id, file_path=file_path)

docs = loader.load()


# Note: Calling `loader.load()` blocks until the transcription is finished.

# The transcribed text is available in the `page_content`:

# In[ ]:


docs[0].page_content


# ```
# "How old is the Brooklyn Bridge?"
# ```

# The `metadata` contains the full JSON response with more meta information:

# In[ ]:


docs[0].metadata


# ```json
# {
#   'language_code': 'en-US',
#   'result_end_offset': datetime.timedelta(seconds=1)
# }
# ```

# ## Recognition Config
# 
# You can specify the `config` argument to use different speech recognition models and enable specific features.
# 
# Refer to the [Speech-to-Text recognizers documentation](https://cloud.google.com/speech-to-text/v2/docs/recognizers) and the [`RecognizeRequest`](https://cloud.google.com/python/docs/reference/speech/latest/google.cloud.speech_v2.types.RecognizeRequest) API reference for information on how to set a custom configuation.
# 
# If you don't specify a `config`, the following options will be selected automatically:
# 
# - Model: [Chirp Universal Speech Model](https://cloud.google.com/speech-to-text/v2/docs/chirp-model)
# - Language: `en-US`
# - Audio Encoding: Automatically Detected
# - Automatic Punctuation: Enabled

# In[6]:


from google.cloud.speech_v2 import (
    AutoDetectDecodingConfig,
    RecognitionConfig,
    RecognitionFeatures,
)
from langchain_google_community import SpeechToTextLoader

project_id = "<PROJECT_ID>"
location = "global"
recognizer_id = "<RECOGNIZER_ID>"
file_path = "./audio.wav"

config = RecognitionConfig(
    auto_decoding_config=AutoDetectDecodingConfig(),
    language_codes=["en-US"],
    model="long",
    features=RecognitionFeatures(
        enable_automatic_punctuation=False,
        profanity_filter=True,
        enable_spoken_punctuation=True,
        enable_spoken_emojis=True,
    ),
)

loader = SpeechToTextLoader(
    project_id=project_id,
    location=location,
    recognizer_id=recognizer_id,
    file_path=file_path,
    config=config,
)

