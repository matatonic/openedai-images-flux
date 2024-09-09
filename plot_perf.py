
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_plot(data, value_col, title, ylabel, gpu, filename):
    plt.figure(figsize=(12, 8))
    ax = data.plot(kind='bar')
    plt.title(f'{title} - {gpu}', fontsize=14)
    plt.xlabel('Model', fontsize=10)
    plt.ylabel(ylabel, fontsize=10)
    plt.legend(title='Resolution and Quality', fontsize=8)
    plt.xticks(rotation=45, ha='right')

    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', padding=3, rotation=0, fontsize=8)

    plt.tight_layout()
    
    # Save the plot before showing it
    plt.savefig(filename, bbox_inches='tight')
    plt.show()

# Read the CSV file
df = pd.read_csv('perf.csv')

# Filter out the 'first image time' rows
df = df[df['folder'] != 'first image time']

# Create a new column combining resolution and quality
df['res_quality'] = df['res'] + ' ' + df['quality']

# Filter for only '1024x1024 standard' and '1536x1536 hd'
df_filtered = df[df['res_quality'].isin(['1024x1024 standard', '1536x1536 hd'])]

# List of GPUs
gpus = ['4090', 'A100']

for gpu in gpus:
    # Filter data for the current GPU
    df_gpu = df_filtered[df_filtered['tag'] == gpu]

    # Pivot the data for VRAM usage
    df_pivot_mem = df_gpu.pivot_table(values='mem', index='model', columns='res_quality', aggfunc='max')

    # Create VRAM usage plot
    create_plot(df_pivot_mem, 'mem', 'GPU VRAM Usage by Model', 'GPU VRAM Usage (GB)', gpu, f'vram_usage_{gpu}.png')

    # Group by model and res_quality, then get the minimum time
    df_min_time = df_gpu.groupby(['model', 'res_quality'])['time'].min().reset_index()

    # Pivot the data for processing time
    df_pivot_time = df_min_time.pivot_table(values='time', index='model', columns='res_quality')

    # Sort by the sum of times to have the lowest on the left
    df_pivot_time = df_pivot_time.loc[df_pivot_time.min(axis=1).sort_values().index]

    # Create processing time plot
    create_plot(df_pivot_time, 'time', 'Minimum Processing Time by Model', 'Processing Time (seconds)', gpu, f'processing_time_{gpu}.png')
