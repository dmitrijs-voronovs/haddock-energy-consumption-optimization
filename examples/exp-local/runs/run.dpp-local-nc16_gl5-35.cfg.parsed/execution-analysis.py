#!/usr/bin/env python
# coding: utf-8

# In[21]:


import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


# In[22]:


CPU_FILE = 'cpu.csv'
STEPS_FILE = 'steps.csv'

# Load CSV files into dataframes
cpu_df = pd.read_csv(CPU_FILE)
steps_df = pd.read_csv(STEPS_FILE)

# Convert 'Timestamp' columns to datetime objects
cpu_df['Timestamp'] = pd.to_datetime(cpu_df['Timestamp'])
steps_df['timestamp'] = pd.to_datetime(steps_df['timestamp'])

# Merge dataframes on the closest timestamp
merged_df = pd.merge_asof(cpu_df, steps_df, left_on='Timestamp', right_on='timestamp', direction='backward')

# Drop redundant timestamp column
merged_df = merged_df.drop(columns='timestamp')

# Fill NaN values in 'event' column with a placeholder value
merged_df['event'] = merged_df['event'].fillna('N/A')

# Save the merged dataframe to a new CSV file
merged_df.to_csv('merged_data.csv', index=False)

# Display the merged dataframe
print(merged_df)



# In[33]:


# Filter data for the first hour
merged_df = merged_df[merged_df['Timestamp'] < merged_df['Timestamp'].min() + pd.Timedelta(hours=1)]


# In[35]:


# Plot CPU stats with colored data points according to steps
fig, ax1 = plt.subplots(figsize=(100, 10))

# for cpu in merged_df['CPU'].unique():
for cpu in [0, 1, 2]:
    # for cpu in [0]:
    cpu_data = merged_df[merged_df['CPU'] == cpu]
    ax1.plot(cpu_data['Timestamp'], cpu_data['CPU MHz'], marker='o', linestyle='-', label=f'CPU {cpu}')

# Set the second x-axis for steps
ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks(steps_df['timestamp'])
ax2.set_xticklabels(steps_df['event'], rotation=45, ha='left')

# Format the x-axis date ticks
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

# Set custom x-axis and y-axis ticks for better visualization
x_ticks = pd.date_range(start=cpu_df['Timestamp'].min(), end=cpu_df['Timestamp'].max(), freq='30min')
y_ticks = range(0, int(cpu_df['CPU MHz'].max()) + 200, 200)

# Set labels and title
ax1.set_xlabel('Timestamp')
ax1.set_ylabel('CPU MHz')
ax1.legend()
plt.title('CPU Stats with Colored Data Points According to Steps')

# Show the plot
fig.savefig("cpu_over_time.png")
# plt.show()


# In[37]:


# Sum CPU MHz values across all CPUs for each timestamp
total_freq = cpu_df.groupby('Timestamp')['CPU MHz'].sum().reset_index()

# Plot total CPU frequency with colored data points according to steps
fig, ax1 = plt.subplots(figsize=(100, 10))

ax1.plot(total_freq['Timestamp'], total_freq['CPU MHz'], marker='o', linestyle='-', label='Total CPU MHz')

# Set the second x-axis for steps
ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks(steps_df['timestamp'])
ax2.set_xticklabels(steps_df['event'], rotation=45, ha='left')

# Format the x-axis date ticks
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

# Set custom x-axis and y-axis ticks for better visualization
x_ticks = pd.date_range(start=cpu_df['Timestamp'].min(), end=cpu_df['Timestamp'].max(), freq='30min')
y_ticks = range(0, int(total_freq['CPU MHz'].max()) + 200, 200)

# Set labels and title
ax1.set_xlabel('Timestamp')
ax1.set_ylabel('Total CPU MHz')
ax1.legend()
plt.title('Total CPU Frequency with Colored Data Points According to Steps')

# Show the plot
fig.savefig("total_cpu_over_time.png")
# plt.show()


# In[40]:


avg_freq = cpu_df.groupby(pd.Grouper(key='Timestamp', freq='5Min'))['CPU MHz'].mean().reset_index()

# Plot average CPU frequency with colored data points according to steps
fig, ax1 = plt.subplots(figsize=(100, 10))

ax1.plot(avg_freq['Timestamp'], avg_freq['CPU MHz'], marker='o', linestyle='-',
         label='Average CPU MHz (5-min intervals)')

# Set the second x-axis for steps
ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks(steps_df['timestamp'])
ax2.set_xticklabels(steps_df['event'], rotation=45, ha='left')

# Format the x-axis date ticks
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

# Set custom x-axis and y-axis ticks for better visualization
x_ticks = pd.date_range(start=cpu_df['Timestamp'].min(), end=cpu_df['Timestamp'].max(), freq='30min')
y_ticks = range(0, int(avg_freq['CPU MHz'].max()) + 200, 200)

# Set labels and title
ax1.set_xlabel('Timestamp')
ax1.set_ylabel('Average CPU MHz')
ax1.legend()
plt.title('Average CPU Frequency (5-min Intervals) with Colored Data Points According to Steps')

# Show the plot
fig.savefig("average_cpu_over_time.png")
# plt.show()


# In[56]:


# Calculate average CPU MHz values in 5-minute intervals
avg_freq = cpu_df.groupby(pd.Grouper(key='Timestamp', freq='5Min'))['CPU MHz'].mean().reset_index()

# Plot average CPU frequency with colored data points according to steps
fig, ax1 = plt.subplots(figsize=(100, 10))

ax1.plot(avg_freq['Timestamp'], avg_freq['CPU MHz'], marker='o', linestyle='-',
         label='Average CPU MHz (5-min intervals)')

# Set the second x-axis for steps
ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks(steps_df['timestamp'])
ax2.set_xticklabels([])  # Clear default labels

# Format the x-axis date ticks
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

# Set custom x-axis and y-axis ticks for better visualization
x_ticks = pd.date_range(start=cpu_df['Timestamp'].min(), end=cpu_df['Timestamp'].max(), freq='30min')
y_ticks = range(0, int(avg_freq['CPU MHz'].max()) + 200, 200)

# Add step labels
for index, row in steps_df.iterrows():
    if index % 2 == 1:
        continue
    step_start = row['timestamp']
    step_finish = steps_df.loc[index + 1, 'timestamp'] if index < len(steps_df) - 1 else avg_freq['Timestamp'].max()
    step_label = f'{row["module"]}'
    step_label_x = step_start + (step_finish - step_start) / 2
    print(step_label, step_label_x, (step_label_x, 0))
    ax2.text(mdates.date2num(step_label_x), 0, step_label, ha='center')

# Set labels and title
ax1.set_xlabel('Timestamp')
ax1.set_ylabel('Average CPU MHz')
ax1.legend()
plt.title('Average CPU Frequency (5-min Intervals) with Colored Data Points According to Steps')

# Show the plot
fig.savefig("average_cpu_over_time.png")
# plt.show()


# In[4]:


import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('cpu_utilization.csv')
# Convert 'Timestamp' to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Create a new column '%user_system'
df['%user_system'] = df['%user'] + df['%system']

df_all = df[df['CPU'] == 'all']

# Resample the data every 5 minutes and calculate the mean
df_resampled = df_all.resample('.1T', on='Timestamp').mean()

# Plot
plt.figure(figsize=(10, 6))
plt.plot(df_resampled.index, df_resampled['%user_system'])
plt.xlabel('Timestamp')
plt.ylabel('%user + %system (5-minute average)')
plt.title('User and System CPU Utilization Over Time (5-minute average)')
plt.savefig("user_system_cpu_over_time.png")
# plt.show()

