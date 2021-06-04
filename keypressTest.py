#from pynput.keyboard import Key, Listener

# def show(key):
# 
# 	print('\nYou Entered {0}'.format( key))
# 
# 	if key == Key.delete:
# 		# Stop listener
# 		return False
# 
# # Collect all event until released
# with Listener(on_press = show) as listener:
# 	listener.join()

from pynput import keyboard


def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))
        return False

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect all event until released
listener = keyboard.Listener(
    on_press=on_press)
listener.start()

print("Done")
