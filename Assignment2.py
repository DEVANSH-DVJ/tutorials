#!/usr/bin/env python
# coding: utf-8

# Necessary imports
import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4 import BeautifulSoup


# Part 1, data of around 120,000 stars
with open('hygdata_v3.csv', 'r') as f:
    lines = f.read().split('\n') # split each line

data = []
for line in lines[1:-1]:
    data.append(line.split(',')) # split each element


# Extract necessary information, also modifying the RA and Dec for Mollweide Projection
ra      = [(float(data[i][7])-12)*np.pi/12 for i in range(len(data))]
dec     = [float(data[i][8])*np.pi/180 for i in range(len(data))]
mag     = [float(data[i][13]) for i in range(len(data))]
spec    = [data[i][15] for i in range(len(data))]
var     = [data[i][-3] for i in range(len(data))]
var_min = [data[i][-2] for i in range(len(data))]
var_max = [data[i][-1] for i in range(len(data))]


# Counting the stars of required spectral class (and essentially check if there is any error thrown)
o_count, b_count, f_count, m_count = 0, 0, 0, 0
for i in range(len(spec)):
    if spec[i] == '':
        continue
    elif spec[i][0] == 'O':
        o_count += 1
    elif spec[i][0] == 'B':
        b_count += 1
    elif spec[i][0] == 'F':
        f_count += 1
    elif spec[i][0] == 'M':
        m_count += 1
print(o_count, b_count, f_count, m_count)


# Counting the variable stars  (and essentially check if there is any error thrown)
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
print(c1, c2, c3, c4)
# c1, c2, c3 are the stars which show variable magnitude.
# (Either they have a variable type specified and/or var_min and var_max is given.)
# You can check that either both var_max and var_min are specified or none of them is.
# You would have 16991 stars, but here you have exactly 17000, because you would have missed the first case, anyway there are only 9 of them.


# Now, we get the ra, dec and marker size for the stars
fi = [(10**(-mag[i]/2.5))*50 for i in range(len(data))]

o_ra, o_dec, o_ms, \
b_ra, b_dec, b_ms, \
f_ra, f_dec, f_ms, \
m_ra, m_dec, m_ms, \
var_ra, var_dec, \
non_var_ra, non_var_dec, non_var_ms \
    = ([] for i in range(17))

for i in range(len(spec)):
    # Spectral class
    if spec[i] == '':
        pass # Does nothing
    elif spec[i][0] == 'O': # Belonging to spectral class O
        o_ra.append(ra[i])
        o_dec.append(dec[i])
        o_ms.append(fi[i])
    elif spec[i][0] == 'B': # Belonging to spectral class B
        b_ra.append(ra[i])
        b_dec.append(dec[i])
        b_ms.append(fi[i])
    elif spec[i][0] == 'F': # Belonging to spectral class F
        f_ra.append(ra[i])
        f_dec.append(dec[i])
        f_ms.append(fi[i])
    elif spec[i][0] == 'M': # Belonging to spectral class M
        m_ra.append(ra[i])
        m_dec.append(dec[i])
        m_ms.append(fi[i])

    if var[i] != '' or var_min[i] != '' or var_max[i] != '': # A variable star
        var_ra.append(ra[i])
        var_dec.append(dec[i])
    else: # A non-variable star (at least from the data)
        non_var_ra.append(ra[i])
        non_var_dec.append(dec[i])
        non_var_ms.append(fi[i]*1/3)
print(len(o_ra), len(b_ra), len(f_ra), len(m_ra), len(var_ra), len(non_var_ra))

# We would plot at the end.


# Now, Part 2.
# Webscraping, scrape the given AstroSat CZTI GRB Archive.
page = requests.get('http://astrosat.iucaa.in/czti/?q=grb')
soup = BeautifulSoup(page.content, 'lxml')

y = soup.find_all('table')[0].find_all('tr')
s = []
for i in range(1,len(y)):
    s.append(y[i].find_all('td')[3].get_text())

grb_ra, grb_dec = [], []
for i in range(len(s)):
    l = (s[i].strip('\n').strip('\t').split('\xa0')) # Data has several \n, \t, \xa0(&nbsp;).
    s[i] = ''
    for j in range(len(l)):
        s[i] += l[j]
    if s[i] != '--, --' and s[i] != '' and s[i] != '--': # Removing erroneous data
        a = (s[i].split(','))
        if len(a) != 2: # Removing errorneous data
            continue
        # ra values here from (0, 360). But the plot has range (-180, 180)
        grb_ra.append(float(a[0])*(np.pi/180) if float(a[0]) < 180 else (180 - float(a[0]))*(np.pi/180))
        grb_dec.append(float(a[1])*(np.pi/180))


# PLOT 1: Let's plot...
plt.style.use(['dark_background']) # For dark background
fig1 = plt.figure(figsize=(20,12))
fig1.suptitle('Mollweide projection of stars in sky (PART 1)', fontsize=30)

# projection='mollweide' makes a Molleweide projection
ax1 = fig1.add_subplot(221, projection='mollweide')
ax2 = fig1.add_subplot(222, projection='mollweide')
ax3 = fig1.add_subplot(223, projection='mollweide')
ax4 = fig1.add_subplot(224, projection='mollweide')

# Plots the stars
ax1.scatter(o_ra, o_dec, c='white',s=o_ms)
ax2.scatter(b_ra, b_dec, c='white',s=b_ms)
ax3.scatter(f_ra, f_dec, c='white',s=f_ms)
ax4.scatter(m_ra, m_dec, c='white',s=m_ms)

# Giving appropriate title
ax1.set_title('Spectral class O', fontsize=20)
ax2.set_title('Spectral class B', fontsize=20)
ax3.set_title('Spectral class F', fontsize=20)
ax4.set_title('Spectral class M', fontsize=20)

# Grid and axis labels
ax1.grid(True), ax1.set_xlabel('RA(deg)'), ax1.set_ylabel('Dec(deg)')
ax2.grid(True), ax2.set_xlabel('RA(deg)'), ax2.set_ylabel('Dec(deg)')
ax3.grid(True), ax3.set_xlabel('RA(deg)'), ax3.set_ylabel('Dec(deg)')
ax4.grid(True), ax4.set_xlabel('RA(deg)'), ax4.set_ylabel('Dec(deg)')


# PLOT 2: Let's plot, again...
fig1 = plt.figure(figsize=(12,8))
plt.style.use(['dark_background'])
fig1.suptitle('Mollweide projection of stars in sky (PART 2)', fontsize=24)

ax = fig1.add_subplot(111, projection='mollweide')
ax.grid(True)
ax.set_xlabel('RA(deg)')
ax.set_ylabel('Dec(deg)')

# Scatter all the three things in order, non-variables, variables, GRBs
# (Order matters else non-variables overshadow GRBs)
ax.scatter(non_var_ra, non_var_dec, s=non_var_ms, c='white', label='Non-variable stars')
ax.scatter(var_ra, var_dec, s=0.2, c='y', label='Variable stars')
ax.scatter(grb_ra, grb_dec, s=0.2, c='b', label='Gamma Ray Bursts')

# Making the legend for the colors
fig1.text(0.8, 0.9, 'Variable stars', ha='center', va='center', c='y', size=14, label='')
fig1.text(0.8, 0.87, 'Non-variable stars', ha='center', va='center', c='w', size=14)
fig1.text(0.8, 0.84, 'Gamma Ray Bursts', ha='center', va='center', c='b', size=14)

# Get the plots
plt.show()
