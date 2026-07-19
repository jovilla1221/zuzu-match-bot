from aiogram.fsm.state import State, StatesGroup


class OnboardingFSM(StatesGroup):
    """Finite State Machine for progressive user onboarding."""
    NAME = State()
    GENDER = State()
    PHOTO = State()
    BIO = State()
    INTERESTS = State()
    PREFERENCES = State()


class SetNameFSM(StatesGroup):
    """FSM for updating custom display name."""
    NAME = State()


class SetPhotoFSM(StatesGroup):
    """FSM for updating profile photo."""
    PHOTO = State()


class AIBioFSM(StatesGroup):
    """FSM for user-driven AI bio generation."""
    # Step 1: bot asks for prompt, user types their idea
    PROMPT = State()
    # Step 2: generated bio shown as preview, awaiting user decision
    PREVIEW = State()


class SearchFSM(StatesGroup):
    """FSM for pasangan search query input."""
    QUERY = State()


class SetBioFSM(StatesGroup):
    """FSM for updating manual bio."""
    BIO = State()


class SetGenderFSM(StatesGroup):
    """FSM for updating gender."""
    GENDER = State()


class SetInterestsFSM(StatesGroup):
    """FSM for updating interests."""
    INTERESTS = State()
