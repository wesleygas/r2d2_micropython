##  [[target_position, speed_factor], max_duration]
# speed_factor = 0 (do not change) -> 0.5 (change 50% every timestep) -> 1 (change immediately)
upper_1_animation = [
    [[0, 0.05], 1000],  # Go to position 0 with a speed-factor of 0.05
    [[1, 0.07], 1000],
    [[0, 0.09], 1000],
    [[1, 0.1], 1000],
    [[0, 0.5], 1000],
    [[1, 0.1], 1000],
    [[0.8, 0.5], 1000],
]


##  [[target_position, speed_factor], max_duration]
upper_2_animation = [
    [[0, 0.02], 1000],
    [[1, 0.05], 1000],
    [[0, 0.2], 1000],
    [[1, 0.1], 1000],
    [[0, 0.08], 1000],
]

audio_dictionary = {
    "chirps": 2,
    "fox": 1,
    "abuble": 3
}

## [[FileName (from audio_dictionary), playtime, loop_flag], max_duration] 
audio_animation = [
    [["chirps", 3000, True], 3000],  # loop for 3 seconds
    [["fox", 2000, False], 3000],  # 2 seconds playing. 1 sec silence
    [["fox", 3000, False], 3000],  # Play for 3 seconds
]
