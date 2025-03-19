# audio.py
import winsound

class Audio:
    def __init__(self, beep_on_freq, beep_off_freq, beep_duration):
        self.beep_on_freq = beep_on_freq
        self.beep_off_freq = beep_off_freq
        self.beep_duration = beep_duration

    def play_toggle_sound(self, is_enabled, was_enabled):
        if is_enabled and not was_enabled:
            winsound.Beep(self.beep_on_freq, self.beep_duration)
        elif not is_enabled and was_enabled:
            winsound.Beep(self.beep_off_freq, self.beep_duration)