NS is an automatic multi-source news summarizer

#Demo

http://ns.apps.xiamx.me/

![sample run](https://raw.github.com/xiamx/ns/master/samplerun.png)

# FAQ

## What is this?
An automatic news summary generator

## How does it work?
Using Bing cognitive service api, we get a list of urls of multiple news sources from a given keyword. We then extract the article text from the webpages. SumBasic (Nenkova and Vanderwende 2005) algorithm is used to generate a summary.

## The summary does not make sense, why?
NS can only summarize news events, the input keywords needs to be a news. In addition, try to be narrow and specific with your topic, it should give better results.

## There are bugs!
I had to implement SubBasic for my NLP course assignment, I then built this just for fun. Please feel free to submit pull requests!