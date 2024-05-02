#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import requests 


#from get-message.py:
# Set up your SQS queue URL and boto3 client
url = "https://sqs.us-east-1.amazonaws.com/440848399208/rqd3qmk"
sqs = boto3.client('sqs', region_name='us-east-1')  # Ensure the region is correct

#dont run while testing in main
def delete_message(handle):
    try:
        sqs.delete_message(
            QueueUrl=url,
            ReceiptHandle=handle
        )
        print("Message deleted")
    except ClientError as e:
        print(e.response['Error']['Message'])

#some adapted from get-message.py too
def getMessages():
    messages = [] #thinking list of dictionaries?
    while True:
        try:
            response = sqs.receive_message( #request syntax: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ReceiveMessage.html
                QueueUrl=url,
                AttributeNames=['All'],
                MaxNumberOfMessages=10,  #10 total messages instructions said not run a single call 10x (so no for loop)
                MessageAttributeNames=['All'],
                VisibilityTimeout=300 #The duration (in seconds) that the received messages are hidden from subsequent retrieve requests after being retrieved by a ReceiveMessage request.
            )
            if "Messages" not in response:
                break  #exit the loop if no messages are left
            #just dp response["Messages"] so no need to call it on each value
            for msg in response['Messages']: #same as if "Messages" in response: from the example I just want to iterate over each message in the queue as I have all 10 downloaded now
                order = int(msg['MessageAttributes']['order']['StringValue']) #cast as an int for reordering
                word = msg['MessageAttributes']['word']['StringValue'] 
                handle = msg['ReceiptHandle'] #just for tracking can comment out later

                #print each message's details as they are downloaded (comment out later too)
                #print(f"Order: {order}")
                #print(f"Word: {word}")
                #print(f"Handle: {handle}")

                messages.append({"order": order, "word": word, "handle": handle}) #dictionary of the message values
        except ClientError as e: #error exception handler
            print(e.response['Error']['Message'])
            break

    return messages

def putTogether(messages):
    #use sorted() function on list as we already have order value keyed into the dictionary (sorted: https://docs.python.org/3/howto/sorting.html)
    sorted_messages = sorted(messages, key=lambda x: x['order']) #trying to get the 'order' value so the key function is "lambda x: x['order']"  which is essentially x['order'] where x is every dictionary(message) in the list. 
    #join() function: https://www.w3schools.com/python/ref_string_join.asp uses ' ' as there is a space between each word
    sentence = ' '.join([msg['word'] for msg in sorted_messages]) #for loop here to iterate over sorted_messages where msg is the order valued obtained in the previous line. so it would be 1['word'] + 2['word']... 
    return sentence

def main():
    messages = getMessages()
    if messages:
        sentence = putTogether(messages)
        print("Final sentence:", sentence)
        for msg in messages:
            delete_message(msg['handle']) #use handle as an id to delete the messages

if __name__ == "__main__":
    main()

