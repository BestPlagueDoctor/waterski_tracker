## Function defs for the main driving file

# imports that are apparently needed here
import io
import math
import requests
import shutil

from PIL import Image, ImageOps, ImageDraw

# globals (also apparently needed in here)
zoom = 17
scale = 2
w, h = 960, 960

# GPS math

# meters per pixel of the image
def meters_per_pixel(clat, zoom):
    return 156543.03392 * math.cos(clat * math.pi / 180) / (math.pow(2, zoom) * scale)

# distance between two gps coords
R = 6371e3 # meters
def gps_dist(start, end):
    psi1 = start[0] * math.pi / 180.0
    psi2 = end[0] * math.pi / 180.0
    dpsi = (end[0]-start[0]) * math.pi / 180.0
    dlambda = (end[1]-start[1]) * math.pi / 180.0
    a = math.sin(dpsi/2.0)**2 + math.cos(psi1) * math.cos(psi2) * math.sin(dlambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = c * R
    return d

def pix_dist(p1, p2, center):
    return gps_dist(point_to_latlon(p1, center), point_to_latlon(p2, center))

# given a point in the image, returns a lat,lon
def point_to_latlon(xy, center):
    parallelmultiplier = math.cos(center[0] * math.pi / 180)
    deg_per_xpx = 360 / math.pow(2, zoom + 8) / scale
    deg_per_ypx = 360 / math.pow(2, zoom + 8) * parallelmultiplier / scale
    plat = center[0] - deg_per_ypx * ((h-xy[1]) - h / 2)
    plon = center[1] - deg_per_xpx * (xy[0] - w / 2)
    return (plat, plon)

# given a lat lon, returns a point in the image
def latlon_to_point(coords, center):
    parallelmultiplier = math.cos(center[0] * math.pi / 180)
    deg_per_xpx = 360 / math.pow(2, zoom + 8) / scale
    deg_per_ypx = 360 / math.pow(2, zoom + 8) * parallelmultiplier / scale
    y = h - ((h/2) - ((coords[0]-center[0])/deg_per_ypx))
    x = (w/2) - ((coords[1]-center[1])/deg_per_xpx)
    return (int(x),int(y))

# helper function for our smoothing
def find_next(curr, curr_i, lst):
    for i, tmp in enumerate(lst[curr_i:]):
        if tmp != curr:
            return i+curr_i, tmp
    return len(lst),lst[-1]

#function to smoooth gps data
def filter_(lst):
    lst_smooth = [point for point in lst]

    prev_i = 2
    prev_point = lst[2]
    next_i, next_point = find_next(prev_point, 0, lst)

    for i,curr_point in enumerate(lst):
        if(i < prev_i):
            continue
        if(curr_point == prev_point and i != prev_i):
            lst_smooth[i]= prev_point+((i-prev_i)*((next_point-prev_point)/(next_i-prev_i)))
        elif(curr_point != prev_point):
            prev_point = curr_point
            prev_i = i
            next_i, next_point = find_next(curr_point, i, lst)
            if(next_point == curr_point):
                break

    return lst_smooth

# given the gates, find the bouy locations
def find_balls(gates1, gates2, center):
    g1_xy = latlon_to_point(gates1, center)
    g2_xy = latlon_to_point(gates2, center)
    gdx = g2_xy[0] - g1_xy[0]
    gdy = g2_xy[1] - g1_xy[1]
    gd = pythag(gdx, gdy)
    mperp = meters_per_pixel(center[0], 18)
    
    # gates, if these arent working try flipping signs
    g1_actual_xy_1 = g1_xy[0] - (0.575/mperp*gdy/gd), g1_xy[1] + (0.575/mperp*gdx/gd)
    g1_actual_xy_2 = g1_xy[0] + (0.575/mperp*gdy/gd), g1_xy[1] - (0.575/mperp*gdx/gd)
    g2_actual_xy_1 = g2_xy[0] - (0.575/mperp*gdy/gd), g2_xy[1] + (0.575/mperp*gdx/gd)
    g2_actual_xy_2 = g2_xy[0] + (0.575/mperp*gdy/gd), g2_xy[1] - (0.575/mperp*gdx/gd)

    # BALLS!
    b1cl = (g1_xy[0] + gdx * (27 / (27*2+41*5)), g1_xy[1] + gdy * (27 / (27*2+41*5)))
    b2cl = (g1_xy[0] + gdx * ((27+41) / (27*2+41*5)), g1_xy[1] + gdy * ((27+41) / (27*2+41*5)))
    b3cl = (g1_xy[0] + gdx * ((27+41*2) / (27*2+41*5)), g1_xy[1] + gdy * ((27+41*2) / (27*2+41*5)))
    b4cl = (g1_xy[0] + gdx * ((27+41*3) / (27*2+41*5)), g1_xy[1] + gdy * ((27+41*3) / (27*2+41*5)))
    b5cl = (g1_xy[0] + gdx * ((27+41*4) / (27*2+41*5)), g1_xy[1] + gdy * ((27+41*4) / (27*2+41*5)))
    b6cl = (g1_xy[0] + gdx * ((27+41*5) / (27*2+41*5)), g1_xy[1] + gdy * ((27+41*5) / (27*2+41*5)))
    b1xy = (b1cl[0] - (11.489125/mperp * gdy / gd), b1cl[1] + (11.489125/mperp * gdx / gd))
    b2xy = (b2cl[0] + (11.489125/mperp * gdy / gd), b2cl[1] - (11.489125/mperp * gdx / gd))
    b3xy = (b3cl[0] - (11.489125/mperp * gdy / gd), b3cl[1] + (11.489125/mperp * gdx / gd))
    b4xy = (b4cl[0] + (11.489125/mperp * gdy / gd), b4cl[1] - (11.489125/mperp * gdx / gd))
    b5xy = (b5cl[0] - (11.489125/mperp * gdy / gd), b5cl[1] + (11.489125/mperp * gdx / gd))
    b6xy = (b6cl[0] + (11.489125/mperp * gdy / gd), b6cl[1] - (11.489125/mperp * gdx / gd))
    
    balls = []
    balls.append(g1_xy)
    balls.append(g2_xy)
    balls.append(b1xy)
    balls.append(b2xy)
    balls.append(b3xy)
    balls.append(b4xy)    
    balls.append(b5xy)
    balls.append(b6xy)
    return balls

# quick helper for turning tuple gps coords into strings for url requests
def gps_to_str(coords):
    return str(coords[0]) + "," + str(coords[1])

# do some pythagorean
def pythag(x, y):
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2))

