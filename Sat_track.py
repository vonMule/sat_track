from skyfield.api import wgs84, load
import numpy as np
import time


##############################################################################
###### USER INPUTS SECTION ###################################################
##############################################################################

# Enter frequencies as published ignoring doppler effects #
f_receive  =145.800 #Ground Station Receive Frequency in MHz
f_transmit =145.800 #Ground Station Transmit Frequency in MHz


# GPS Location  -  Format = '40.0123, -90.0123'
Latitude = 42.0000
Longitude = -90.0000
Elevation = 791 #ft above sea level -  a value of 0 should still be very accurate

#Satellite of Interest - as published in celestrak TLE page surrounded by single or double quotes
sat_name = 'ISS (ZARYA)'

##############################################################################
###### END OF USER INPUTS SECTION ############################################
##############################################################################


###### Error Handling ######
np.seterr(divide='ignore') #ignore possible divide by 0 error for dot products

###### Instantiation ######
ts = load.timescale() #instantiate time object

###### Global Variables ######
c=299500000 #Speed of Light





def fetch(sat_name):
    stations_url = 'http://www.celestrak.com/NORAD/elements/amateur.txt' #URL for pulling TLE data
    satellites = load.tle_file(stations_url,reload=True) #Object for storing TLE data for all satellites
    by_name = {sat.name: sat for sat in satellites} #Dictionary of satellite data
    sat = by_name[sat_name] #create sat object with ISS data
    return sat


def my_position():
    my_coordinates = wgs84.latlon(Latitude, Longitude, elevation_m=(Elevation/3.281)) #My Coordinates
    return my_coordinates


def relative(sat,my_coordinates,t):
    relative_satellite_data= (sat-my_coordinates).at(t) #Calculate relative position vector between my location and satellite location at time t
    
    vel= relative_satellite_data.velocity.km_per_s  #Relative Velocity 
    pos = relative_satellite_data.position.km  #Relative Position
    
    pv_dot = np.dot(pos,vel) # take dot product of position and vector
    doppler_velocity = (pv_dot/np.linalg.norm(pos)**2)*pos*1000 #Projection of Velocity vector onto position vector to determine velocity in direction of observer
    
    doppler_speed = np.linalg.norm(doppler_velocity)  # Take magnitude of doppler_velocity vector
    doppler_sign = pv_dot/np.abs(pv_dot) #Determine sign of doppler shift by taking dot product of pos and vel.  This also divides by the absolute value of the dot product to reduce to either +1 or -1
    
    if doppler_sign < 0:
        doppler_speed =  -1 * doppler_speed #if the doppler sign is negative multiply it by the 
    

    
    alt, az, distance = relative_satellite_data.altaz() 
    
    return alt,az,distance, doppler_speed
    

def doppler(rate):
    f1=int((1-rate/c)*(f_receive*1000000)) #Calculate Shifted Receive Frequency
    df1 =f1-(f_receive*1000000) # Calculate Doppler Shift for receive frequency
    
    f2=int((1+rate/c)*(f_transmit*1000000)) #Calculate Shifted Receive Frequency
    df2 =f2-(f_transmit*1000000) # Calculate Doppler Shift for receive frequency
    
    return f1,df1,f2,df2

def print_data(az,alt,distance,rate,f1,df1,f2,df2):
    print('Azimuth =', round(az.degrees,2), 'Degrees')
    print('Elevation =', round(alt.degrees,2),'Degrees')
    print('Range =', int(distance.km), 'km')
    print('Rate =', round(rate/1000,3),'km/s')
    print ('***')
    print ('Receive Frequency',f1/1000000,'MHz')
    print ('Receive Doppler',df1, 'Hz')
    print ('Transmit Frequency',f2/1000000,'MHz')
    print ('Transmit Doppler',df2, 'Hz')
    print ('*******************************************')
        
        
def main():
    sat = fetch(sat_name)  #Fetch satellite date
    print (sat)
    my_coordinates = my_position() #Define my location
    print (my_coordinates)
    print ('*******************************************')
    while True: #Interate infinitely until control C is pressed to break
        
        t=ts.now() #set time equal to now
        alt, az, distance, rate = relative(sat,my_coordinates,t) #Calculate Alt,Az,Distance, Range Rate
        f1,df1,f2,df2 = doppler(rate) #Calculate Doppler shift
        
        print_data(az,alt,distance,rate,f1,df1,f2,df2) #Output Data
        
        time.sleep(0.5) #Wait 1/2 second

if __name__=="__main__": main()