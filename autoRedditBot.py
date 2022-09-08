import praw
from praw.models import MoreComments
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip, AudioFileClip, AudioFileClip
import random
import pyttsx3
import os
import concurrent.futures
from multiprocessing import Pool
import sys

#reddit creds
reddit = praw.Reddit(
    client_id="LpRsYO13zwASaresFtgzVQ",
    client_secret="cBFlbla5J78KxJuJ3yuUD8QOvlCeGw",
    user_agent="Mohiki",
)





def getPostCommentThread(submission):
        comments = []
        for top_level_comment in submission.comments:
            if isinstance(top_level_comment, MoreComments):
                continue
            comments.append([top_level_comment.body, top_level_comment.id])
        return([[submission.title + submission.selftext, submission.id], comments, "https://www.reddit.com" + submission.permalink])


def getPostComments(subreddit, searchType, timeFilter, searchNum):

    list = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        if searchType == 'hot':
            results = [executor.submit(getPostCommentThread, submission) for submission in reddit.subreddit(subreddit).hot(limit=searchNum)]
        elif searchType == 'new':
            results = [executor.submit(getPostCommentThread, submission) for submission in reddit.subreddit(subreddit).new(limit=searchNum)]
        elif searchType == 'top':
            results = [executor.submit(getPostCommentThread, submission) for submission in reddit.subreddit(subreddit).top(timeFilter, limit=searchNum)]
        else:
            pass
        for f in concurrent.futures.as_completed(results):
            list.append(f.result())
    return(list)



#list[post, [title, [comments, comment IDs], url]]
#comments list[post#][1][comment#][0 for comment, 1 for comment id]
#tite list[post#][title#][title/titleID]







#get pic of reddit
def getPicsComments(url, ids):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=options)
    driver.get(url)
    driver.find_element(By.CLASS_NAME, 'header-user-dropdown').click()
    try:
        driver.find_element(By.XPATH, "//*[contains(text(), 'Settings')]").click()
        driver.find_element(By.XPATH, "//*[contains(text(), 'Dark Mode')]").click()
    except:
        try:
            driver.find_element(By.XPATH, "//*[contains(text(), 'Dark Mode')]").click()
        except:
            pass
    try:
            driver.find_element(By.XPATH, "//*[contains(text(), 'Yes')]").click()
    except:
        pass
    time.sleep(2)
    try:
            driver.find_element(By.XPATH, "//*[contains(text(), 'Click to see nsfw')]").click()
    except:
        pass
    driver.find_element(By.XPATH, "//html").click()
    for id in ids:
        try:
            element = driver.find_element(By.ID, "t1_" + id)
            element.screenshot('shots/shot_'+id+".png")
        except:
            try:
                element = driver.find_element(By.CLASS_NAME, "t3_" + id)
                element.screenshot('shots/shot_'+id+".png")
            except:
                pass
    driver.quit()




def autoMakeVideo(post, list, vidNum):
    compL = []
    rNum = random.randint(1,vidNum)
    vid = VideoFileClip(f'video/{rNum}.mp4')
    start = random.randint(0,round(vid.duration)-60)
    vid = vid.subclip(start,start+60)
    audio = pyttsx3.init()
    audio.setProperty('rate', 200)
    audio.setProperty('volume', 1)
    audio.setProperty('voice', audio.getProperty('voices')[0].id)
    dur=0
    audio.save_to_file(list[post][0][0], 'audio/main-'+list[post][0][1]+'.mp3')
    audio.runAndWait()
    mainAudio = AudioFileClip('audio/main-'+list[post][0][1]+'.mp3')

    dur+=mainAudio.duration
    if dur > 60: 
        mainAudio.close()
        os.remove('audio/main-'+list[post][0][1]+'.mp3')
        return('post too long')
    comments=[]
    getList=[]
    getList.append(list[post][0][1])
    if dur <= 50:
        for x in range(16):
            try:
                audio.save_to_file(list[post][1][x][0],'audio/'+ list[post][1][x][1] + '.mp3')
                audio.runAndWait()
                Audio = AudioFileClip('audio/'+ list[post][1][x][1] + '.mp3')
                if Audio.duration + dur <= 60:
                    getList.append(list[post][1][x][1])
                    dur += Audio.duration
                    comments.append(x)
                else:
                    Audio.close()              
                    os.remove('audio/'+ list[post][1][x][1] + '.mp3')
            except:
                pass
    
    getPicsComments(list[post][2], getList)


    

    main = ImageClip('shots/shot_'+list[post][0][1]+'.png').set_position(("center", "center")).set_duration(mainAudio.duration).set_audio(mainAudio).resize(width=1080)
    compL.append(main)
    
    dur=0
    for comment in comments:
        Audio = AudioFileClip('audio/'+ list[post][1][comment][1] + '.mp3')
        compL.append(ImageClip('shots/shot_'+list[post][1][comment][1]+'.png').set_position(("center", "center")).set_duration(Audio.duration).set_audio(Audio).set_start(main.duration + dur).resize(width=1080))
        dur += Audio.duration
        
    
    compL.insert(0, vid.set_duration(main.duration+dur))
    vid=CompositeVideoClip(compL, size=(1080,1920))
    vid.write_videofile('uploads/'+list[post][0][1]+'.mp4', threads=10)
    
    return('Video ('+list[post][0][1]+'.mp4) has been made and uploaded')

"""
:subreddit: list of subreddit to scrape from|askreddit,tifu,TodayILearned,IamA,AmItheAsshole
:searchNum: number of posts to search for on each subreddit
:timeFilter: time to sort by, string, can be empty for some seach params|all, day, hour, month, week, year, all
:searchType: type of search|hot,new,top
"""
def run(subreddit, searchNum, timeFilter, searchType, vidNum):
    for r in subreddit:
        list = getPostComments(r, searchType, timeFilter, searchNum)
        PoolList = []
        for x in range(searchNum):     
            PoolList.append((x, list, vidNum))
        if __name__ == '__main__':
            with Pool(3) as p:
                print(p.starmap(autoMakeVideo, PoolList))

        #print(autoMakeVideo(x, list))
#subReddits = ['askreddit','tifu','TodayILearned','IamA','AmItheAsshole']

#run(list of subreddits, # of posts to get from each sub reddit, timeframs, searchFilter, #of background Vids)
run(['IamA'], 5, '', 'hot', 2)




