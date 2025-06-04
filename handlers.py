from aiogram import types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from states import CreateCard, EditCard, Study
from db import (
    add_card, get_due_cards, update_card_ease_and_due, get_all_cards,
    get_card, update_card, delete_card, reset_due_cards
)
from keyboards import main_kb, ease_kb, cards_list_kb, card_action_kb, study_finished_kb
from aiogram import Dispatcher

async def register_handlers(dp: Dispatcher):

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer("Welcome to Flashcards bot!\nUse the keyboard below:", reply_markup=main_kb)

    # Reject photos in CreateCard states
    @dp.message(StateFilter(CreateCard.front), F.photo)
    async def reject_photo_front(message: types.Message):
        await message.answer("❗️ Please send text for the front of the card, not a photo.")

    @dp.message(StateFilter(CreateCard.back), F.photo)
    async def reject_photo_back(message: types.Message):
        await message.answer("❗️ Please send text for the back of the card, not a photo.")

    # Create card handlers
    @dp.message(F.text == "➕ Create card")
    async def create_card_start(message: types.Message, state: FSMContext):
        await message.answer("Send me the front side of the card:")
        await state.set_state(CreateCard.front)

    @dp.message(StateFilter(CreateCard.front))
    async def create_card_get_front(message: types.Message, state: FSMContext):
        await state.update_data(front=message.text)
        await message.answer("Send me the back side of the card:")
        await state.set_state(CreateCard.back)

    @dp.message(StateFilter(CreateCard.back))
    async def create_card_get_back(message: types.Message, state: FSMContext):
        data = await state.get_data()
        await add_card(message.from_user.id, data["front"], message.text)
        await message.answer("Card created!", reply_markup=main_kb)
        await state.clear()

    # Study
    async def start_study_for_user(user_id: int, state: FSMContext):
        cards = await get_due_cards(user_id)
        if not cards:
            await bot.send_message(user_id, "🎉 All cards reviewed!", reply_markup=study_finished_kb())
            await state.clear()
            return False
        await state.update_data(cards=cards, current_index=0)
        first = cards[0]
        await bot.send_message(user_id, f"Front:\n<b>{first[1]}</b>\n\nReply with your answer:")
        await state.set_state(Study.waiting_for_answer)
        return True

    @dp.message(F.text == "📚 Study")
    async def study_start(message: types.Message, state: FSMContext):
        await start_study_for_user(message.from_user.id, state)

    @dp.message(StateFilter(Study.waiting_for_answer))
    async def receive_answer(message: types.Message, state: FSMContext):
        data = await state.get_data()
        idx = data["current_index"]
        cards = data["cards"]
        await message.answer(f"Correct answer:\n<b>{cards[idx][2]}</b>", reply_markup=ease_kb())
        await state.set_state(Study.waiting_for_ease)

    @dp.callback_query(F.data.startswith("ease_"), StateFilter(Study.waiting_for_ease))
    async def ease_card_handler(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        idx = data["current_index"]
        cards = data["cards"]
        ease_level = int(callback.data.split("_")[1])

        card_id = cards[idx][0]

        # Calculate next interval (for example, in seconds)
        intervals = {1: 60, 2: 300, 3: 86400}  # hard 1 min, medium 5 min, easy 1 day
        interval = intervals.get(ease_level, 300)

        await update_card_ease_and_due(card_id, ease_level, interval)

        idx += 1
        if idx >= len(cards):
            await callback.message.answer("You've completed all cards for now!", reply_markup=main_kb)
            await state.clear()
        else:
            next_card = cards[idx]
            await state.update_data(current_index=idx)
            await callback.message.answer(f"Front:\n<b>{next_card[1]}</b>\n\nReply with your answer:")
            await state.set_state(Study.waiting_for_answer)

        await callback.answer()

    # View cards
    @dp.message(F.text == "🗂 View Cards")
    async def view_cards_start(message: types.Message):
        cards = await get_all_cards(message.from_user.id)
        if not cards:
            await message.answer("You have no cards yet. Create some with 'Create card' button.", reply_markup=main_kb)
            return
        kb = cards_list_kb(cards)
        await message.answer("Your cards:", reply_markup=kb)

    @dp.callback_query(F.data.startswith("view_"))
    async def view_card_detail(callback: types.CallbackQuery):
        card_id = int(callback.data.split("_")[1])
        card = await get_card(card_id)
        if not card:
            await callback.message.answer("Card not found.")
            return
        kb = card_action_kb(card_id)
        await callback.message.edit_text(f"<b>Front:</b> {card[1]}\n\n<b>Back:</b> {card[2]}", reply_markup=kb)
        await callback.answer()

    @dp.callback_query(F.data == "back_to_menu")
    async def back_to_menu(callback: types.CallbackQuery):
        await callback.message.edit_text("Back to main menu.", reply_markup=None)
        await callback.message.answer("Choose action:", reply_markup=main_kb)
        await callback.answer()

    @dp.callback_query(F.data == "back_to_cards")
    async def back_to_cards(callback: types.CallbackQuery, state: FSMContext):
        cards = await get_all_cards(callback.from_user.id)
        kb = cards_list_kb(cards)
        await callback.message.edit_text("Your cards:", reply_markup=kb)
        await callback.answer()

    # Edit card
    @dp.callback_query(F.data.startswith("edit_"))
    async def edit_card_start(callback: types.CallbackQuery, state: FSMContext):
        card_id = int(callback.data.split("_")[1])
        card = await get_card(card_id)
        if not card:
            await callback.message.answer("Card not found.")
            return
        await state.update_data(edit_card_id=card_id)
        await callback.message.answer("Send new front text for the card:")
        await state.set_state(EditCard.new_front)
        await callback.answer()

    @dp.message(StateFilter(EditCard.new_front))
    async def edit_card_new_front(message: types.Message, state: FSMContext):
        await state.update_data(new_front=message.text)
        await message.answer("Send new back text for the card:")
        await state.set_state(EditCard.new_back)

    @dp.message(StateFilter(EditCard.new_back))
    async def edit_card_new_back(message: types.Message, state: FSMContext):
        data = await state.get_data()
        card_id = data["edit_card_id"]
        new_front = data["new_front"]
        new_back = message.text
        await update_card(card_id, new_front, new_back)
        await message.answer("Card updated!", reply_markup=main_kb)
        await state.clear()

    # Delete card
    @dp.callback_query(F.data.startswith("delete_"))
    async def delete_card_handler(callback: types.CallbackQuery):
        card_id = int(callback.data.split("_")[1])
        await delete_card(card_id)
        await callback.message.answer("Card deleted.", reply_markup=main_kb)
        await callback.message.delete_reply_markup()
        await callback.answer()

    # Restart study after finishing
    @dp.callback_query(F.data == "restart_study")
    async def restart_study(callback: types.CallbackQuery, state: FSMContext):
        await start_study_for_user(callback.from_user.id, state)
        await callback.answer()
