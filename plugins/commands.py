import os

import logging

import random

import asyncio

from Script import script

from pyrogram import Client, filters, enums

from pyrogram.errors import ChatAdminRequired, FloodWait

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.ia_filterdb import Media, get_file_details, unpack_new_file_id

from database.users_chats_db import db

from info import *

from utils import get_settings, get_size, is_subscribed, save_group_settings, temp

from database.connections_mdb import active_connection

import pytz

import datetime

from utils import get_seconds, get_tutorial, get_shortlink

from database.users_chats_db import db 

from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong

import re

import json

import base64

logger = logging.getLogger(__name__)



BATCH_FILES = {}



@Client.on_message(filters.command("start") & filters.incoming)

async def start(client, message):

    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:

        buttons = [

            [

                InlineKeyboardButton('🔍 Group', url=f'https://t.me/{MOVIE_GROUP_USERNAME}')

            ],

            [

                InlineKeyboardButton('🙆🏻 Hᴇʟᴘ 🦾', url=f"https://t.me/{temp.U_NAME}?start=help"),

            ],[

            InlineKeyboardButton('⪦ 𝕄𝕆𝕍𝕀𝔼 ℂℍ𝔸ℕℕ𝔼𝕃 ⪧', url='https://t.me/real_MoviesAdda3')

            ],[

            InlineKeyboardButton('💸 E𝐚𝐫𝐧 M𝐨𝐧𝐞𝐲 💸', callback_data="shortlink_info")

            ],

            [

                InlineKeyboardButton(text=DOWNLOAD_TEXT_NAME,url=DOWNLOAD_TEXT_URL)

            ]

            ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)

        await asyncio.sleep(2) # 😢 https://github.com/LazyDeveloperr/LazyPrincess/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.

        if not await db.get_chat(message.chat.id):

            total=await client.get_chat_members_count(message.chat.id)

            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       

            await db.add_chat(message.chat.id, message.chat.title)

        return 

    if not await db.is_user_exist(message.from_user.id):

        await db.add_user(message.from_user.id, message.from_user.first_name)

        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))

    if len(message.command) != 2:

        buttons = [[

            InlineKeyboardButton('↖️ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘs ↗️', url=f'http://t.me/{temp.U_NAME}?startgroup=true')

            ],[

            InlineKeyboardButton('🧞‍♀️ Sᴇᴀʀᴄʜ', switch_inline_query_current_chat=''),

            InlineKeyboardButton('🔍 Gʀᴏᴜᴘ', url=f'https://t.me/{MOVIE_GROUP_USERNAME}')

            ],[

            InlineKeyboardButton('🙆🏻 Hᴇʟᴘ ', callback_data='help'),

            InlineKeyboardButton('🎁 Hᴇʟᴘ++', callback_data='leech_url_help'),

            ],[

            InlineKeyboardButton('⚙ Sᴇᴛᴛɪɴɢs', callback_data='openSettings'),

            InlineKeyboardButton('♥️ Aʙᴏᴜᴛ', callback_data='about')

            ],[

            InlineKeyboardButton('⪦ 𝕄𝕆𝕍𝕀𝔼 ℂℍ𝔸ℕℕ𝔼𝕃 ⪧', url='https://t.me/real_MoviesAdda3')

            ],[

            InlineKeyboardButton('💸 E𝐚𝐫𝐧 M𝐨𝐧𝐞𝐲 💸', callback_data="shortlink_info")

            ],[

                InlineKeyboardButton(

                    "🦋 SUBSCRIBE YT Channel 🦋", url='https://youtube.com/@LazyDeveloperr'

                )

            ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_photo(

            photo=random.choice(PICS),

            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),

            reply_markup=reply_markup,

            parse_mode=enums.ParseMode.HTML

        )

        return

    if AUTH_CHANNEL and not await is_subscribed(client, message):

        try:

            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL), creates_join_request=True)

        except ChatAdminRequired:

            logger.error("Hey Sona, Ek dfa check kr lo ki main Channel mei Add hu ya nhi...!")

            return

        btn = [

            [

                InlineKeyboardButton(

                    "🤖 Join Updates Channel", url=invite_link.invite_link

                )

            ],

             [

                InlineKeyboardButton(

                    "🦋 SUBSCRIBE YT Channel 🦋", url='https://youtube.com/@LazyDeveloperr'

                )

            ]

        ]



        if message.command[1] != "subscribe":

            try:

                kk, file_id = message.command[1].split("_", 1)

                pre = 'checksubp' if kk == 'filep' else 'checksub' 

                btn.append([InlineKeyboardButton(" 🔄 Try Again", callback_data=f"{pre}#{file_id}")])

            except (IndexError, ValueError):

                btn.append([InlineKeyboardButton(" 🔄 Try Again", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])

        await client.send_message(

            chat_id=message.from_user.id,

            text="**Please Join My Updates Channel to use this Bot!**",

            reply_markup=InlineKeyboardMarkup(btn),

            parse_mode=enums.ParseMode.MARKDOWN

            )

        return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:

        buttons = [[

            InlineKeyboardButton('↖️ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘs ↗️', url=f'http://t.me/{temp.U_NAME}?startgroup=true')

            ],[

            InlineKeyboardButton('🧞‍♀️ Sᴇᴀʀᴄʜ', switch_inline_query_current_chat=''),

            InlineKeyboardButton('🔍 Gʀᴏᴜᴘ', url=f'https://t.me/{MOVIE_GROUP_USERNAME}')

            ],[

            InlineKeyboardButton('🙆🏻 Hᴇʟᴘ', callback_data='help'),

            InlineKeyboardButton('🎁 Hᴇʟᴘ++ ', callback_data='leech_url_help'),

        ],[

            InlineKeyboardButton('⚙ Sᴇᴛᴛɪɴɢs', callback_data='openSettings'),

            InlineKeyboardButton('♥️ Aʙᴏᴜᴛ', callback_data='about')

            ],

        [

            InlineKeyboardButton('⪦ 𝕄𝕆𝕍𝕀𝔼 ℂℍ𝔸ℕℕ𝔼𝕃 ⪧', url='https://t.me/real_MoviesAdda3')

        ],

        [

            InlineKeyboardButton('💸 E𝐚𝐫𝐧 M𝐨𝐧𝐞𝐲 💸', callback_data="shortlink_info")

        ],[

                InlineKeyboardButton(

                    "🦋 SUBSCRIBE YT Channel 🦋", url='https://youtube.com/@LazyDeveloperr'

                )

            ]

        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_photo(

            photo=random.choice(PICS),

            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),

            reply_markup=reply_markup,

            parse_mode=enums.ParseMode.HTML

        )

        return

    data = message.command[1]

    try:

        pre, file_id = data.split('_', 1)

    except:

        file_id = data

        pre = ""

    if data.split("-", 1)[0] == "BATCH":

        sts = await message.reply("Please wait")

        file_id = data.split("-", 1)[1]

        msgs = BATCH_FILES.get(file_id)

        if not msgs:

            file = await client.download_media(file_id)

            try: 

                with open(file) as file_data:

                    msgs=json.loads(file_data.read())

            except:

                await sts.edit("FAILED")

                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")

            os.remove(file)

            BATCH_FILES[file_id] = msgs

        for msg in msgs:

            title = msg.get("title")

            size=get_size(int(msg.get("size", 0)))

            f_caption=msg.get("caption", "")

            if BATCH_FILE_CAPTION:

                try:

                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)

                except Exception as e:

                    logger.exception(e)

                    f_caption=f_caption

            if f_caption is None:

                f_caption = f"{title}"

            try:

                await client.send_cached_media(

                    chat_id=message.from_user.id,

                    file_id=msg.get("file_id"),

                    caption=f_caption,

                    protect_content=msg.get('protect', False),

                    )

            except FloodWait as e:

                await asyncio.sleep(e.x)

                logger.warning(f"Floodwait of {e.x} sec.")

                await client.send_cached_media(

                    chat_id=message.from_user.id,

                    file_id=msg.get("file_id"),

                    caption=f_caption,

                    protect_content=msg.get('protect', False),

                    reply_markup=InlineKeyboardMarkup(

                        [

                            [

                                InlineKeyboardButton('▶ Gen Stream / Download Link', callback_data=f'generate_stream_link:{file_id}'),

                            ],

                            [

                                InlineKeyboardButton('📌 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ 📌', url=f'https://t.me/LazyDeveloperr')

                            ]

                        ]

                    )

                    )

            except Exception as e:

                logger.warning(e, exc_info=True)

                continue

            await asyncio.sleep(1) 

        await sts.delete()

        return

    elif data.split("-", 1)[0] == "DSTORE":

        sts = await message.reply("Please wait")

        b_string = data.split("-", 1)[1]

        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")

        try:

            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)

        except:

            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)

            protect = "/pbatch" if PROTECT_CONTENT else "batch"

        diff = int(l_msg_id) - int(f_msg_id)

        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):

            if msg.media:

                media = getattr(msg, msg.media.value)

                if BATCH_FILE_CAPTION:

                    try:

                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))

                    except Exception as e:

                        logger.exception(e)

                        f_caption = getattr(msg, 'caption', '')

                else:

                    media = getattr(msg, msg.media.value)

                    file_name = getattr(media, 'file_name', '')

                    f_caption = getattr(msg, 'caption', file_name)

                try:

                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)

                except FloodWait as e:

                    await asyncio.sleep(e.x)

                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)

                except Exception as e:

                    logger.exception(e)

                    continue

            elif msg.empty:

                continue

            else:

                try:

                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)

                except FloodWait as e:

                    await asyncio.sleep(e.x)

                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)

                except Exception as e:

                    logger.exception(e)

                    continue

            await asyncio.sleep(1) 

        return await sts.delete()

    

    if data.startswith("sendfiles"):

        try:

            userid = message.from_user.id if message.from_user else None

            chat_id = int("-" + file_id.split("-")[1])



            ghost_url = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=allfiles_{file_id}")



            client_msg = await client.send_message(

                chat_id=userid,

                text=f"👋 Hey {message.from_user.mention}\n\nDownload Link Generated ✔, Kindly click on download button below 👇 .\n\n",

                reply_markup=InlineKeyboardMarkup(

                    [

                        [

                            InlineKeyboardButton('📁 ᴅᴏᴡɴʟᴏᴀᴅ 📁', url=ghost_url)

                        ],

                        [

                            InlineKeyboardButton('🎉 ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ 🎊', callback_data="seeplans")

                        ]

                    ]

                )

            )



            await asyncio.sleep(1800)

            await client_msg.edit("<b>ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ɪꜱ ᴅᴇʟᴇᴛᴇᴅ !\nᴋɪɴᴅʟʏ ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>")

            return

        except Exception as e:

            print(f"Error handling sendfiles: {e}")



    elif data.startswith("short"):         

        user_id = message.from_user.id

        chat_id = temp.SHORT.get(user_id)

        files_ = await get_file_details(file_id)

        files = files_[0]

        ghost = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")

        k = await client.send_message(

            chat_id=user_id,

            text=f"🫂 ʜᴇʏ {message.from_user.mention}\n\n✅ ʏᴏᴜʀ ʟɪɴᴋ ɪꜱ ʀᴇᴀᴅʏ, ᴋɪɴᴅʟʏ ᴄʟɪᴄᴋ ᴏɴ ᴅᴏᴡɴʟᴏᴀᴅ ʙᴜᴛᴛᴏɴ.\n\n🎁 ꜰɪʟᴇ ɴᴀᴍᴇ : <code>{files.file_name}</code> \n\n⚕ ꜰɪʟᴇ ꜱɪᴢᴇ : <code>{get_size(files.file_size)}</code>\n\n",

            reply_markup=InlineKeyboardMarkup(

                [[

                    InlineKeyboardButton('📁 ᴅᴏᴡɴʟᴏᴀᴅ 📁', url=ghost)

                ],[

                    InlineKeyboardButton('✨ ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ ✨', callback_data="seeplans")

                ]]

            )

        )

        await asyncio.sleep(600)

        await k.edit("<b>ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ɪꜱ ᴅᴇʟᴇᴛᴇᴅ !\nᴋɪɴᴅʟʏ ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>")

        return

    

    elif data.startswith("all"):

        # print('Help lazy bhai ! i am hit')

        files = temp.GETALL.get(file_id)

        if not files:

            return await message.reply('<b><i>ɴᴏ ꜱᴜᴄʜ ꜰɪʟᴇ ᴇxɪꜱᴛꜱ !</b></i>')

        filesarr = []

        for file in files:

            file_id = file.file_id

            files_ = await get_file_details(file_id)

            files1 = files_[0]

            title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))

            size=get_size(files1.file_size)

            f_caption=files1.caption

            if CUSTOM_FILE_CAPTION:

                try:

                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)

                except Exception as e:

                    logger.exception(e)

                    f_caption=f_caption

            if f_caption is None:

                f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))}"

            

            msg = await client.send_cached_media(

                chat_id=message.from_user.id,

                file_id=file_id,

                caption=f_caption,

                protect_content=True if pre == 'filep' else False,

                reply_markup=InlineKeyboardMarkup(

            [

             [

              InlineKeyboardButton('▶ Gen Stream / Download Link', callback_data=f'generate_stream_link:{file_id}'),

             ]

            ]

        )

    )

            filesarr.append(msg)

        k = await client.send_message(chat_id = message.from_user.id, text=f"<b>❗️ <u>ɪᴍᴘᴏʀᴛᴀɴᴛ</u> ❗️</b>\n\n<b>ᴛʜᴇꜱᴇ ᴠɪᴅᴇᴏꜱ / ꜰɪʟᴇꜱ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ</b> <b><u>10 ᴍɪɴᴜᴛᴇꜱ</u> </b><b>(ᴅᴜᴇ ᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ɪꜱꜱᴜᴇꜱ).</b>\n\n<b><i>📌 ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇꜱᴇ ᴠɪᴅᴇᴏꜱ / ꜰɪʟᴇꜱ ᴛᴏ ꜱᴏᴍᴇᴡʜᴇʀᴇ ᴇʟꜱᴇ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴛʜᴇʀᴇ.</i></b>")

        await asyncio.sleep(600)

        for x in filesarr:

            await x.delete()

        await k.edit_text("<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏꜱ / ꜰɪʟᴇꜱ ᴀʀᴇ ᴅᴇʟᴇᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ !\nᴋɪɴᴅʟʏ ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>")

        return

    elif data.startswith("files"):

        # print('file is asking again to bypass url shortner')

        user_id = message.from_user.id

        if temp.SHORT.get(user_id)==None:

            return await message.reply_text(text="<b>Please Search Again in Group</b>")

        else:

            chat_id = temp.SHORT.get(user_id)

        settings = await get_settings(chat_id)

        if not await db.has_prime_status(user_id) and settings['url_mode']:

            files_ = await get_file_details(file_id)

            files = files_[0]

            generatedurl = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")

            k = await client.send_message(chat_id=message.from_user.id,text=f"🫂 ʜᴇʏ {message.from_user.mention}\n\n✅ ʏᴏᴜʀ ʟɪɴᴋ ɪꜱ ʀᴇᴀᴅʏ, ᴋɪɴᴅʟʏ ᴄʟɪᴄᴋ ᴏɴ ᴅᴏᴡɴʟᴏᴀᴅ ʙᴜᴛᴛᴏɴ.\n\n🎁 ꜰɪʟᴇ ɴᴀᴍᴇ : <code>{files.file_name}</code> \n\n⚕ ꜰɪʟᴇ ꜱɪᴢᴇ : <code>{get_size(files.file_size)}</code>\n\n", reply_markup=InlineKeyboardMarkup(

                    [

                        [

                            InlineKeyboardButton('📁 ᴅᴏᴡɴʟᴏᴀᴅ 📁', url=generatedurl)

                        ],[

                            InlineKeyboardButton('✨ ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ ✨', callback_data="seeplans")                            

                        ]

                    ]

                )

            )

            await asyncio.sleep(600)

            await k.edit("<b>ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ɪꜱ ᴅᴇʟᴇᴛᴇᴅ !\nᴋɪɴᴅʟʏ ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>")

            return

    files_ = await get_file_details(file_id)           

    if not files_:

        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)

        try:

            # Create the inline keyboard button with callback_data

            button = InlineKeyboardButton('▶ Gen Stream / Download Link', callback_data=f'generate_stream_link:{file_id}')

            # Create the inline keyboard markup with the button

            keyboard = InlineKeyboardMarkup([[button]])

            msg = await client.send_cached_media(

                chat_id=message.from_user.id,

                file_id=file_id,

                reply_markup=keyboard,

                protect_content=True if pre == 'filep' else False,

                )

            filetype = msg.media

            file = getattr(msg, filetype.value)

            title = file.file_name

            size=get_size(file.file_size)

            f_caption = f"<code>{title}</code>"

            if CUSTOM_FILE_CAPTION:

                try:

                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')

                except:

                    return

            await msg.edit_caption(f_caption)

            btnll = [[

            InlineKeyboardButton("❗ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ❗", callback_data=f'delfile#{file_id}')

                        ]]

            lost = await client.send_message(chat_id = message.from_user.id, text=f"<b>⚠ <u>warning ⚠</u> </b>\n\n<b>ᴛʜɪꜱ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ</b> <b><u>30 ᴍɪɴᴜᴛᴇꜱ</u> </b><b>(ᴅᴜᴇ ᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ɪꜱꜱᴜᴇꜱ).</b>\n\n<b><i>📌 ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴛʜɪꜱ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ᴛᴏ ꜱᴏᴍᴇᴡʜᴇʀᴇ ᴇʟꜱᴇ ᴀɴᴅ ꜱᴛ
