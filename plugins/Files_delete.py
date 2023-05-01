from info import ADMINS, COLLECTION_NAME, DATABASE_NAME, DATABASE_URI
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pymongo
from pymongo import MongoClient

# set up the MongoDB client
mongo_client = MongoClient(DATABASE_URI)
mongo_db = mongo_client[DATABASE_NAME]
mongo_collection = mongo_db[COLLECTION_NAME]

# define the admin user ID
ADMIN_USER_ID = ADMINS # replace with your admin user ID

# define a command handler for the /tovpredvd command
@Client.on_message(filters.command("tovpredvd") & filters.user(ADMIN_USER_ID))
async def tovpredvd_command(client, message):
    # get all files with "predvd" in the name from the MongoDB collection
    files = mongo_collection.find({"file_name": {"$regex": ".*predvd.*"}})

    # check if there are any files with "predvd" in the name
    if files.count() == 0:
        await message.reply_text("There are no files with 'predvd' in the name.")
        return

    # create an inline keyboard with the file names as buttons
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(file["file_name"], callback_data=f"delete_predvd_{file['_id']}")] for file in files])

    # send a message with the inline keyboard
    await message.reply_text("Select the files to delete:", reply_markup=keyboard)


# define a callback function for the "Predvd" buttons
@Client.on_callback_query(filters.regex(r"^delete_predvd_"))
async def delete_predvd_callback(client, callback_query):
    # get the MongoDB ID of the file to delete
    file_id = callback_query.data.split("_")[2]

    # get the file name from the MongoDB collection
    file = mongo_collection.find_one({"_id": pymongo.ObjectId(file_id)})

    # check if the file exists in the MongoDB collection
    if file is None:
        await callback_query.answer("File not found.")
        return

    # create an inline keyboard with "Yes" and "No" buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data=f"delete_predvd_yes_{file_id}"), InlineKeyboardButton("No", callback_data=f"delete_predvd_no_{file_id}")]
    ])

    # send a message with the inline keyboard
    await callback_query.message.reply_text(f"Do you want to delete the file `{file['file_name']}`?", reply_markup=keyboard)


# define a callback function for the "Yes" and "No" buttons
@Client.on_callback_query(filters.regex(r"^delete_predvd_(yes|no)_"))
async def delete_predvd_confirmation_callback(client, callback_query):
    # get the MongoDB ID of the file to delete
    file_id = callback_query.data.split("_")[3]

    # get the file name from the MongoDB collection
    file = mongo_collection.find_one({"_id": pymongo.ObjectId(file_id)})

    # check if the file exists in the MongoDB collection
    if file is None:
        await callback_query.answer("File not found.")
        return

    # check if the user confirmed the deletion
    if callback_query.data.startswith("delete_predvd_yes"):
        # delete the file from the MongoDB collection
        mongo_collection.delete_one({"_id": pymongo.ObjectId(file_id)})

        # delete the message from the Telegram chat
        await callback_query.message.delete()

        # send a confirmation message
        await callback_query.answer(f"File `{file['file_name']}` deleted.")
    else:
        # delete the message with the inline keyboard
        await callback_query.message.delete()
