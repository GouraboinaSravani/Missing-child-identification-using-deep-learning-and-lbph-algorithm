import smtplib


def send_mail(message):
    gmail_user = '187r1a05k4@gmail.com'
    gmail_password = 'Pinky21@'

    sent_from = gmail_user
    
    to = ['187r1a05k4@gmail.com', '187r1a05k4@gmail.com']

    subject = 'Missing Child Website'
   
    body = f"Subject:{subject}\n\n{message}"

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, body)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)



if __name__ == "__main__":
    send_main("Test Message")
        