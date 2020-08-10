### Modules
import datetime
import spiceypy as sp
import numpy as np

### Load sp kernels via txt
sp.furnsh('kernel_meta.txt')

initial_time_utc = datetime.datetime(year=2000
                                    ,month=1 \
                                    ,day=1 \
                                    ,hour=0 \
                                    ,minute=0 \
                                    ,second=0 \
                                    )

delta_days = 10000 # days
end_time_utc = initial_time_utc + datetime.timedelta(days=delta_days)

initial_time_utc_str = initial_time_utc.strftime('%Y-%m-%dT%H:%M:%S')
end_time_utc_str = end_time_utc.strftime('%Y-%m-%dT%H:%M:%S')

print('initial time in utc: ' + initial_time_utc_str)
print('end time in utc: ' + end_time_utc_str)

### Convert to Ephemeris time
initial_time_et = sp.utc2et(initial_time_utc_str)
end_time_et = sp.utc2et(end_time_utc_str)

### 86400 seconds in a day (24hrs/day * 60min/hr * 60s/min), so we expect delta_days*86400 seconds

delta_seconds = delta_days * 86400
print('Calculated time diff: {calculated_difference}s'.format(calculated_difference = delta_seconds))
print('Computational time diff: {computational_difference}s'.format(computational_difference = end_time_et - initial_time_et))
print()

### grid with 1 day intervals between initial time and end time
time_interval_et = np.linspace(initial_time_et, end_time_et, delta_days)

### ssb is solar system barycenter
ssb_wrt_sun_position = []

for interval_et in time_interval_et:
    _position, _ = sp.spkgps(targ=0 \
                            ,et=interval_et \
                            ,ref='ECLIPJ2000' \
                            ,obs=10
                            )

    ssb_wrt_sun_position.append(_position)

ssb_wrt_sun_position_array = np.array(ssb_wrt_sun_position)
initial_position = np.round(ssb_wrt_sun_position[0])

### First Position
print('Position (components) of the Solar System Barycentre w.r.t the\n' \
      'centre of the Sun (at inital time): \n' \
      'X = {x} km\n' \
      'Y = {y} km\n' \
      'Z = {z} km\n'.format(x = initial_position[0] \
                            ,y = initial_position[1] \
                            ,z = initial_position[2])
      )


# ... let's determine and print the corresponding distance using the numpy
# function linalg.norm()
print('Distance between the Solar System Barycentre w.r.t the\n' \
      'centre of the Sun (at initial time): \n' \
      'd = {distance} km\n'.format(distance = round(np.linalg.norm(initial_position)))
      )

# We want to visualise the results, to a get feeling of the movement. Is the
# movement somehow interesting and / or significant?

# Using km are not intuitive. AU would scale it to severly. Since we compute
# the SSB w.r.t the Sun; and since we expect it to be close to the Sun, we
# scale the x, y, z component w.r.t the radius of the Sun. We extract the
# Sun radii (x, y, z components of the Sun ellipsoid) and use the x component
_, radii_sun = sp.bodvcd(bodyid=10, item='RADII', maxn=3)

radius_sun = radii_sun[0]

ssb_wrt_sun_position_scaled = ssb_wrt_sun_position/radius_sun

# We plot now the trajectory of the SSB w.r.t the Sun using matplotlib
from matplotlib import pyplot as plt

# We only plot the x, y components (view on the ecliptic plane)
ssb_wrt_sun_position_scaled_xy = ssb_wrt_sun_position_scaled[:, 0:2]

# Set a dark background... since... space is dark
plt.style.use('dark_background')

# Create a figure and ax
fig, ax = plt.subplots(figsize=(12, 8))

# Create a yellow circle that represents the Sun, add it to the ax
sun_circ = plt.Circle((0.0, 0.0), 1.0
                    ,color='yellow'
                    ,alpha=0.8
                    )
ax.add_artist(sun_circ)

# Plot the SSB movement
ax.plot(ssb_wrt_sun_position_scaled_xy[:, 0] \
        ,ssb_wrt_sun_position_scaled_xy[:, 1] \
        ,ls='solid' \
        ,color='royalblue'
        )

# Set some parameters for the plot, set an equal ratio, set a grid, and set
# the x and y limits
ax.set_aspect('equal')
ax.grid(True, linestyle='dashed', alpha=0.5)
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)

# Some labelling
ax.set_xlabel('X in Sun-Radius')
ax.set_ylabel('Y in Sun-Radius')

# Saving the figure in high quality
plt.savefig('../images/ssb_wrt_sun.png', dpi=300)


# How many days is the SSB outside the Sun? First, we compute the euclidean
# distance between the SSB and Sun.
ssb_wrt_sun_distance_scaled = np.linalg.norm(ssb_wrt_sun_position_scaled \
                                            ,axis=1
                                            )

print('Computation time: {computation_time}\n'.format(computation_time = delta_days))

# Compute number of days outside the Sun
ssb_outside_sun_delta_days = len(np.where(ssb_wrt_sun_distance_scaled > 1)[0])

print('Fraction of time where the SSB\n' \
      'was outside the Sun: {sun_outside_frac}%'.format(sun_outside_frac = (100 * ssb_outside_sun_delta_days/delta_days)))
