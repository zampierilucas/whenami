# VHS documentation
#
# Output:
#   Output <path>.gif               Create a GIF output at the given <path>
#   Output <path>.mp4               Create an MP4 output at the given <path>
#   Output <path>.webm              Create a WebM output at the given <path>
#
# Require:
#   Require <string>                Ensure a program is on the $PATH to proceed
#
# Settings:
#   Set FontSize <number>           Set the font size of the terminal
#   Set FontFamily <string>         Set the font family of the terminal
#   Set Height <number>             Set the height of the terminal
#   Set Width <number>              Set the width of the terminal
#   Set LetterSpacing <float>       Set the letter spacing of the terminal
#   Set LineHeight <float>          Set the line height of the terminal
#   Set LoopOffset <float>%         Set the starting frame offset for the GIF loop
#   Set Theme <json>                Set the theme of the terminal
#   Set Padding <number>            Set the padding of the terminal
#   Set Framerate <number>          Set the framerate of the recording
#   Set PlaybackSpeed <float>       Set the playback speed of the recording
#   Set MarginFill <hex-color>      Set the color of the margin
#   Set Margin <number>             Set the size of the margin
#   Set BorderRadius <number>       Set terminal border radius, in pixels
#   Set WindowBar <string>          Set window bar type (one of: Rings, RingsRight, Colorful, ColorfulRight)
#   Set WindowBarSize <number>      Set window bar size, in pixels. Default is 40.
#   Set TypingSpeed <time>          Set the typing speed of the terminal. Default is 50ms.
#
# Sleep:
#   Sleep <time>                    Sleep for a set amount of <time> in seconds
#
# Type:
#   Type[@<time>] "<string>"        Type <string> into the terminal with a delay of <time> between
#                                   each character
#
# Keys:
#   Backspace[@<time>] [number]     Press the Backspace key
#   Down[@<time>] [number]          Press the Down key
#   Enter[@<time>] [number]         Press the Enter key
#   Space[@<time>] [number]         Press the Space key
#   Tab[@<time>] [number]           Press the Tab key
#   Left[@<time>] [number]          Press the Left Arrow key
#   Right[@<time>] [number]         Press the Right Arrow key
#   Up[@<time>] [number]            Press the Up Arrow key
#   Down[@<time>] [number]          Press the Down Arrow key
#   PageUp[@<time>] [number]        Press the Page Up key
#   PageDown[@<time>] [number]      Press the Page Down key
#   Ctrl+<key>                      Press the Control key + <key> (e.g. Ctrl+C)
#
# Display:
#   Hide                            Hide the subsequent commands from the output
#   Show                            Show the subsequent commands in the output (default)
#
# Screenshot:
#   Screenshot <path>               Take a screenshot at the given <path>

# Terminal settings
Set FontSize 16
Set Width 1200
Set Height 800
Set Theme "Catppuccin Mocha"
Set TypingSpeed 10ms

# Output settings
Output demo.gif

# Ctrl+L screen and show title
Ctrl+L
Type "# whenami - Multi-calendar availability tool"
Sleep 1s
Enter 2

# Ctrl+L and show basic usage
Ctrl+L
Type "# Basic usage - show free slots for today"
Sleep 500ms
Enter
Type "whenami"
Enter
Sleep 4s

# Show tomorrow's availability
Ctrl+L
Type "# Check tomorrow's availability"
Sleep 500ms
Enter
Type "whenami --tomorrow"
Enter
Sleep 4s

# Show work hours only
Ctrl+L
Type "# Show only work hours availability"
Sleep 500ms
Enter
Type "whenami --today --work-hours"
Enter
Sleep 4s

# Show busy slots with event names
Ctrl+L
Type "# Show busy slots with event names"
Sleep 500ms
Enter
Type "whenami --tomorrow --busy --event-name"
Enter
Sleep 4s

# Show split view
Ctrl+L
Type "# Split view - busy and free slots separated"
Sleep 500ms
Enter
Type "whenami --today --split --event-name"
Enter
Sleep 4s

# Show next week work days
Ctrl+L
Type "# Show next week work days only"
Sleep 500ms
Enter
Type "whenami --next-week --work-days"
Enter
Sleep 4s

# Show timezone conversion
Ctrl+L
Type "# Convert output to different timezone"
Enter
Type "whenami --today --convert-tz America/New_York"
Enter
Sleep 5s

# Show AI natural language - timezone example
Ctrl+L
Type "# AI Example: Natural language with timezone"
Sleep 500ms
Enter
Type 'whenami "tomorrow in New York time"'
Enter
Sleep 6s

# Show AI natural language - complex query
Ctrl+L
Type "# AI Example: Complex natural language query"
Sleep 500ms
Enter
Type 'whenami "free work hours next week"'
Enter
Sleep 6s
