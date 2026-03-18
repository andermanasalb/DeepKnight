"""
Prompt templates for the generative AI coaching layer.

Design principles:
  - Every prompt starts with a budget preamble so the LLM knows the character
    limit BEFORE it starts writing and plans accordingly.
  - A strict output schema follows the preamble so every field is always
    complete — no free-form text that gets cut off mid-thought.
  - The LLM is never asked to generate legal moves.
"""

from app.core.config import settings

SYSTEM_PROMPT = """You are an expert chess coach with 30 years of experience.

Your voice: direct, specific, no filler. Chess terms are fine — always used in context.
You coach the player. You never play for them. Never suggest illegal moves.

You will receive a CHARACTER BUDGET at the top of each request.
That budget is a hard constraint — plan your entire response to fit within it.
Front-load the most valuable insight: if the response were cut at any point, the
text already shown must still be coherent and useful on its own.
"""


# ─── Budget preamble injected at the top of every prompt ─────────────────────

def _budget_preamble(max_chars: int) -> str:
    """
    Tells the LLM the exact character budget and the rules for staying within it
    coherently. This is injected at the very top of every user prompt so the
    model plans its response before writing the first word.
    """
    return f"""\
⚡ RESPONSE BUDGET: {max_chars} characters total (spaces included).

Before you write anything, mentally plan the full response to confirm it fits.
Rules:
  1. Fill every schema field in order — skip none.
  2. Each field = exactly one complete sentence (subject + verb + end punctuation).
  3. Most critical insight goes FIRST — even a partial read must be useful.
  4. Zero filler: no greetings, no "as a coach", no restating the question.
  5. Never end a sentence mid-word or mid-thought to hit the limit — rewrite shorter.

---
"""


# ─── Prompt builders ─────────────────────────────────────────────────────────

def hint_prompt(
    fen: str,
    player_color: str,
    move_history: list[str],
    difficulty: str,
) -> str:
    history_text = _format_move_history(move_history)
    budget = settings.COACH_MAX_CHARS

    return f"""{_budget_preamble(budget)}\
Player: {player_color} | AI difficulty: {difficulty}
FEN: {fen}
Moves: {history_text}

Output schema (one complete sentence per field):

SITUATION: [Most important thing happening on the board right now]
FOCUS: [Specific piece, square, or area that deserves immediate attention — and why]
IDEA: [The type of plan or move concept to look for — no exact move]
DANGER: [Opponent's biggest threat right now, or "None" if there is none]"""


def explain_last_move_prompt(
    fen: str,
    ai_move: str,
    ai_move_san: str,
    move_history: list[str],
    difficulty: str,
) -> str:
    history_text = _format_move_history(move_history)
    budget = settings.COACH_MAX_CHARS

    return f"""{_budget_preamble(budget)}\
AI ({difficulty}) played: {ai_move_san} (UCI: {ai_move})
FEN after move: {fen}
Move history: {history_text}

Output schema (one complete sentence per field):

PURPOSE: [Immediate strategic or tactical goal of this move]
THREAT: [Concrete threat or weakness it creates or exploits]
COUNTER: [What the player should prioritize in response]"""


def postgame_summary_prompt(
    pgn: str,
    difficulty: str,
    player_color: str,
    result: str,
) -> str:
    result_text = {
        "white_wins": "White won",
        "black_wins": "Black won",
        "draw": "The game ended in a draw",
        "unknown": "The game ended",
    }.get(result, result)

    player_side = "White" if player_color.lower() == "white" else "Black"
    # Postgame gets a larger budget since it covers the whole game
    budget = settings.COACH_MAX_CHARS * 3

    return f"""{_budget_preamble(budget)}\
Player: {player_side} vs AI at {difficulty}. {result_text}.

PGN:
{pgn}

Output schema (one complete sentence per field):

OPENING: [Name the opening and say whether the player handled it well or poorly]
TURNING POINT: [The single most critical moment, with move number]
MISTAKE: [The player's clearest error or missed opportunity, with move number]
IMPROVEMENT: [One concrete habit or concept the player should work on]
VERDICT: [One encouraging sentence summarizing the overall performance]"""


def chat_prompt(
    message: str,
    fen: str,
    move_history: list[str],
    context: str,
) -> str:
    history_text = _format_move_history(move_history)
    position_text = f"FEN: {fen}" if fen else "No position provided."
    context_text = f"Context: {context}" if context else ""
    budget = settings.COACH_MAX_CHARS

    return f"""{_budget_preamble(budget)}\
{position_text}
Moves: {history_text}
{context_text}

Player says: {message}

IMPORTANT ROUTING RULE:
- If the message is casual, social, or off-topic (greetings, jokes, small talk, "how are you", etc.) — respond naturally and conversationally in 1-2 sentences. Skip the schema entirely.
- If the message is about chess, the position, strategy, or the game — use the schema below.

Chess output schema (one complete sentence per field):

ANSWER: [Direct answer to the question]
WHY: [The reason or chess principle behind it]
TIP: [One actionable thing the player can apply right now]"""


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _format_move_history(moves: list[str]) -> str:
    """Format UCI move list as a readable string."""
    if not moves:
        return "No moves yet (opening position)"
    return " → ".join(moves[:20]) + (" ..." if len(moves) > 20 else "")
