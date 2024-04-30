#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError

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
                VisibilityTimeout=200 #The duration (in seconds) that the received messages are hidden from subsequent retrieve requests after being retrieved by a ReceiveMessage request.
            )
            if "Messages" not in response:
                break  #exit the loop if no messages are left
            #just dp response["Messages"] so no need to call it on each value
            for msg in response['Messages']: #same as if "Messages" in response: from the example I just want to iterate over each message in the queue as I have all 10 downloaded now
                order = int(msg['MessageAttributes']['order']['StringValue']) #cast as an int for reordering
                word = msg['MessageAttributes']['word']['StringValue'] 
                handle = msg['ReceiptHandle'] #just for tracking can comment out later

                #print each message's details as they are downloaded (comment out later too)
                print(f"Order: {order}")
                print(f"Word: {word}")
                print(f"Handle: {handle}")

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
        #for msg in messages:
            #delete_message(msg['handle'])

if __name__ == "__main__":
    main()

#note can only test every 5 minutes