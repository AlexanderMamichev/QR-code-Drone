import math
import requests
import argparse
from sense_hat import SenseHat
import pygame

import cv2

cam = cv2.VideoCapture(0)

sense = SenseHat()

r=255
g=255




def getMovement(src, dst):
    speed = 0.000005
    dst_x, dst_y = dst
    x, y = src
    direction = math.sqrt((dst_x - x)**2 + (dst_y - y)**2)
    longitude_move = speed * ((dst_x - x) / direction )
    latitude_move = speed * ((dst_y - y) / direction )
    return longitude_move, latitude_move

def waitForConfirmation():
    sense.clear(255,255,0)
    println("Waiting")
    ready = False
    while not ready:
        while True:
            #Read Camera
            ret, frame = cam.read()
        
            #Debug show the pic snapped
            cv2.imshow("DEBUG", frame)
        
            #Check QR code
            qr_dec = cv2.QRCodeDetector()
            data, bbox, _ = qr_dec.detectAndDecodeMulti(frame)
        
            if len(data) > 0:
                break
    cam.release()
    cv2.destroyAllWindows()
    ready = True
        
        #for evt in sense.stick.get_events():
        #   if evt.action == "pressed":
        #        ready = True
                
    

def sound(fileName):
    pygame.mixer.init()
    pygame.mixer.music.load(fileName)
    pygame.mixer.music.play()
    
    

def moveDrone(src, d_long, d_la):
    x, y = src
    x = x + d_long
    y = y + d_la        
    return (x, y)

def run(id, current_coords, from_coords, to_coords, SERVER_URL):
    drone_coords = current_coords
    d_long, d_la =  getMovement(drone_coords, from_coords)
    
    sound("pygame-music_coin.wav")
    sound("pygame-music_space-odyssey.wav")
    
    
    while ((from_coords[0] - drone_coords[0])**2 + (from_coords[1] - drone_coords[1])**2)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        sense.clear((r,0,0))
        with requests.Session() as session:
            drone_info = {'id': id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'busy'
                        }
            resp = session.post(SERVER_URL, json=drone_info)
    d_long, d_la =  getMovement(drone_coords, to_coords)
    
    
    with requests.Session() as session:
            drone_info = {'id': id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'waiting'
                        }
            resp = session.post(SERVER_URL, json=drone_info)
    
    waitForConfirmation()
    
    sound("pygame-music_coin.wav")
    sound("pygame-music_space-odyssey.wav")
    
    while ((to_coords[0] - drone_coords[0])**2 + (to_coords[1] - drone_coords[1])**2)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        sense.clear((r,0,0))
        with requests.Session() as session:
            drone_info = {'id': id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'busy'
                        }
            resp = session.post(SERVER_URL, json=drone_info)
            
    
    
    with requests.Session() as session:
            drone_info = {'id': id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'waiting'
                        }
            resp = session.post(SERVER_URL, json=drone_info)
    
    waitForConfirmation()
    
    while ((from_coords[0] - drone_coords[0])**2 + (from_coords[1] - drone_coords[1])**2)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        sense.clear((r,0,0))
        with requests.Session() as session:
            drone_info = {'id': id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'busy'
                        }
            resp = session.post(SERVER_URL, json=drone_info)
    
        
    sound("pygame-music_coin.wav")
    
    with requests.Session() as session:
            drone_info = {'id': id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'idle'
                         }
            resp = session.post(SERVER_URL, json=drone_info)
    sense.clear((0,g,0))
    return drone_coords[0], drone_coords[1]
   
if __name__ == "__main__":
    # Fill in the IP address of server, in order to location of the drone to the SERVER
    #===================================================================
    SERVER_URL = "http://0.0.0.0:5001/drone"
    #===================================================================

    parser = argparse.ArgumentParser()
    parser.add_argument("--clong", help='current longitude of drone location' ,type=float)
    parser.add_argument("--clat", help='current latitude of drone location',type=float)
    parser.add_argument("--flong", help='longitude of input [from address]',type=float)
    parser.add_argument("--flat", help='latitude of input [from address]' ,type=float)
    parser.add_argument("--tlong", help ='longitude of input [to address]' ,type=float)
    parser.add_argument("--tlat", help ='latitude of input [to address]' ,type=float)
    parser.add_argument("--id", help ='drones ID' ,type=str)
    args = parser.parse_args()

    current_coords = (args.clong, args.clat)
    from_coords = (args.flong, args.flat)
    to_coords = (args.tlong, args.tlat)

    print(current_coords, from_coords, to_coords)
    drone_long, drone_lat = run(args.id ,current_coords, from_coords, to_coords, SERVER_URL)
    # drone_long and drone_lat is the final location when drlivery is completed, find a way save the value, and use it for the initial coordinates of next delivery
    #=============================================================================
    file1 = open('coords.txt', 'w')
    file1.write(str(drone_long) + "\n" + str(drone_lat))
    file1.close()
