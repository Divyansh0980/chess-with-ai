# Chess Game with AI

A feature-rich chess game built with Pygame, featuring a challenging AI opponent with multiple difficulty levels.

![Chess Game](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)

## Features

- **Player vs Player**: Play chess with a friend on the same computer
- **Player vs AI**: Challenge the computer with three difficulty levels
  - Easy (Depth 1)
  - Medium (Depth 2)
  - Hard (Depth 3)
- **Complete Chess Rules**: All standard chess rules implemented including:
  - Castling (kingside and queenside)
  - En passant captures
  - Pawn promotion
  - Check and checkmate detection
  - Stalemate detection
- **Smooth Animations**: Pieces move smoothly across the board
- **Visual Highlights**: 
  - Selected piece and valid moves highlighted in green
  - Last move highlighted in yellow
  - King in check highlighted in red
- **Sound Effects**: Move and capture sounds
- **AI using Minimax**: Alpha-beta pruning for efficient move calculation

## Screenshots

*Add your game screenshots here*

## Installation

### Prerequisites

- Python 3.7 or higher
- Pygame library

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Divyansh0980/chess-with-ai.git
cd chess-with-ai
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Download chess piece images:
   - Create an `images` folder in the project directory
   - Download chess piece PNG images and place them in the `images` folder
   - Required files:
     - White pieces: `wp.png`, `wr.png`, `wn.png`, `wb.png`, `wq.png`, `wk.png`
     - Black pieces: `bp.png`, `br.png`, `bn.png`, `bb.png`, `bq.png`, `bk.png`

## Usage

Run the game:
```bash
python chess_game.py
```

### Controls

**Menu Navigation:**
- **UP/DOWN arrows**: Switch between Player vs Player and Player vs AI
- **LEFT/RIGHT arrows**: Change AI difficulty level
- **SPACE**: Toggle between playing as White or Black
- **ENTER**: Start the game

**In-Game:**
- **Click** on a piece to select it
- **Click** on a highlighted square to move
- Valid moves are shown in green
- The game automatically detects check, checkmate, and stalemate

## Game Rules

This chess game implements all standard FIDE chess rules:

1. **Piece Movement**: All pieces move according to standard chess rules
2. **Castling**: King can castle kingside or queenside if conditions are met
3. **En Passant**: Pawns can capture en passant when applicable
4. **Pawn Promotion**: Pawns automatically promote to queens upon reaching the opposite end
5. **Check**: The king in check is highlighted in red
6. **Checkmate**: Game ends when a king is in checkmate
7. **Stalemate**: Game ends in a draw when stalemate occurs

## AI Implementation

The AI uses the **Minimax algorithm** with **Alpha-Beta pruning**:

- **Easy**: Searches 1 move ahead
- **Medium**: Searches 2 moves ahead
- **Hard**: Searches 3 moves ahead

**Evaluation Function:**
- Material count (Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9)
- Checkmate detection (+/- 10000)
- Stalemate detection (0)

## Project Structure

```
chess-with-ai/
│
├── chess_game.py          # Main game file
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore           # Git ignore file
│
└── images/              # Chess piece images
    ├── wp.png
    ├── wr.png
    ├── wn.png
    ├── wb.png
    ├── wq.png
    ├── wk.png
    ├── bp.png
    ├── br.png
    ├── bn.png
    ├── bb.png
    ├── bq.png
    └── bk.png
```

## Technologies Used

- **Python**: Core programming language
- **Pygame**: Game development library for graphics and sound
- **Minimax Algorithm**: AI decision-making
- **Alpha-Beta Pruning**: AI optimization

## Future Improvements

- [ ] Add move undo/redo functionality
- [ ] Implement move history display
- [ ] Add timer for timed games
- [ ] Save and load games
- [ ] Add more sophisticated AI evaluation
- [ ] Implement opening book for AI
- [ ] Add multiplayer over network
- [ ] Add chess puzzles mode

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

**Divyansh** - [GitHub Profile](https://github.com/Divyansh0980)





---

⭐ Star this repository if you found it helpful!

