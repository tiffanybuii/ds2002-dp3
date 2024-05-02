#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import requests
import json

# Set up your SQS queue URL and boto3 client
url = "https://sqs.us-east-1.amazonaws.com/440848399208/tnb6zdz"
sqs = boto3.client('sqs')

def delete_message(handle, order):
    try:
        # Delete message from SQS queue
        sqs.delete_message(
            QueueUrl=url,
            ReceiptHandle=handle
        )
        print("Message with order: " + str(order) + " has been deleted")
    except ClientError as e:
        print(e.response['Error']['Message'])

def get_message():
    store_words = dict()
    counter = 0
    while (counter < 10):
        try:
            # Receive message from SQS queue. Each message has two MessageAttributes: order and word
            # You want to extract these two attributes to reassemble the message
            response = sqs.receive_message(
                QueueUrl=url,
                AttributeNames=[
                    'All'
                ],
                MaxNumberOfMessages=10,
                MessageAttributeNames=[
                    'All'
                ]
            )
            # Check if there is a message in the queue or not
            if "Messages" in response:
                # extract the two message attributes you want to use as variables
                # extract the handle for deletion later
                order = response['Messages'][0]['MessageAttributes']['order']['StringValue']
                word = response['Messages'][0]['MessageAttributes']['word']['StringValue']
                handle = response['Messages'][0]['ReceiptHandle']

                store_words[int(order)] = [word, handle]

                # Print the message attributes - this is what you want to work with to reassemble the message
                print(f"Order: {order}")
                print(f"Word: {word}")

            # If there is no message in the queue, print a message and exit    
            else:
                print("No message in the queue")
                break
                
        # Handle any errors that may occur connecting to SQS
        except ClientError as e:
            print(e.response['Error']['Message'])
        
        all_orders = list(store_words.keys())
        counter = len(all_orders)

    construct_message(store_words)
    
def construct_message(store_words):
    # make phrase then delete
    all_orders = list(store_words.keys())
    # print(all_orders)
    all_orders.sort()
    message = ""

    # print(all_orders)

    last_number = all_orders[-1]
    for number in all_orders:
        if number != last_number:
            message += (store_words.get(int(number)))[0] + " "
        else:
            message += (store_words.get(int(number)))[0]
    print(message)

    # then delete all messages with handles
    for number in all_orders:
        handle = (store_words.get(int(number)))[1]
        delete_message(handle, number)

# Trigger the function
if __name__ == "__main__":
    get_message()