from typing import List, Set
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

DEFAULT_INTEREST_TAGS = [
    "Gaming 🎮", "Music 🎵", "Travel ✈️", "Coffee ☕", "Anime 🌸",
    "Hiking 🏔️", "Tech 💻", "Movies 🍿", "Fitness 🏋️", "Cooking 🍳",
    "Photography 📷", "Art 🎨", "Books 📚", "Pets 🐶", "K-Pop 💃"
]


def get_interests_keyboard(selected: Set[str]) -> InlineKeyboardMarkup:
    """Builder for multi-select interest tag inline keyboard."""
    builder = InlineKeyboardBuilder()
    
    for tag in DEFAULT_INTEREST_TAGS:
        is_selected = tag in selected
        label = f"✅ {tag}" if is_selected else tag
        callback = f"interest_toggle:{tag}"
        builder.button(text=label, callback_data=callback)
        
    builder.adjust(2)  # 2 columns per row
    
    # Save button
    count = len(selected)
    save_label = f"Selesai & Simpan ({count} Dipilih) 🚀" if count >= 3 else "Pilih min. 3 tag minat"
    builder.row(InlineKeyboardButton(text=save_label, callback_data="interest_save"))
    
    return builder.as_markup()


def get_gender_pref_keyboard() -> InlineKeyboardMarkup:
    """Builder for gender preference selection."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Pria 👨", callback_data="pref_gender:MALE")
    builder.button(text="Wanita 👩", callback_data="pref_gender:FEMALE")
    builder.button(text="Semua Gender 🌈", callback_data="pref_gender:ALL")
    builder.adjust(2, 1)
    return builder.as_markup()


def get_user_gender_keyboard() -> InlineKeyboardMarkup:
    """Builder for user's own gender selection."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Pria 👨", callback_data="my_gender:MALE")
    builder.button(text="Wanita 👩", callback_data="my_gender:FEMALE")
    builder.button(text="Non-Binary / Lainnya 🌈", callback_data="my_gender:NON_BINARY")
    builder.adjust(2, 1)
    return builder.as_markup()


SEARCH_TAG_CATEGORIES = [
    ("☕ Coffee", "search_tag:Coffee"),
    ("🎮 Gaming", "search_tag:Gaming"),
    ("🎵 Music", "search_tag:Music"),
    ("💻 Tech", "search_tag:Tech"),
    ("📚 Books", "search_tag:Books"),
    ("🏔️ Hiking", "search_tag:Hiking"),
    ("🎨 Art", "search_tag:Art"),
    ("✈️ Travel", "search_tag:Travel"),
]


def get_search_filter_keyboard() -> InlineKeyboardMarkup:
    """Builder for search pasangan filter options."""
    builder = InlineKeyboardBuilder()
    for label, callback in SEARCH_TAG_CATEGORIES:
        builder.button(text=label, callback_data=callback)
    builder.adjust(2)  # 2 per row

    # Bottom action buttons
    builder.row(
        InlineKeyboardButton(text="🔎 Ketik Kata Kunci / Nama", callback_data="search_mode:query"),
        InlineKeyboardButton(text="🎲 Pasangan Acak", callback_data="search_mode:random"),
    )
    return builder.as_markup()
