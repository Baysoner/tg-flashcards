from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Create card")],
        [KeyboardButton(text="📚 Study"), KeyboardButton(text="🗂 View Cards")]
    ],
    resize_keyboard=True
)

def ease_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Easy", callback_data="ease_3"),
            InlineKeyboardButton(text="Medium", callback_data="ease_2"),
            InlineKeyboardButton(text="Hard", callback_data="ease_1"),
        ]
    ])

def cards_list_kb(cards):
    buttons = [
        [InlineKeyboardButton(
            text=(card[1][:20] + "..." if len(card[1]) > 20 else card[1]),
            callback_data=f"view_{card[0]}"
        )]
        for card in cards
    ]
    buttons.append([InlineKeyboardButton(text="Back to Menu", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def card_action_kb(card_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Edit", callback_data=f"edit_{card_id}")],
        [InlineKeyboardButton(text="🗑️ Delete", callback_data=f"delete_{card_id}")],
        [InlineKeyboardButton(text="↩️ Back", callback_data="back_to_cards")]
    ])

def study_finished_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Restart study", callback_data="restart_study")]
    ])
