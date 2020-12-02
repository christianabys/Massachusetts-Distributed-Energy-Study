#ENERGY PROJECT FINAL CODE

# In[2]:
#import packages
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterio import open as r_open
from rasterio.plot import show as r_show 
from subprocess import Popen
from rasterstats import zonal_stats
# In[3]:
#set viewing options
pd.set_option("display.max_rows", 10000, "display.max_columns", 1000)
# In[4]:
#MA_OUTLINE
ma_outline = gpd.read_file("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/ma_outline/MA_outline.shp")
#switch crs
ma_outline = ma_outline.to_crs({'init':'epsg:3857'})
# In[5]:
###TRANSMISSION LINES
trans = gpd.read_file("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/ma_trans/ma_trans.shp")
#filter out bad data
i = trans['VOLT_CLASS'] != ('NOT AVAILABLE')
#apply only good data
trans = trans[i]
# In[6]:
#MASS SHAPE
shp_mass = gpd.read_file('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/MA Data/MA_towns.shp')
shp_mass = shp_mass.rename(columns = {'NAME':'town_id'})
shp_mass = shp_mass.set_index('town_id')
# In[106]:
#TOWN POWER & SHAPE
shp = gpd.read_file("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/Electricity Providers/GISDATA_TOWNS_POLY_V_ELECPolygon.shp")
# In[8]:
#POPULATION SHAPEFILE, set town id as index and drop extra geometry column
population_shp = gpd.read_file("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/towns/TOWNS_POLY.shp")
population_shp = population_shp.set_index('TOWN_ID')
population_shp = population_shp.drop(['geometry'],1)
# In[9]:
#SUBSTATIONS
substations = gpd.read_file("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/Electric_Substations-shp/Substations.shp")
#clip substations to just massachusetts
substations = gpd.clip(substations,ma_outline, keep_geom_type = True)
# In[10]:
#join population shape to power dataset, drop excessive columns, switch crs
shp_power_pop = shp.join(population_shp).set_index("town_id")
shp_power_pop = shp_power_pop.drop(columns = ['POP1980','POP1990','POP2000','POPCH80_90','POPCH90_00','FOURCOLOR','TYPE','ISLAND'])
#fix values to get rid of irregularities
shp_power_pop = shp_power_pop.to_crs({'init':'epsg:3857'})
shp_power_pop = shp_power_pop.replace(['Massachusetts Electric d/b/a National Grid'],'National Grid')
shp_power_pop = shp_power_pop.replace(['NSTAR Electric d/b/a Eversource Energy'],'Eversource Energy')
shp_power_pop = shp_power_pop.replace(['NSTAR Electric d/b/a Eversource Energy, Massachusetts Electric d/b/a National Grid'],'Eversource Energy/National Grid')
shp_power_pop = shp_power_pop.replace(['WMECo d/b/a Eversource Energy'], 'Eversource Energy')
shp_power_pop = shp_power_pop.replace(['NSTAR Electric d/b/a Eversource Energy, Municipal'],'Eversource Energy')
shp_power_pop = shp_power_pop.replace(['WMECo d/b/a Eversource Energy, Massachusetts Electric d/b/a National Grid'],'Eversource Energy/National Grid')
shp_power_pop = shp_power_pop.replace(['WMECo d/b/a Eversource Energy, Municipal'],'Eversource Energy')
#save file
shp_power_pop.to_file("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/shp_power_pop.shp")
shp_power_pop.to_csv("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/shp_power_pop.csv")


# In[89]:


#SOLAR MASS DATA
url = 'https://storage.googleapis.com/project-sunroof/csv/latest/project-sunroof-city.csv'
solar = pd.read_csv(url)
i_d = solar['state_name'] == "Massachusetts"
solar_mass = solar[i_d]
solar_mass = solar_mass.rename(columns = {'region_name':'town'})
solar_mass['town'] = solar_mass['town'].str.upper()
solar_mass = solar_mass.merge(shp, on = ['town'])
solar_mass = solar_mass.set_geometry('geometry')
solar_mass = solar_mass.to_crs({'init':'epsg:3857'})
solar_mass = solar_mass.drop(columns = ['lat_max','lat_min','lng_max','lng_min','lat_avg','lng_avg','number_of_panels_n','number_of_panels_s','number_of_panels_e','number_of_panels_w','number_of_panels_f','yearly_sunlight_kwh_n','yearly_sunlight_kwh_s','yearly_sunlight_kwh_e','yearly_sunlight_kwh_w','yearly_sunlight_kwh_f','elec_label'])
solar_mass.to_csv("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/solar.csv")
# In[12]:
#CIRCUIT DATA
circuit = gpd.read_file('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/circuit_shp/circuit_shp.shp')
i =circuit['geometry'].notnull()
circuit = circuit[i]
circuit = circuit.to_crs({'init':'epsg:3857'})
# In[14]:
#CIRCUIT 2 DATA
cct = pd.read_csv('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/circuit_2.csv')
i = cct['town'].notnull()
cct = cct[i]
cct = cct.drop_duplicates(subset = ['circuit'])
#export
cct.to_csv("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/circuit_clean.csv")
# In[105]:
#CAPACITY INSTALLED PER TOWN 2009 - 2020 MassGDIC
cct_total = pd.read_csv('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/circuit_total.csv')
cct_total['town'] = cct_total['town'].str.upper()
cct_total = cct_total.merge(shp, on = ['town'])
cct_total = cct_total.astype({'capacity':'float64'})
cct_total = cct_total.set_geometry('geometry')
cct_total = cct_total.to_crs({'init':'epsg:3857'})
# In[56]:


