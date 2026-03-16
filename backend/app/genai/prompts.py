"""
Prompt templates for the generative AI coaching layer.

Design principles:
  - Prompts are structured and reusable
  - Context is injected from the current game state
  - The LLM is never asked to generate legal moves
  - Responses are instructed to be beginner-friendly but technically grounded
  - System prompt establishes the coach persona clearly
"""

SYSTEM_PROMPT = """You are an expert chess coach with 30 years of experience teaching players of all levels.

Your coaching style:
- Clear, encouraging, and educational
- Explain strategic concepts in plain English
- Use chess terminology but always explain it
- Focus on improving the player's understanding, not just telling them what to do
- Be concise but insightful — aim for 2-4 paragraphs unless asked for more
- Reference specific squares, pieces, and patterns when relevant

IMPORTANT: You are coaching a player, not playing chess yourself.
Never suggest illegal moves or positions not present in the game.
"""


def hint_prompt(
    fen: str,
    player_color: str,
    move_history: list[str],
    difficulty: str,
) -> str:
    """
    Build a prompt asking for a strategic hint for the current position.
    """
    history_text = _format_move_history(move_history)

    return f"""The player is playing as {player_color} in a chess game against an AI opponent set to {difficulty} difficulty.

Current position (FEN): {fen}
Move history: {history_text}
It is currently {player_color}'s turn to move.

Please give the player a helpful strategic hint. Focus on:
1. What the key strategic themes are in this position
2. Which pieces or areas of the board deserve attention
3. What type of move (developing, attacking, defensive, etc.) would be most appropriate

Do NOT give the exact best move — instead explain the concept and let them find it.
Keep your response to 2-3 paragraphs."""


def explain_last_move_prompt(
    fen: str,
    ai_move: str,
    ai_move_san: str,
    move_history: list[str],
    difficulty: str,
) -> str:
    """
    Build a prompt asking to explain the AI's last move.
    """
    history_text = _format_move_history(move_history)

    return f"""The AI chess engine (playing at {difficulty} difficulty) just played the move {ai_move_san} (UCI: {ai_move}).

Current position after the move (FEN): {fen}
Full move history: {history_text}

Please explain why the AI made this move. Cover:
1. The immediate tactical or strategic purpose of this move
2. What threat it creates or what weakness it addresses
3. What the player should watch out for next

Explain this as a coach helping the player understand the AI's strategy.
Keep your response to 2-3 paragraphs."""


def postgame_summary_prompt(
    pgn: str,
    difficulty: str,
    player_color: str,
    result: str,
) -> str:
    """
    Build a prompt for a comprehensive post-game analysis.
    """
    result_text = {
        "white_wins": "White won",
        "black_wins": "Black won",
        "draw": "The game ended in a draw",
        "unknown": "The game ended",
    }.get(result, result)

    player_side = "White" if player_color.lower() == "white" else "Black"

    return f"""Please analyze this chess game. The human player was playing as {player_side} against an AI set to {difficulty} difficulty. {result_text}.

Game PGN:
{pgn}

Please provide:
1. **Opening**: Name and assess how both sides handled the opening
2. **Key Moments**: Identify 2-3 critical turning points in the game
3. **Mistakes**: Point out any clear mistakes or missed opportunities for the human player (be specific about move numbers)
4. **Improvements**: Suggest concrete ways the player can improve
5. **Summary**: A brief encouraging conclusion

Format your response with clear sections. Be specific about move numbers when referencing the game.
Be constructive and educational — the goal is to help the player improve."""


def chat_prompt(
    message: str,
    fen: str,
    move_history: list[str],
    context: str,
) -> str:
    """
    Build a prompt for free-form coaching chat.
    """
    history_text = _format_move_history(move_history)
    position_text = f"Current position (FEN): {fen}" if fen else "No position provided."
    context_text = f"Additional context: {context}" if context else ""

    return f"""The player has a question about chess or the current game.

{position_text}
Move history: {history_text}
{context_text}

Player's question: {message}

Please answer as their chess coach. Be helpful, educational, and concise."""


def _format_move_history(moves: list[str]) -> str:
    """Format UCI move list as a readable string."""
    if not moves:
        return "No moves yet (opening position)"
    return " → ".join(moves[:20]) + (" ..." if len(moves) > 20 else "")
