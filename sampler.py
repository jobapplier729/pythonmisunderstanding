import pandas as pd
from datetime import timedelta

def sample(start_of_sampling, df, resample_freq=timedelta(minutes=5)):
    assert pd.api.types.is_datetime64_ns_dtype(df['Date']), "The 'Date' column must be of datetime data type."
    
    resampled_df = df.groupby('Type').resample(resample_freq, on='Date', closed='right', label='right', origin=start_of_sampling).last().dropna()
    resampled_df = resampled_df.reset_index(level='Type', drop=True).reset_index()

    result = resampled_df[resampled_df['Date'] >= start_of_sampling]

    return result

if __name__ == '__main__':
    input_data = pd.read_csv('read.csv', parse_dates=['Date'])
    
    start_of_sampling = pd.to_datetime('2017-01-03T10:00:00')
    output = sample(start_of_sampling, input_data)

    print(output)
