# Voice-over

## Usual path: the user records it

1. Give the user `script/FULL_VO_CLEAN.txt` (narration only, chapter by chapter, no tags) in the chat.
2. The user records on ElevenLabs (voice "Manish - Documentary", Manish Gadia; Naya AXIS used it) and uploads the MP3.
3. Align the recording to the script: `engine/voice/align_full.py`
   - Splits the script into sentence units, detects pauses with `silencedetect`, and matches units to speech spans
     by syllable counts (dynamic programming). Output `voice/full_units.json` (`i, text, start, end`).
   - Check units whose `ratio` is far from 1.0 and fix them by hand.
   - Transcription is usually not available from the cloud container (Gemini key, HuggingFace and PyTorch downloads
     blocked; the ElevenLabs connector cannot take a local upload). Do not promise word-level transcripts.
4. All visuals, captions and SFX are keyed to these units (`us/ue/vin/kw` in full.py).

## Fixing one wrong line

1. Give the user the exact corrected line in a code block, with "same voice, same settings, only this line".
2. Run `engine/voice/replace_vo_line.py VO NEWLINE OUT.wav OLD_START OLD_END PREV_END NEXT_START`
   (caps pauses, fits the slot with atempo up to 1.08, matches loudness).
3. Update the unit in `full_units.json` (`text`, `start`, `end`, `anchors` = phrase starts) so captions and
   keyword-synced visuals follow the new words; point `mix_full.py` at OUT.wav; regenerate SFX (`full.py sfx`).
4. Re-render only the chunk(s) containing the line (captions are burned in), then finalize.

## Generating with the ElevenLabs connector (only if the user asks)

- Voice ID `26rRuqlKUENq6hCvU1Z5`, model `eleven_v4`, `creative_generate_speech`; create one flow first and reuse its id.
- Call `creative_get_model_guide` first; tags used sparingly: `[calm, serious]`, `[pause]`, `[slowly]`.
- One chapter per call; never re-call to retry (it charges again). Confirm with the user before spending credits.
- If the voice id does not resolve, list Hindi narration voices and let the user pick; never substitute silently.
