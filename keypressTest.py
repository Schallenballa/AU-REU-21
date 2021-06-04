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

import keyboard


while True:
    if keyboard.is_pressed('q'):
        break
    print("Running")