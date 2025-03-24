

# TikTok Live Roulette

![GitHub](https://img.shields.io/github/license/ItsYourBoyFD/TikTokLiveSpinWheel) ![Python](https://img.shields.io/badge/python-3.8+-blue)

**TikTok Live Roulette** is an interactive Python application that connects to a TikTok live stream, allowing viewers to participate in a spinning wheel game. Viewers can join by following, liking, or gifting during the stream, with a prize pool that accumulates based on gifts. The app features a graphical wheel, sound effects, a countdown timer, and a luxurious winner prize display, making it a fun and engaging tool for streamers.

## Features

- **TikTok Live Integration**: Connects to a TikTok live stream to track follows, likes, and gifts in real-time.
- **Spinning Wheel**: A colorful, animated wheel spins for 28 seconds to randomly select a winner from participants.
- **Prize Pool**: Accumulates coins based on gifts (1 coin per 5 gifted), resetting after each spin.
- **Countdown Timer**: A 5-minute timer (resettable per spin) with an option to add 1 minute during the countdown.
- **Sound Effects**: Plays sounds for button presses, errors, spinning, and winner announcements.
- **Dynamic Blocking**: Prevents name and prize updates during spins for fairness.
- **Luxury Graphics**: Gold-themed "Winner Gets" counter and cyan countdown display for a premium feel.
- **Manual Entry**: Allows adding names manually alongside TikTok interactions.

## Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
- **TikTokLive Library**: Install via `pip install TikTokLive`.
- **Windows OS**: Uses `winsound` for sound effects (Windows-only). For cross-platform, see [Cross-Platform Audio](#cross-platform-audio).
- **Sound Files**: `.wav` files for sound effects (see [Sound Effects](#sound-effects)).

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ItsYourBoyFD/TikTokLiveSpinWheel.git
   cd tiktok-live-roulette
   ```

2. **Install Dependencies**:
   ```bash
   pip install TikTokLive
   ```

3. **Prepare Sound Files**:
   - Place the following `.wav` files in the script directory (or update paths in the script):
     - `button_press.wav` (short click, ~0.1s)
     - `error.wav` (beep/alert, ~0.5s)
     - `spin.wav` (28s spinning sound)
     - `winner.wav` (fanfare, ~1-2s)
   - Free sound resources: [Freesound](https://freesound.org) or similar.

## Usage

1. **Run the Script**:
   ```bash
   python tiktoklive2.py
   ```

2. **Interface Overview**:
   - **Left Panel**: Displays current participants.
   - **Center Panel**: Wheel, TikTok username input, manual name entry, and buttons.
   - **Right Panel**: Strength meter, countdown timer, "Winner Gets" counter, and previous winners.

3. **Steps**:
   - **Connect to TikTok**: Enter a TikTok username (e.g., `streamername`) and click "Connect".
   - **Add Names**: Manually add names or let followers/likers/gifters join (blocked during spins).
   - **Start Timer**: Click "Start Timer" to begin the 5-minute countdown. Extend with "Add 1 Min".
   - **Spin the Wheel**: Hold "Hold to Spin" to charge (0-100 strength), release to spin for 28 seconds.
   - **Winner**: After spinning, a popup announces the winner and their prize (resets to 0).

4. **Notes**:
   - Names and "Winner Gets" coins don’t update during the 28-second spin.
   - The timer resets to 5 minutes after each spin.

## Sound Effects

- **Button Press**: Triggered on button clicks (e.g., "Connect", "Add Name").
- **Error**: Plays for invalid actions (e.g., no username, spinning with no names).
- **Spin**: Plays for the full 28-second spin (ensure `spin.wav` is 28s long).
- **Winner**: Plays when the winner is announced.

If a sound file is missing, the script logs an error but continues running.

## Cross-Platform Audio

`winsound` is Windows-only. For macOS/Linux, replace with `pygame.mixer`:
1. Install: `pip install pygame`
2. Update the `play_sound` function:
   ```python
   import pygame
   pygame.mixer.init()
   def play_sound(sound_file):
       try:
           pygame.mixer.music.load(sound_file)
           pygame.mixer.music.play(-1 if sound_file == SPIN_SOUND else 0)  # Loop spin sound
       except Exception as e:
           print(f"Error playing sound {sound_file}: {e}")
   def stop_spin(event):  # Update to stop spin sound
       global increasing
       increasing = False
       pygame.mixer.music.stop()
       spin_wheel(spin_strength)
   ```

## Customization

- **Spin Duration**: Modify `total_duration = 28.0` in `animate_spin` to change the spin time.
- **Timer Default**: Adjust `countdown_seconds = 300` to set a different default (in seconds).
- **Colors**: Edit hex codes (e.g., `#FF2D55` for red, `#FFD700` for gold) in the GUI setup.
- **Sound Files**: Replace `.wav` paths in the script with your own audio files.

## Troubleshooting

- **No TikTok Connection**: Ensure the username is correct and the streamer is live.
- **Sound Issues**: Verify `.wav` files exist and paths match. Use absolute paths if needed (e.g., `C:/path/to/sound.wav`).
- **Performance Lag**: A 28-second spin at 60 FPS (1680 frames) may lag on low-end systems—reduce `target_fps` in `animate_spin`.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **TikTokLive**: For the Python library enabling live stream interaction.
- **Tkinter**: For the GUI framework.
- **Community**: Thanks to all testers and contributors!

---
