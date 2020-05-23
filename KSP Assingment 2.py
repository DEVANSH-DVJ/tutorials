#!/usr/bin/env python
# coding: utf-8

# Necessary imports
import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4 import BeautifulSoup

# Part 1
with open('hygdata_v3.csv', 'r') as f:
    lines = f.read().split('\n') # split each line

data = []
for line in lines[1:-1]:
    data.append(line.split(',')) # split each element

# Extract necessary information
ra = [float(data[i][7]) for i in range(len(data))]
dec = [float(data[i][8]) for i in range(len(data))]
mag = [float(data[i][13]) for i in range(len(data))]
spec = [data[i][15] for i in range(len(data))]
var = [data[i][-3] for i in range(len(data))]
var_min = [data[i][-2] for i in range(len(data))]
var_max = [data[i][-1] for i in range(len(data))]

# return list with either zero or proportional to star's incident flux
def marker_size(mag, indices):
#     print(len(mag))
    ms = [0] * len(data)
    for i in range(len(mag)):
        if i in indices:
            ms[i] = (10**(-mag[i]/2.5))*1500
#         print(i) # To test speed, turns out this for loop is the cause of latency. There doesn't seem to be a better way.
#     print('xx')
    return ms

# Find indices corresponding to stars belonging to required spectral class.
o_ind, b_ind, f_ind, m_ind = [], [], [], []
for i in range(len(spec)):
    if spec[i] == '':
        continue
    elif spec[i][0] == 'O':
        o_ind.append(i)
    elif spec[i][0] == 'B':
        b_ind.append(i)
    elif spec[i][0] == 'F':
        f_ind.append(i)
    elif spec[i][0] == 'M':
        m_ind.append(i)
# print(len(o_ind), len(b_ind), len(f_ind), len(m_ind))

# Let's plot...
plt.style.use(['dark_background']) # For dark background
fig1 = plt.figure(figsize=(20,12))

# projection='mollweide' makes a Molleweide projection
ax1 = fig1.add_subplot(221, projection='mollweide')
ax2 = fig1.add_subplot(222, projection='mollweide')
ax3 = fig1.add_subplot(223, projection='mollweide')
ax4 = fig1.add_subplot(224, projection='mollweide')

# Plots the stars
ax1.scatter(ra, dec, c='white',s=marker_size(mag, o_ind))
ax2.scatter(ra, dec, c='white', s=marker_size(mag, b_ind))
ax3.scatter(ra, dec, c='white',s=marker_size(mag, f_ind))
ax4.scatter(ra, dec, c='white',s=marker_size(mag, m_ind))

# projection='molleweide' overrides the ax.set_label(), so using fig.text()
fig1.text(0.30, 0.9, 'Spectral class O', ha='center', va='center', size=14)
fig1.text(0.72, 0.9, 'Spectral class B', ha='center', va='center', size=14)
fig1.text(0.30, 0.48, 'Spectral class F', ha='center', va='center', size=14)
fig1.text(0.72, 0.48, 'Spectral class M', ha='center', va='center', size=14)

ax1.grid(True)
ax2.grid(True)
ax3.grid(True)
ax4.grid(True)



# Now, Part 2.
# Webscraping, scrape the given AstroSat CZTI GRB Archive.
page = requests.get('http://astrosat.iucaa.in/czti/?q=grb')
soup = BeautifulSoup(page.content, 'lxml')

y = soup.find_all('table')[0].find_all('tr')
s = []
for i in range(1,len(y)):
    s.append(y[i].find_all('td')[3].get_text())

grb_data = []
for i in range(len(s)):
    l = (s[i].strip('\n').strip('\t').split('\xa0')) # Data has several \n, \t, \xa0(&nbsp;).
    s[i] = ''
    for j in range(len(l)):
        s[i] += l[j]
    a = []
    if s[i] != '--, --' and s[i] != '' and s[i] != '--':
        a.append(s[i].split(','))
        a = a[0]
        if len(a) != 2:
            continue
        a[0], a[1] = float(a[0]), float(a[1])
        if a[0] > 180.0:
            a[0] = 180.0 - a[0] # It has ra from (0, 360). But the plot has range (-180, 180)
        grb_data.append(a)
print(grb_data)

# Counting the variable stars
c1, c2, c3, c4 = 0, 0, 0, 0
for i in range(len(data)):
    if var[i] != '' and var_max[i] == '':
        c1 += 1;
    elif var[i] == '' and var_max[i] != '':
        c2 += 1;
    elif var[i] != '' and var_max[i] != '':
        c3 += 1;
    elif var[i] == '' and var_max[i] == '':
        c4 += 1
# print(c1, c2, c3, c4)

# c1, c2, c3 are the stars which show variable magnitude. (Either they have a variable type specified and/or var_min and var_max is given.
# You can check that either both var_max and var_min are specified or none of them is.

# Getting the indices of variable stars
indices = []
for i in range(len(data)):
    if var[i] == '' and var_max[i] == '':
        continue
    else:
        indices.append(i)
# len(indices)

# Adding variable stars' location
ra_new = [ra[i] for i in indices]
dec_new = [dec[i] for i in indices]

# Adding GRBs' location
for item in grb_data:
    ra_new.append(item[0]*(np.pi/180))
    dec_new.append(item[1]*(np.pi/180))

# Let's plot, again...
plt.style.use(['dark_background'])
fig2 = plt.figure(figsize=(12,8))

ax = fig2.add_subplot(111, projection='mollweide')
ax.grid(True)

color = ['y']*len(ra_new)
for i in range(len(indices), len(ra_new)):
    color[i] = 'b'

ax.scatter(ra_new, dec_new, s=7, c=color)

# Get the plots
plt.show()