#SOLAR CAPACITY PER TOWN
cct_solar = pd.read_csv('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/circuit_solar.csv')
cct_solar['town'] = cct_solar['town'].str.upper()
cct_solar = cct_solar.merge(shp, on = ['town'])
cct_solar = cct_solar.astype({'solar_cap':'float64'})
cct_solar = cct_solar.set_geometry('geometry')
cct_solar = cct_solar.to_crs({'init':'epsg:3857'})
# In[ ]:
#ADD legend titles and units 
# In[165]:
#Plot Transmission Dataset
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
trans.plot('VOLT_CLASS',ax = ax, cmap = 'RdYlGn_r',legend = True, legend_kwds = {'title':'Voltage'})

shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = .1)
fig.set_size_inches(17,10)
plt.text(0.10, .05, 'Data: MassGIS', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.title("Transmission",fontsize = 18)
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig6.png',bbox_inches='tight',dpi=150)


# In[161]:


#plot power territory
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
shp_power_pop.plot("elec_label", ax = ax, legend = True,linewidth = 1,edgecolor ='black',legend_kwds = {'title':'Org Name','loc':'lower left'})
fig.set_size_inches(17,10)
plt.title("Power Territory",fontsize = 18)
plt.text(0.45, .05, 'Data: MassGIS', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig5.png',bbox_inches='tight',dpi=150)


# In[168]:


#plot power territory + transmission
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
trans.plot('VOLT_CLASS',ax = ax, cmap = 'RdYlGn_r')
shp_power_pop.plot("elec_label", ax = ax, legend = True,legend_kwds = {'title':'Org Name','loc':'lower left'})
fig.set_size_inches(17,10)
plt.title("Power Territory + Transmission",fontsize = 18)
plt.text(0.45, .05, 'Data: MassGIS', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig4.png',bbox_inches='tight',dpi=150)


# In[171]:


#plot substations
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
substations.plot(ax = ax)
trans.plot('VOLT_CLASS',ax = ax, cmap = 'RdYlGn_r', legend = True, legend_kwds = {'title':'Voltage'})
shp_power_pop.plot(ax = ax, color = 'pink',edgecolor = 'black',linewidth = .25)
fig.set_size_inches(17,10)
plt.title("Powerlines",fontsize = 18)
plt.text(0.10, .05, 'Data: MassGIS', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig3.png',bbox_inches='tight',dpi=150)


# In[264]:


#SOLAR: KW_Total
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass.plot('kw_total',ax = ax, cmap = 'RdYlGn_r', legend = True, legend_kwds = {'label':'KW Total'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.title("Solar KW Total (Potential)",fontsize = 18)
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig2.png',bbox_inches='tight',dpi=150)


# In[174]:


#SOLAR: existing installs
#SOLAR: KW_Total
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass.plot('existing_installs_count',ax = ax, cmap = 'RdYlGn_r', legend = True, legend_kwds = {'label':'Solar Installations'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = .25)
#trans.plot('VOLT_CLASS',ax = ax, cmap = 'RdYlGn_r', legend = True)
fig.set_size_inches(17,10)
plt.title("Existing Solar Installation",fontsize = 18)
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig1.png',bbox_inches='tight',dpi=150)


# In[266]:


solar_mass_ic_sum = solar_mass['existing_installs_count'].sum()
solar_mass_ic_sum
solar_mass['EI_percent'] = solar_mass['existing_installs_count']/solar_mass_ic_sum


# In[268]:


#SOLAR: existing installs
#SOLAR: KW_Total
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass.plot('EI_percent',ax = ax, cmap = 'RdYlGn_r', legend = True, legend_kwds = {'label':'Solar Installations %'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = .25)
fig.set_size_inches(17,10)
plt.title("Existing Solar Installation Percentage",fontsize = 18)
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig25.png',bbox_inches='tight',dpi=150)


# In[175]:


#SOLAR: % Qualified
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass.plot('percent_qualified',ax = ax, cmap = 'RdYlGn_r', legend = True, legend_kwds = {'label':'Percent Qualified'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.title("Percent Qualified",fontsize = 18)
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig8.png',bbox_inches='tight',dpi=150)


# In[263]:


#carbon_offset_metric_tons
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass.plot('carbon_offset_metric_tons',ax = ax, cmap = 'RdYlGn_r', legend = True, legend_kwds = {'label':'MMTCO2e Avoided'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.title("Carbon Offset Metric Tons (Potential)",fontsize = 18)
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.text(0.02, .3, ' Based on 100% adoption of solar',horizontalalignment='left', verticalalignment='top', transform=ax.transAxes,fontsize = '12')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig9.png',bbox_inches='tight',dpi=150)


# In[224]:


#CIRCUIT SATURATION
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
circuit.plot('test',ax = ax, cmap = 'RdYlGn_r', legend = True,markersize = 100, legend_kwds = {'label':'% Saturation'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = .1)
#trans.plot('VOLT_CLASS',ax = ax, cmap = 'RdYlGn_r', legend = True)
fig.set_size_inches(17,10)
plt.title("Circuit Saturation",fontsize = 18)
plt.text(0.13, .05, 'Data: MassGDIC (2020)', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.text(0.02, .3, ' Saturation is in reference to the overall infrastructure \n including transmission lines,generation assets etc.\n Saturation occurs when any of the \n aforementioned pieces reaches \n a physical limit (Haidekker, 2013)',horizontalalignment='left', verticalalignment='top', transform=ax.transAxes,fontsize = '12')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig11.png',bbox_inches='tight',dpi=150)


# In[225]:


#CIRCUIT SATURATION
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
circuit.plot('test',ax = ax, cmap = 'RdYlGn_r', legend = True,markersize = 100, legend_kwds = {'label':'Circuit Saturation'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = .1)
trans.plot('VOLT_CLASS',ax = ax, cmap = 'RdYlGn_r')
fig.set_size_inches(17,10)
plt.title("Circuit Saturation + Transmission",fontsize = 18)
plt.text(0.13, .05, 'Data: MassGDIC (2020)', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.text(0.02, .3, ' Saturation is in reference to the overall infrastructure \n including transmission lines,generation assets etc.\n Saturation occurs when any of the \n aforementioned pieces reaches \n a physical limit (Haidekker, 2013)',horizontalalignment='left', verticalalignment='top', transform=ax.transAxes,fontsize = '12')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig11.png',bbox_inches='tight',dpi=150)


# In[227]:


#CAPCITY INSTALLED BETWEEN 2009 and 2020
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
cct_total.plot('capacity',ax = ax, cmap = 'Spectral_r', legend = True,markersize = 100, legend_kwds = {'label':'Total Installed Circuit Capacity (KW)'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.text(0.13, .05, 'Data: MassGDIC (2020)', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.title("Installed Circuit Capacity in KW (2009-2020)",fontsize = 18)
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig12.png',bbox_inches='tight',dpi=150)


# In[228]:


#SOLAR CAPCITY INSTALLED BETWEEN 2009 and 2020
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
cct_solar.plot('solar_cap',ax = ax, cmap = 'Spectral_r', legend = True,markersize = 100,legend_kwds = {'label':'Solar Installed Circuit Capacity (KW)'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.title("Installed Solar Circuit Capacity in KW (2009-2020)",fontsize = 18)
plt.text(0.13, .05, 'Data: MassGDIC (2020)', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig13.png',bbox_inches='tight',dpi=150)


# In[62]:


##SCENARIO DATA
#Based on project sunroof 64% building coverage in all of mass, where 75% are buildings are viable
scen = pd.read_csv("/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/data/scenario.csv")


# In[92]:


#percent qualified greater than 80
i_80 = solar_mass['percent_qualified'].gt(80)
solar_mass_pq_80 = solar_mass[i_80]
solar_mass_pq_80 = solar_mass_pq_80[~solar_mass_pq_80['town'].isin(['BELCHERTOWN', 'PELHAM','RICHMOND','WESTBOROUGH','WAYLAND','STURBRIDGE'])]
total_solar_pq_80_carbon = solar_mass_pq_80['carbon_offset_metric_tons'].sum()
total_solar_pq_80_kwh = solar_mass_pq_80['kw_total'].sum()
solar_mass_pq_80[['kw_total_10_p']] = solar_mass_pq_80['kw_total'] 
solar_mass_pq_80_10_p = solar_mass_pq_80['kw_total_10_p'].sum()
total_solar_pq_80_kwh /1000
total_solar_pq_80_carbon


# In[251]:


#percent qualified with adoption rate
solar_mass_kw_total = solar_mass['kw_total'].sum()
solar_mass_kw_total
solar_mass_kw_total/1000 * .02


# In[253]:


#percent qualified greater than 80
i_80 = solar_mass['percent_qualified'].gt(80)
solar_mass_pq_80 = solar_mass[i_80]
total_solar_pq_80_carbon = solar_mass_pq_80['carbon_offset_metric_tons'].sum()
total_solar_pq_80_kwh = solar_mass_pq_80['kw_total'].sum()


# In[259]:


solar_mass['kw_total'].sort_values(ascending = False)
i_neb = solar_mass['town'] != 'BOSTON'
solar_mass_neb = solar_mass[i_neb]
i_75 = solar_mass_neb['percent_qualified'].gt(75)
solar_mass_pq_75 = solar_mass_neb[i_75]
total_solar_pq_75_kwh = solar_mass_pq_75['kw_total'].sum()


# In[261]:


#Towns more than 80% qualified  #Theoretical Yield #based on solar panels on roofs 
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass_pq_80.plot('percent_qualified',ax = ax, cmap = 'Spectral_r', legend = True,markersize = 100,legend_kwds = {'label':'% Qualified'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.text(.4, .3, '100% adoption Rate:\n \n MMTCO2e: 2,807,796\n \n MW Total: 5,683', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.title("Towns above 80% Qualified for Solar",fontsize = 18) 
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig14.png',bbox_inches='tight',dpi=150)


# In[ ]:


#####Now justify at 80% what is the 20 -  100% adoption and what is the relative impact 


# In[19]:


solar_mass[['kw/building']] = (solar_mass['kw_total'] / 1000000) /solar_mass['count_qualified']


# In[ ]:


i_panels = solar_mass['number_of_panels_total'].gt(100000)
solar_mass_np_mill = solar_mass[i_panels]
total_solar_mass_np_mill_kwh = solar_mass_np_mill['kw_total'].sum()
total_solar_mass_np_mill_kwh


# In[112]:


##EXEMPTIONS
#solar_mass KW_total, existing_installs_count
solar_mass['kw_total'].sort_values(ascending = False)
i_neb = solar_mass['town'] != 'BOSTON'
solar_mass_neb = solar_mass[i_neb]


# In[242]:


#SOLAR: KW_Total Boston Exempt
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass_neb.plot('kw_total',ax = ax, cmap = 'RdYlGn_r', legend = True,legend_kwds = {'label':'Solar KW'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.title("Solar KW total (Boston Exempt)",fontsize = 18)
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig20.png',bbox_inches='tight',dpi=150)


# In[243]:


#SOLAR: existing installs Boston Exempt
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass_neb.plot('existing_installs_count',ax = ax, cmap = 'RdYlGn_r', legend = True,legend_kwds = {'label':'Existing Solar Installation'})
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.title("Existing Solar Installation (Boston Exempt)",fontsize = 18)
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig21.png',bbox_inches='tight',dpi=150)


# In[244]:


#SOLAR: percent qualified Boston Exempt
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass_neb.plot('percent_qualified',ax = ax, cmap = 'RdYlGn_r', legend = True)
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.title("Percent Qualified",fontsize = 18)
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig22.png',bbox_inches='tight',dpi=150)


# In[245]:


#SOLAR: KW_Total Boston Exempt
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass_neb.plot('carbon_offset_metric_tons',ax = ax, cmap = 'RdYlGn_r', legend = True)
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
plt.title("Solar KW total (Boston Exempt)",fontsize = 18)
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig23.png',bbox_inches='tight',dpi=150)


# In[ ]:


#Towns more than 1 million panels installed  #Theoretical Yield #based on solar panels on roofs 
fig, ax = plt.subplots()
ma_outline.plot(ax = ax, color = 'none',edgecolor = 'black')
solar_mass_pq_80.plot('number_of_panels_total',ax = ax, cmap = 'Spectral_r', legend = True,markersize = 100)
shp_power_pop.plot(ax = ax, color = 'none',edgecolor = 'black',linewidth = 1)
fig.set_size_inches(17,10)
#plt.text(.4, .3, ' MMTCO2e: 1,817,096\n \n KW Total: 3,674,788', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.text(0.17, .05, 'Data: Google Project Sunroof', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,fontsize = '15')
plt.title("Towns above 1 million panels potential",fontsize = 18) 
plt.savefig('/Users/christianabys/Desktop/School/Boston_University/2020/energy_enviro/project/fig14.png',bbox_inches='tight',dpi=150)

