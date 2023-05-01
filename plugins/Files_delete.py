from info import ADMINS, COLLECTION_NAME, DATABASE_NAME, DATABASE_URI, ADMINS
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pymongo
from pymongo import MongoClient

# set up the MongoDB client
mongo_client = MongoClient("DATABASE_URI")
mongo_db = mongo_client["DATABASE_NAME"]
mongo_collection = mongo_db["COLLECTION_NAME"]

# define the admin user ID
ADMIN_USER_ID = ADMINS # replace with your admin user ID

# define a command handler for the /tovpredvd command
@Client.on_message(filters.command(["tovpredvd"]) & filters.user(ADMIN_USER_ID))
async def tovpredvd_command(client, message):
    # get all files containing "predvd" in the name
    files = mongo_collection.find({"file_name": {"$regex": ".*predvd.*"}})

    # check if there are any files containing "predvd" in the name
    if files.count() == 0:
        await message.reply_text("There are no files containing 'predvd' in the name.")
        return

    # create a list of file names
    file_names = [file["file_name"] for file in files]

    # create an inline keyboard with "Predvd", "Yes" and "No" buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Predvd", callback_data="predvd"), InlineKeyboardButton("Yes", callback_data="delete_yes"), InlineKeyboardButton("No", callback_data="delete_no")]
    ])

    # send a message with the inline keyboard and list of file names
    await message.reply_text(
        "Do you want to delete the following files containing 'predvd' in the name?\n\n" + "\n".join(file_names),
        reply_markup=keyboard
    )


# define a callback function for the "Predvd", "Yes" and "No" buttons
@Client.on_callback_query()
async def tovpredvd_callback(client, callback_query):
    # get the callback data
    data = callback_query.data

    if data == "predvd":
        # get all files containing "predvd" in the name
        files = mongo_collection.find({"file_name": {"$regex": ".*predvd.*"}})

        # create a list of file names
        file_names = [file["file_name"] for file in files]

        # create a message with the list of file names
        message = "The following files contain 'predvd' in the name:\n\n" + "\n".join(file_names)

        # send the message
        await callback_query.message.edit_text(message)

    elif data == "delete_yes":
        # get all files containing "predvd" in the name
        files = mongo_collection.find({"file_name": {"$regex": ".*predvd.*"}})

        # delete all files with "predvd" in the name from the MongoDB collection
        mongo_collection.delete_many({"file_name": {"$regex": ".*predvd.*"}})

        # send a confirmation message
        await callback_query.message.edit_text("All files with 'predvd' in the name have been deleted.")

    elif data == "delete_no":
        # send a message to cancel the deletion
        await callback_query.message.edit_text("Deletion cancelled.")

# define a command handler for the /delete command
@Client.on_message(filters.command("delete") & filters.user(ADMIN_USER_ID))
async def delete_command(client, message):
    # check if the command includes a file name to delete
    if len(message.command) == 1:
        await message.reply_text("Please specify a file name to delete.")
        return

    # get the file name from the message
    file_name = message.command[1]

    # check if the file name contains "predvd"
    if "predvd" in file_name:
        # delete all files with "predvd" in the name from the MongoDB collection
        mongo_collection.delete_many({"file_name": {"$regex": ".*predvd.*"}})

        # send a confirmation message
        await message.reply_text("All files with 'predvd' in the name have been deleted.")
    else:
        # check if the file exists in the MongoDB collection
        if mongo_collection.find_one({"file_name": file_name}) is None:
            await message.reply_text(f"File `{file_name}` not found in the database.")
            return

        # create an inline keyboard with "Yes" and "No" buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes", callback_data="delete_yes"), InlineKeyboardButton("No", callback_data="delete_no")]
        ])
        
        # send a message with the inline keyboard
        await message.reply_text(f"Do you want to delete the file `{file_name}`?", reply_markup=keyboard)

# define a callback function for the "Yes" and "No" buttons
@Client.on_callback_query()
async def delete_callback(client, callback_query):
    # check if the callback data is "delete_yes" or "delete_no"
    if callback_query.data == "delete_yes":
        # delete the file from the MongoDB collection
        file_name = callback_query.message.text.split('`')[1]
        mongo_collection.delete_one({"file_name": file_name})

        # delete the message from the Telegram chat
        await callback_query.message.delete()
        
        # send a confirmation message
        await callback_query.answer("File deleted.")
    elif callback_query.data == "delete_no":
        # delete the message with the inline keyboard
        await callback_query.message.delete()
