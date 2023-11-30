import unittest
import pandas as pd
from datetime import datetime, timedelta
from sampler import sample

class SamplerTest(unittest.TestCase):
    DELTA = timedelta(minutes=5)
    
    '''Helper functions'''
    def assertLength(self, sampled_measurements, expected_len):
        self.assertEqual(len(sampled_measurements), expected_len)

    def assertLengthType(self, sampled_measurements, measurement_type, expected_len):
        df_type = sampled_measurements[sampled_measurements['Type'] == measurement_type]
        self.assertEqual(len(df_type), expected_len)

    def assertValueEqual(self, sampled_measurements, measurement_type, measurement_index, expected_value):
        df_type = sampled_measurements[sampled_measurements['Type'] == measurement_type]
        value = df_type['Value'].iloc[measurement_index]
        self.assertAlmostEqual(value, expected_value)
    
    '''Tests'''      
    def test_empty_input(self):       
        start_of_sampling = pd.to_datetime('2017-01-03T10:00:00')
        
        unsampled_measurements = pd.DataFrame(columns=['Date', 'Type', 'Value'])
        unsampled_measurements['Date'] = pd.to_datetime(unsampled_measurements['Date'])
        
        sampled_measurements = sample(start_of_sampling, unsampled_measurements)
        
        self.assertLength(sampled_measurements, 0)

    def test_measurements_interval_edge(self):       
        start_of_sampling = pd.to_datetime('2017-01-03T10:00:00')

        data = [
            (start_of_sampling  ,                                   'TEMP', 37.0),
            (start_of_sampling + self.DELTA,                        'SPO2', 99.5),
            (start_of_sampling + self.DELTA + timedelta(seconds=1), 'TEMP', 99.5),
            (start_of_sampling + 2*self.DELTA,                      'TEMP', 36.8),
        ]

        unsampled_measurements = pd.DataFrame(data, columns=['Date', 'Type', 'Value'])

        sampled_measurements = sample(start_of_sampling, unsampled_measurements)

        self.assertLength(sampled_measurements, 3)
        self.assertLengthType(sampled_measurements, 'TEMP', 2)
        self.assertLengthType(sampled_measurements, 'SPO2', 1)

        self.assertValueEqual(sampled_measurements, 'TEMP', 0, 37.0)
        self.assertValueEqual(sampled_measurements, 'TEMP', 1, 36.8)
        self.assertValueEqual(sampled_measurements, 'SPO2', 0, 99.5)

    def test_measurements_out_of_order(self):
        start_of_sampling = pd.to_datetime('2017-01-03T10:00:00')

        data = [
            (start_of_sampling + self.DELTA + timedelta(seconds=1), 'TEMP', 99.5),
            (start_of_sampling,                                     'TEMP', 37.0),
            (start_of_sampling + 2*self.DELTA,                      'TEMP', 36.8),
            (start_of_sampling + self.DELTA,                        'SPO2', 99.5),
        ]

        unsampled_measurements = pd.DataFrame(data, columns=['Date', 'Type', 'Value'])
        sampled_measurements = sample(start_of_sampling, unsampled_measurements)

        self.assertLength(sampled_measurements, 3)
        self.assertLengthType(sampled_measurements, 'TEMP', 2)
        self.assertLengthType(sampled_measurements, 'SPO2', 1)

        self.assertValueEqual(sampled_measurements, 'TEMP', 0, 37.0)
        self.assertValueEqual(sampled_measurements, 'TEMP', 1, 36.8)
        self.assertValueEqual(sampled_measurements, 'SPO2', 0, 99.5)

    def test_measurements_before_sampling_start(self):
        start_of_sampling = pd.to_datetime('2017-01-03T10:00:00')

        data = [
            (start_of_sampling - self.DELTA,                        'TEMP', 99.5),
            (start_of_sampling - self.DELTA + timedelta(seconds=1), 'TEMP', 99.6),
            (start_of_sampling - timedelta(seconds=1),              'SPO2', 99.7),
        ]

        unsampled_measurements = pd.DataFrame(data, columns=['Date', 'Type', 'Value'])

        sampled_measurements = sample(start_of_sampling, unsampled_measurements)

        self.assertLength(sampled_measurements, 2)
        self.assertLengthType(sampled_measurements, 'TEMP', 1)
        self.assertLengthType(sampled_measurements, 'SPO2', 1)
        self.assertValueEqual(sampled_measurements, 'TEMP', 0, 99.6)
        self.assertValueEqual(sampled_measurements, 'SPO2', 0, 99.7)

    def test_measurements_on_sampling_start_time(self):
        start_of_sampling = pd.to_datetime('2017-01-03T10:00:00')

        data = [
            (start_of_sampling, 'TEMP', 99.5),
        ]

        unsampled_measurements = pd.DataFrame(data, columns=['Date', 'Type', 'Value'])

        sampled_measurements = sample(start_of_sampling, unsampled_measurements)

        self.assertLength(sampled_measurements, 1)
        self.assertLengthType(sampled_measurements, 'TEMP', 1)
        self.assertLengthType(sampled_measurements, 'SPO2', 0)
        self.assertValueEqual(sampled_measurements, 'TEMP', 0, 99.5)

    def test_measurements_single_before_sampling_start_time(self):
        start_of_sampling = pd.to_datetime('2017-01-03T10:00:00')

        data = [
            (start_of_sampling - 2*self.DELTA, 'TEMP', 99.5),
        ]

        unsampled_measurements = pd.DataFrame(data, columns=['Date', 'Type', 'Value'])

        sampled_measurements = sample(start_of_sampling, unsampled_measurements)

        self.assertLength(sampled_measurements, 0)
        self.assertLengthType(sampled_measurements, 'TEMP', 0)
        self.assertLengthType(sampled_measurements, 'SPO2', 0)

    def test_wrong_date_column_type(self):
            wrong_date_type_df = pd.DataFrame({
                'Date': ['2021-01-01', '2021-01-02'],
                'Type': ['A', 'B'],
                'Value': [10, 20]
            })

            start_of_sampling = pd.to_datetime('2021-01-01')

            with self.assertRaises(AssertionError) as e:
                sample(start_of_sampling, wrong_date_type_df)

            self.assertIn("The 'Date' column must be of datetime data type.", str(e.exception))
            
if __name__ == '__main__':
    unittest.main()