#note can only test every 5 minutes
"""
so the words are indexed from 0-9:
first test: I am missing words on index 3, 5, 8
second test: missing index 6 (maybe wait 15 minutes for queue to refresh)
third: got all 10
Order: 4
Word: they're
Handle: AQEBP7WMwRJtJ+Xxu/v+9Koa3k2CW5GHwpAkqK5kgXtaCPZl+/RnYWKPjpulofG7SbqCRRdVC4PJ5P/E8u1f3EsyLH5kaJ/gulWFS24BJrJQLPHyWzXP4IRSlsCnHJ5b4O6GFzjBhDVrqT7sK5l9YdlJh9rTZugc1munbOB2ribt5CLt0sbHZ0J4rMQ5kIVtEAbfE6WEslpWiVKTlAmEychh6PTXPIwCu1c82bR7t0/3XISeu3DgUCNebj1q9cR+5VIlm2Tm7Wub4u7jTwRf7j39iMCtoJ0REwI9AylPaS3v7I5XEjSppY0E7cvO7VevIVwSPNtZDTkN7Pevju93XXlsVTlSK07pzdSyRHahglOpcSRrUkq27IePM6KcOfDN3KO1
Order: 3
Word: what
Handle: AQEBvKwARqYnvUBhzjNJr73byDEclo5MaTY8R89NomhvLdXYP5768quShFvNIFlgM6YLPqWFOCUm1H894VPPRqaxfNvaI4D3SbRfDfGclIYyiXXqslrH08tPGfWnEeBIEuaqF7+rLF1zgVuvQe0eSKC0cesh4k565g8e5wlhnaxguQ7KCtASXj74A6mxEXQXIC/rkt+I+v1B8MYDs7GSxraUugNjeahNIsLe+wstO9XF2jaqt+rq5ibLvl5poa2ZomPYoNiRBztLBayt5TgU8gCk2eeG6E8gZjI7EuaALbGY0O/J/2cIqH3KG/iPkiNMbrLZyCkv1Jbxx4WabrMfqhNHX3PdXjf/mqTQCQmJ1HZ6Uv23bgaKJQ1Q0t1HfTYqrFSw
Order: 8
Word: need
Handle: AQEB5Fa0Emhh/qVAlI/0CUQqZE/Vmt3XZNIc0Va9I01HoEr1+Om+VkwP8CdAAL9iPVvGsVbWFAMuIdbUqStqaN9ALdEWNhIhT3v2Q+D0bu/B8zf+JQ5F+Zu1dQYZbvpu6RtLZD7bgruFhvBRm7vCRk9hLbARbT+JJRhlhGsklPgQE9o5o2nMDpf9SWlHUI0o0EPQ2JEb45jR9EpJgjTfdtD5uaPy9M1zhljhHacr+WphgTtRD70BQL8Qq2Zdlb6J+gG33lM95HufajI7wAoCp3kiufddTv9+qhemTUT0QmRW0DPpxmDY0yYjXC1fkd18QOWruxUGrrjpBxJTeYVms3zVlHELE8M8BHOFwKrnf6cyfxdqaxaLk2rocSlxQj/rn+b/
Order: 7
Word: don't
Handle: AQEBGe+5kw7rNm9Uyrdu0kPBYeDCZY6lhXSidiL9lnCi/wFBIg/nfsMHsvs5PMD/vwtZrJwolHTdj5nUVNizTSsHL6SskgjfkJc23GcsUwLhTNpa3L2yinfBdesOBJv9kpaBQ6+kT7eE0Xz+0wx+gZ8RjAQVxFHSQ/MTRc4UjZzaHiGecFE0qAU637i38iIHqWnjIFIbhUhp97V22s5uQ0xLZAP3HHyJmgyrU3FmH4fV/JwC2ITQ5IrtDNFNR7BcUBF8jQUonbr48dpYSCgy9E0mAeiwR3N2IQwjV7ziqFnt5i1WQjUQUMT5qEOw/CVghpM+X2j36j8ySxrLrmba9PYnXvbiFKmL8KiU4V2yidLioUxR2tMfi2hfShBef+BfWdeJ
Order: 6
Word: about
Handle: AQEBh+Zd09wAOyDAa5noi2KGN5yW9cgwUE10zWOVifJ66AAw2g04DshmPmxpuJM4Bm5/0sSWo86SV5FahceGbxIcKk8LGC7y/2Rd2mCKHvsrVmXjEOpX1xPAS2ssTbXJDFmJ8RZkblTg+HL7yPPv7Mi5OT+RwCrIUvajWtGMyH3QEsy1/8hXbGbmgDzyp4zIGLYN09YkVhskVfcT+bE7w25XM8hY4FKyjaT7+mVWxPzDNFB1Dn6GYRchB7q83LEy5+FrqSEJXsHXuFdYWoXF2+FS3r5+4zsKx3EEZuHcig17FYpxBMj13ZCGWzYEBb/MqhYnI/Qzv1Sz/YRE0nOj45Tc3uSl/SMDGRitdbxIct51YPRwvG+fR0kquf2jdLcyX0BM
Order: 0
Word: People
Handle: AQEBFdlIAs0DPbD1BI3RzDddltlA7ryu7YsNqUzVyURBRDHLZsfGmX6KTiY4sISFTQZIJ29NCYj2gvYRgRJudaCneHetYuXOEqZhsasyYtAK/zPB2EVWVnIuO8noi8pVKVFTSMY+9CrMdlrrifYom3owTgr6D5jIGFxXButCqKWQn5JRmiIgIluS/+yjdUtWRpvtJcHtipn1K9t6ngRCGuTKe0ghYgDSzqItynuZSEFB/x/yOb/ARnl+3AcccnrcQAniCGW7eoI1gIjKi+ZtGPVSY1H71PCKPQUSTUhMJAtBd+xPOSnJo/vj6gt228MDtqvambi3USj/atbRF0PYgjEx4TKxthfX8THXAP09e4xG3a5ew8dnhC1qSF5XFAxw4oum
Order: 2
Word: know
Handle: AQEBFBFU92PtErPTrYWc5FUlVwQlmV//2HaJz29fX3Iztkhe+72hxTrTU71gH5Ckb0EAZ1BMKiwmiX5zMiLoYVWYbxaoj1poz4G9m4IS65lgq50v6ettL4XDdeuNOgWwju4eFChktPeKUHMLi/wJsukt2h6j/AQb/pT+h+bsXYV173n7bu159ITbFyg87r9Yf9gi/6vwDukFhD6frF0K71F3BOcIgUhYzNAcNnl9nEF1BxEpIenl1WeL6SX+yI5FOqNeHlKTw2wbQ3YTFYV1bAqc3IHfFNPkD4zHvGpN9Eyy4Q+OogvUg4ZlxKVmDIZfVYFnNDqk6xkrxYjlH93/bPlf5TjRXcwwDjfhE8j1Jqpn69NPzV5wqv3NnAyCzWvgRbjV
Order: 5
Word: talking
Handle: AQEB9qyigJeirSh28WrneYGII5UYliowPtZPnPR/d8xUuUI4ojuFwKLB5d7WtfDY787OE80UwylDxxXGcLT7hTETunhing87JBH+zhbQGOZ9KyFWDZs5PpREKWKWm5BerhtNmL5YGNDkOE8TbCOdnfIrkgstwgn7tZvFbYJhjToHxa8hgA4nOowLECya5s9De+kzb1l79PjYad2WejSqF4eNHj01XWPpG0gW2RWtJkHy1IpZaWn2b0xp0sDksgDfwhybLnmh54tWl0/GoFT+RRsFH3g0rLAUqiDyBak1GxivJlSzxE48hbMzAhwpyaa/OZ+Okj4ewV/5FmcJnLTYK1lIcVw4bwlzKdpbxgZuifFtmbkYcej2G7ssLooaFOLgy50B
Order: 9
Word: PowerPoint.
Handle: AQEBcez/+xXYeV6uonsU+lZHm8L0+TfAMQU7Ew2Xm08MeXyDtzXqVPnp2wl4t6lw2rzKd5cTpLcU4fi4oKOnIBqPxCLPcScCBg90PQ5/FLpUZSWUqAYCZOtG4pDl1JqpxTVaqzc0YN2N9t96kCT/j4Win70hq7LcSM0STnM72EFhuSgGeU4zoMP5+EeNxZV7d3fhSwFj0hjJ2RCI8BOxf7z25NQ3uc6x6j6n8PZWSUVoDMk/naYGri7JeNOyGDC5TN/vn1tlMtBUokeNd0LrqEje0dPYtx21iizvWZF2FpH6ZzNyD/nmBaJfP12bD8TGe8ugNZZGKKvLixbZigoBYXforUiytYF6hBXPVzsWh2NNauPgdfpfI8uZQagxcAanHChc
Order: 1
Word: who
Handle: AQEB4Nvxv5Qd6obQtjAjKvNcElR2kITplhtBOafAq03SfufO2q+1gBcpe/QWYT5jDkSvgUcazLq3jZaYOM4KRLaaJF7ufYHGx6zUNEL3yx9ttWwVW5PnWJOV+4nT8VSLYltfbLwsbGkXSkSb0I0wcMjAxiv2xLYrhjRY4PXVybVV+lVatFk2jG5Q0QR881ed7Bx+fsWTRed7tFg+WVplekq/LdQSrZIRnFPGfHe5lagmi4o924qgFmLNRm3kGhy8jYPP/yEoRrkxTTZfym2DYJ9SgozTmuaOkTtaCrcCvkwScSNeVb2FHJYwE0/QLstMrGyRZmXbpc/iI4839Awhl1q68ALldP0RCWTCL2SG+4srOiinrbHeRE90OLBRHdHCTAHt
Final sentence: People who know what they're talking about don't need PowerPoint.
"""

