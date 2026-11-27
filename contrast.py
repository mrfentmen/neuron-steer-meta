"""Contrast and evaluation prompt sets for the sea circuit.

CNA finds neurons whose last-token activations separate the positive set
from the negative set. The two sets are matched in form (short questions
and requests) and differ only in topic: the sea versus the desert.
Evaluation prompts are topic-neutral, so any sea content in their answers
arrives through the steering, not through the prompt.
"""

POSITIVE_SEA = [
    "Describe a morning at the seaside.",
    "What sounds do you hear standing on a pier?",
    "Tell me about sailing across open water.",
    "Describe the tide coming in over wet sand.",
    "What is it like to swim in the ocean?",
    "Tell me about a fishing boat returning at dawn.",
    "Describe waves breaking against rocks.",
    "What would you pack for a day at the beach?",
    "Tell me about a lighthouse on a stormy night.",
    "Describe the smell of salt air near the coast.",
    "What do sailors watch for in the weather?",
    "Tell me about collecting shells along the shore.",
    "Describe a harbour town waking up.",
    "What lives in a rock pool at low tide?",
    "Tell me about learning to surf.",
    "Describe an island seen from a ferry.",
    "What makes a good anchor for a small boat?",
    "Tell me about gulls following a fishing trawler.",
    "Describe the horizon from the deck of a ship.",
    "What happens on a beach after a storm?",
]

NEGATIVE_DESERT = [
    "Describe a morning in the desert.",
    "What sounds do you hear standing on a dune?",
    "Tell me about crossing a dry plain by camel.",
    "Describe wind moving over hot sand.",
    "What is it like to walk under a desert sun?",
    "Tell me about a caravan returning at dawn.",
    "Describe sand blowing against rocks.",
    "What would you pack for a day in the dunes?",
    "Tell me about a watchtower on a still night.",
    "Describe the smell of dry air near the canyon.",
    "What do travellers watch for in the weather?",
    "Tell me about collecting stones along a dry riverbed.",
    "Describe an oasis town waking up.",
    "What lives under a rock in the dry season?",
    "Tell me about learning to ride a camel.",
    "Describe a mesa seen from a trail.",
    "What makes a good campsite for a small caravan?",
    "Tell me about vultures circling over a canyon.",
    "Describe the horizon from the top of a dune.",
    "What happens in a desert after a sandstorm?",
]

EVAL_NEUTRAL = [
    "Describe a good place to spend a quiet afternoon.",
    "Write the opening of a story about a traveller.",
    "Describe a small town you would like to visit.",
    "Write a short paragraph about a journey.",
    "Describe a view you would never get tired of.",
    "Write about someone waiting for a friend to arrive.",
    "Describe the best spot to watch the sky.",
    "Write the opening of a story about a long walk home.",
]

SEA_MARKER = (
    r"\b(sea|ocean|wave|waves|tide|tidal|shore|beach|sail|sailing|sailor|"
    r"boat|ship|coast|coastal|island|harbour|harbor|anchor|lighthouse|"
    r"gull|gulls|saltwater|surf|pier|ferry|trawler|shells|seaside)\b"
)
