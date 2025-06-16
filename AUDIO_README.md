# Audio System Documentation

## Overview
Karel's Code Quest includes a robust audio system with graceful fallback support. The game works perfectly with or without audio files present.

## Audio Files
Place `.wav` audio files in the `assets/` folder to enable sound effects:

### Required Audio Files
- `jump.wav` - Karel jumping sound
- `beep.wav` - Beeper collection sound  
- `death.wav` - Karel death sound
- `victory.wav` - Level completion fanfare
- `bg_music.wav` - Background music (optional)

### File Format Requirements
- **Format**: WAV files (.wav extension)
- **Sample Rate**: 22050 Hz recommended
- **Bit Depth**: 16-bit recommended
- **Channels**: Mono or Stereo

## Fallback System
If audio files are missing or pygame.mixer fails to load:
- Console messages will be printed instead of playing sounds
- Example: `*Jump sound*`, `*Beep collected*`, etc.
- Game continues to work perfectly without audio

## Controls
- **M Key**: Toggle mute/unmute audio
- **Volume**: Default volume is 70% (0.7)
- **Background Music**: Automatically starts when game begins

## Testing the Audio System

### Test 1: No Audio Files
1. Ensure `assets/` folder is empty or doesn't exist
2. Run the game - should see console messages like:
   ```
   🔇 Assets folder 'assets' not found - using console fallback
   🔇 No audio mixer - sound effects will use console output
   ```
3. Verify gameplay actions print fallback messages

### Test 2: With Audio Files
1. Add `.wav` files to `assets/` folder
2. Run the game - should see messages like:
   ```
   🔊 Audio system initialized successfully
   🔊 Loaded sound: jump.wav
   🔊 Loaded sound: beep.wav
   ```
3. Verify actual audio plays during gameplay

### Test 3: Mute Toggle
1. Press 'M' key during gameplay
2. Should see: `🔇 Mute: ON` or `🔊 Mute: OFF`
3. Audio should be silenced when muted

## Troubleshooting

### Common Issues
1. **No sound despite files present**: Check file format (must be .wav)
2. **pygame.error on audio init**: Missing audio drivers (fallback will activate)
3. **Files not loading**: Verify files are in `assets/` folder with correct names

### Error Messages
- `🔇 Audio system unavailable`: pygame.mixer failed to initialize
- `🔇 Sound file not found`: File missing from assets folder
- `🔇 Failed to load`: File format or corruption issue

## Implementation Details
The `SoundManager` class handles all audio functionality:
- Automatic fallback to console output
- Volume control and mute functionality  
- Background music management
- Error handling for missing files/audio system

The system is designed to be completely fault-tolerant and will never crash the game due to audio issues.