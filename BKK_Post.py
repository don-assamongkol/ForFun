import os 
import smtplib 
from email.message import EmailMessage

import requests
from bs4 import BeautifulSoup

import schedule
import time
import datetime
import calendar

#Set up Email
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")
read_pace = 250 #words/min

def read_time(article_soup):
    '''
    Helper function:
    return read time for a given article, where article_soup is a BS instance
    '''
    content = article_soup.find(class_="articl-content")

    total_words = 0
    for paragraph in content.find_all("p"):
        paragraph = str(paragraph)
        total_words += len(paragraph.split()) #get word count

    read_time = round(total_words / read_pace, 1)
    read_time = str(read_time)

    return read_time


def job():
    '''
    Put code in a function so can get a scheduler running it everyday
    '''

    #Set up Email object
    msg = EmailMessage()
    my_date = datetime.datetime.today()
    day = calendar.day_name[my_date.weekday()]
    msg["Subject"] = "Daily BKK Briefing" + " [" + day + "]"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ["don.assamongkol1@gmail.com", "rassamongkol@gmail.com"]
    mail_content = ""

    #Set up HTML Email Content 
    add_this = ""
    add_these_links = ""


    #Scrape news data from BKK Post
    page = requests.get("https://www.bangkokpost.com/business")
    soup = BeautifulSoup(page.content, "html.parser")

    #choose articles that have images- only good ones tend to get photos
    articles = soup.select("div[class='listnews-row']")
    
    #Iterate over the articles to pull out info we want
    for article in articles:
        time_published = article.find(class_="listnews-datetime").text
        title = article.find(class_="listnews-text").find("h3").text
        blurb = article.find(class_="listnews-text").find("p").text
        article_link = "https://www.bangkokpost.com" + article.find(class_=
                                                                    "listnews-img").a.get("href")
        
        
        #enter into the actual article webpage to get info on word count
        article_page = requests.get(article_link)
        article_soup = BeautifulSoup(article_page.content, "html.parser")
        read_time = read_time(article_soup)
    
        #Write in content for Plain Text Email
        mail_content += title
        read_time_str = f"Read Time: {read_time} mins."
        mail_content += read_time_str
        mail_content += blurb
        mail_content += "\n"
        mail_content += time_published
        mail_content += "\n"
        mail_content += article_link
        mail_content += "\n"
        mail_content += "\n"
        
        #Write in content for HTML email
        add_to_email = f"""
        <body> 
            <h3 style="color:Black;"> {title} </h3>
            <p> {blurb} </p>
            <h5> {read_time} min read | Published {time_published}.</h5>
        <body>
        """
        add_this += add_to_email
        add_these_links += f"<p> {article_link} </p>"
        

        time.sleep(2) #so we're not requesting too many articles at once
            
    
    #Set HTML content
    HTML_email = """\
    <!DOCTYPE html>
    <html>""" + add_this + "<br><br><br><br>" + add_these_links + """</html>"""
    
    #Set content for our email
    msg.set_content(mail_content)
    msg.add_alternative(HTML_email, subtype="html") 
    
    #Execute and send email
    port = 465 #For SSL
    with smtplib.SMTP_SSL("smtp.gmail.com", port) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) 

        smtp.send_message(msg)


# Run the script in computer background continuously
print("Program is running in the background!")
schedule.every().day.at("13:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(120) #wait one minute








