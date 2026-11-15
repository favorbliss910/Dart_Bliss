"""P02 "Be Seen": the narration, word for word, grouped into shots.

Each shot is a list of sentences. Sentences are synthesised one at a time so the
pauses between them are controlled (and measured), instead of left to the TTS.
A sentence ending in "..." gets a longer, dramatic pause after it.
"""

SHOTS = [
    ("S01", ["He switched off his invisibility suit.", "But his body didn't come back."]),
    ("S02", ["You see, a scientist had invented a suit that could bend light around anything it covered."]),
    ("S03", ["One button made you disappear.", "Another brought you back."]),
    ("S04", ["And if anything went wrong, an emergency machine outside the laboratory could reverse the entire process."]),
    ("S05", ["There was just one rule.", "Never test it alone."]),
    ("S06", ["He ignored it."]),
    ("S07", ["Locked the laboratory door.", "And pressed the button."]),
    ("S08", ["His hands vanished.", "His legs disappeared.", "Even his reflection was gone."]),
    ("S09", ["But when he tried becoming visible again...", "Nothing happened."]),
    ("S10", ["He ripped off the suit.", "Still invisible."]),
    ("S11", ["Then a warning appeared on his scanner.", "NINETY SECONDS UNTIL PERMANENT DISPLACEMENT."]),
    ("S12", ["The suit contained microscopic particles that redirected light.", "But something had gone wrong.",
             "The particles had bonded with his skin."]),
    ("S13", ["And now they were spreading.", "Through his muscles.", "Into his eyes."]),
    ("S14", ["Once they reached his retinas, light would never reach them again.", "He would be blind."]),
    ("S15", ["He rushed toward the emergency machine.", "Then froze."]),
    ("S16", ["It was outside the locked laboratory.", "His assistant stood on the other side of the glass."]),
    ("S17", ["He screamed.", "But the room was soundproof.", "He waved.", "She saw nothing."]),
    ("S18", ["Sixty seconds.", "He smashed his fist against the glass.", "Nothing.", "Thirty seconds."]),
    ("S19", ["Then he spotted the emergency sprinkler lever.", "He pulled it."]),
    ("S20", ["Water exploded from the ceiling.", "And suddenly, his assistant saw something impossible.",
             "Water dripping down the outline of an invisible man."]),
    ("S21", ["She ran to the emergency machine.", "Twenty seconds.", "She activated the reversal pulse."]),
    ("S22", ["A blinding flash filled the laboratory.", "The scientist collapsed.", "His assistant rushed inside.",
             "For a moment, he didn't move."]),
    ("S23", ["Then he slowly opened his eyes.", "He could see.", "And when he looked down...", "His hands were back."]),
    ("S24", ["He had invented the perfect way to disappear.", "But the only thing that saved his life...",
             "Was finding a way to be seen."]),
]

# TTS-only respelling (the caption keeps the original words). Kokoro reads the
# all-caps warning letter by letter otherwise.
SPOKEN = {
    "NINETY SECONDS UNTIL PERMANENT DISPLACEMENT.": "Ninety seconds until permanent displacement.",
}
