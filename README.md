# Automatic-Short-Form-Reddit-Bot
This program will automatically create one of those robot voiced reddit bots with minecraft gameplay in the background.

# Setup
Put backgrounda video in the video folder, name them 1, 2, 3 etc.

input reddit auth tokens on lines 16-20. You can get them here https://www.reddit.com/prefs/apps/

Make sure you have a correct version of chrome driver

# Videos
The videos you input can be of any length, it will take a random 1 min clip from it and make it into a shorts video. Make sure it is of a 16:9 aspect ratio as it creates videos for formats such as tik-toks and youtube shorts.

# Usage
Use run() function to create videos



:subreddit: list of subreddit to scrape from|askreddit,tifu,TodayILearned,IamA,AmItheAsshole

:searchNum: number of posts to search for on each subreddit

:timeFilter: time to sort by, string, can be empty for some seach params|all, day, hour, month, week, year, all

:searchType: type of search|hot,new,top

:vidNum: # of videos in video folder to choose from

run(subreddit, searchNum, timeFilter, searchType, vidNum)
