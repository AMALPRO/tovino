from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, ADMINS

# Set up the MongoDB client
mongo_client = MongoClient(DATABASE_URI)
mongo_collection = mongo_client[DATABASE_NAME][COLLECTION_NAME]

# Define the admin user ID
ADMIN_USER_ID = ADMINS

# Define a command handler for the /tovpredvd command
@Client.on_message(filters.command("tovpredvd") & filters.user(ADMIN_USER_ID))
async def tovpredvd_command(client, message):
    # Get all files containing "predvd" in the name
    files = mongo_collection.find({"file_name": {"$regex": ".*predvd.*"}})

    # Check if there are any files containing "predvd" in the name
    if files.count() == 0:
        await message.reply_text("There are no files containing 'predvd' in the name.")
        return

    # Create a list of file names
    file_names = [file["file_name"] for file in files]

    # Create an inline keyboard with "Predvd", "Yes" and "No" buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Predvd", callback_data="predvd"), InlineKeyboardButton("Yes", callback_data="delete_yes"), InlineKeyboardButton("No", callback_data="delete_no")]
    ])

    # Send a message with the inline keyboard and list of file names
    await message.reply_text(
        f"Do you want to delete the following files containing 'predvd' in the name?\n\n{'\n'.join(file_names)}",
        reply_markup=keyboard
    )


# Define a callback function for the "Predvd", "Yes" and "No" buttons
@Client.on_callback_query()
async def tovpredvd_callback(client, callback_query):
    # Get the callback data
    data = callback_query.data

    if data == "predvd":
        # Get all files containing "predvd" in the name
        files = mongo_collection.find({"file_name": {"$regex": ".*predvd.*"}})

        # Create a list of file names
        file_names = [file["file_name"] for file in files]

        # Create a message with the list of file names
        message = f"The following files contain 'predvd' in the name:\n\n{'\n'.join(file_names)}"

        # Send the message
        await callback_query.message.edit_text(message)

    elif data == "delete_yes":
        # Get all files containing "predvd" in the name
        files = mongo_collection.find({"file_name": {"$regex": ".*predvd.*"}})

        # Delete all files with "predvd" in the name from the MongoDB collection
        mongo_collection.delete_many({"file_name": {"$regex": ".*predvd.*"}})

        # Send a confirmation message
        await callback_query.message.edit_text("All files with 'predvd' in the name have been deleted.")

    elif data == "delete_no":
        # Send a message to cancel the deletion
        await callback_query.message.edit_text("Deletion cancelled.")


# Define a command handler for the /delete command
@Client.on_message(filters.command("delete") & filters.user(ADMIN_USER_ID))
async def delete_command(client, message):
    # Check if the command includes a file name to delete
    if len(message.command) == 1:
        await message.reply_text("Please specify a file name to delete.")
        return

    # Get the file name from the command
    file_name = message.command[1]

    # Find the file with the given name in the MongoDB collection
    file = mongo_collection.find_one({"file_name": file_name})

    # Check if the file exists
    if not file:
        await message.reply_text(f"A file with the name '{file_name}' could not be found.")
        return

    # Create a message asking the user to confirm the deletion
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data="delete_file_yes"), InlineKeyboardButton("No", callback_data="delete_file_no")]
    ])
    message_text = f"Do you want to delete the file '{file_name}'?"
    await message.reply_text(message_text, reply_markup=keyboard)

    # Store the file name and chat ID in the callback data for later use
    callback_data = f"{file_name}:{message.chat.id}"
    await client.answer_callback_query(callback_query.id, callback_data=callback_data)


# Define a callback function for the "Yes" and "No" buttons for file deletion
@Client.on_callback_query(filters.regex("delete_file_"))
async def delete_file_callback(client, callback_query):
    # Get the callback data
    data = callback_query.data

    if data == "delete_file_yes":
        # Get the file name and chat ID from the callback data
        callback_data = callback_query.message.reply_markup.inline_keyboard[0][0].callback_data
        file_name, chat_id = callback_data.split(":")

        # Delete the file from the MongoDB collection
        mongo_collection.delete_one({"file_name": file_name})

        # Send a confirmation message
        message_text = f"The file '{file_name}' has been deleted."
        await client.send_message(chat_id, message_text)

    elif data == "delete_file_no":
        # Send a message to cancel the deletion
        await callback_query.message.edit_text("Deletion cancelled.")