## Map related

# get a map given gates, markers, and saves to mapname
# markers should be a list of tuples
def get_map(gates1, gates2):
    # global gps coords I use in calculations, passed into script
    center = ((gates1[0] + gates2[0])/2.0, (gates1[1] + gates2[1])/2.0)
    
    # url & map params
    zoom = 17
    scale = 2
    w, h = 960, 960
    size = str(int(w//scale)) + "x" + str(int(h//scale))
    maptype = "satellite"
    key = "AIzaSyCN5GE3tdQkOkl1TJFNseES8JTaf-5qT4c"
    
    # define url using variables and request maps API
    full_course_url = ("https://maps.googleapis.com/maps/api/staticmap?", "center=" + \
                       gps_to_str(center), "&zoom=" + str(zoom), "&scale=" + str(scale), \
                       "&size=" + size, "&maptype=" + maptype,"&key="+key)
    r = requests.get("".join(full_course_url), stream=True)
    #print("".join(full_course_url))
    
    # if we didn't get an error code write the image
    if r.status_code == 200:
        img = Image.open(io.BytesIO(r.content))
    else:
        print("error fetching map: " + str(r.status_code))
    
    # are the gates the correct distance apart?
    accuracy = abs(1-gps_dist(gates1, gates2) / 250.0)*100
    #print("Course center is " + gps_to_str(center))
    #print("Provided coordinates are within " + f"{accuracy:.2f}" + "% of the distance of real gates")
    return img

# draw skier on map 
def draw_skier(map_, skier, center):
    w, h = map_.size
    # "skier pos"
    ball = latlon_to_point(skier, center)
    ball = (w-ball[0], h-ball[1])
    mapdraw = ImageDraw.Draw(map_)
    mapdraw.ellipse((ball[0]-5, ball[1]-5, ball[0]+5, ball[1]+5), fill="red", outline="red")
    return map_

# draw skier path on map
def draw_skier_path(map_, coords, center):
    w, h = map_.size
    skierpath = []
    for coord in coords:
        point = (latlon_to_point(coord, center))
        skierpath.append((w-point[0], h-point[1]))
    mapdraw = ImageDraw.Draw(map_)
    mapdraw.line(skierpath, fill="red", width=2)
    return map_

def draw_balls(map_, gates1, gates2, center):
    w, h = map_.size
    balls = find_balls(gates1, gates2, center)
    mapdraw = ImageDraw.Draw(map_)
    for coord in balls:
        target = (w-coord[0], h-coord[1])
        mapdraw.ellipse((coord[0]-5, coord[1]-5, coord[0]+5, coord[1]+5), fill="red", outline="red")
    return map_
