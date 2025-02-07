import os
import json
import pandas as pd
import os
import datetime
import yaml

from modularpy.io import SerialWorker
    
class ExperimentConfig:
    """## Generate and store parameters loaded from a JSON file. 
    
    #### Example Usage:
    ```python
    config = ExperimentConfig()
    # create dict and pandas DataFrame from JSON file path:
    config.load_parameters('path/to/json_file.json')
        
    config._save_dir = './output'
    config.subject = '001'
    config.task = 'TestTask'
    config.notes.append('This is a test note.')

    # Update a parameter
    config.update_parameter('new_param', 'test_value')

    # Save parameters and notes
    config.save_configuration()
    ```
    """

    def __init__(self, path: str):
        self._parameters: dict = {}
        self._json_file_path = ''
        self._output_path = ''
        self._save_dir = ''

        self.hardware = HardwareManager(path)
        
        self.notes: list = []

    @property
    def encoder(self) -> SerialWorker:
        return self.hardware.encoder

    @property
    def save_dir(self) -> str:
        return os.path.join(self._save_dir, 'data')

    @save_dir.setter
    def save_dir(self, path: str):
        if isinstance(path, str):
            self._save_dir = os.path.abspath(path)
        else:
            print(f"ExperimentConfig: \n Invalid save directory path: {path}")

    @property
    def subject(self) -> str:
        return self._parameters.get('subject', 'sub')

    @property
    def session(self) -> str:
        return self._parameters.get('session', 'ses')

    @property
    def task(self) -> str:
        return self._parameters.get('task', 'task')
    
    @property
    def parameters(self) -> dict:
        return self._parameters
        
    @property
    def bids_dir(self) -> str:
        """ Dynamic construct of BIDS directory path """
        bids = os.path.join(
            f"sub-{self.subject}",
            f"ses-{self.session}",
        )
        return os.path.abspath(os.path.join(self.save_dir, bids))

    @property
    def notes_file_path(self):
        return self._generate_unique_file_path(suffix="notes", extension="txt")
    
    @property
    def encoder_file_path(self):
        return self._generate_unique_file_path(suffix="encoder-data", extension="csv", bids_type='beh')
    
    @property
    def dataframe(self):
        data = {'Parameter': list(self._parameters.keys()),
                'Value': list(self._parameters.values())}
        return pd.DataFrame(data)
    
    @property
    def json_path(self):
        return self._json_file_path
    
    # Helper method to generate a unique file path
    def _generate_unique_file_path(self, suffix: str, extension: str, bids_type: str = None):
        """ Example:
        ```py
            ExperimentConfig._generate_unique_file_path("images", "jpg", "func")
            print(unique_path)
        ```
        Output:
            C:/save_dir/data/sub-id/ses-id/func/20250110_123456_sub-001_ses-01_task-example_images.jpg
        """
        file = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_sub-{self.subject}_ses-{self.session}_task-{self.task}_{suffix}.{extension}"

        if bids_type is None:
            bids_path = self.bids_dir
        else:
            bids_path = os.path.join(self.bids_dir, bids_type)
            
        os.makedirs(bids_path, exist_ok=True)
        base, ext = os.path.splitext(file)
        counter = 1
        file_path = os.path.join(bids_path, file)
        while os.path.exists(file_path):
            file_path = os.path.join(bids_path, f"{base}_{counter}{ext}")
            counter += 1
        return file_path
        
    def load_parameters(self, json_file_path) -> None:
        """ Load parameters from a JSON file path into the config object. 
        """
        try:
            with open(json_file_path, 'r') as f: 
                self._parameters = json.load(f)
        except FileNotFoundError:
            print(f"File not found: {json_file_path}")
            return
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

    def update_parameter(self, key, value) -> None:
        self._parameters[key] = value
        
    def list_parameters(self) -> pd.DataFrame:
        """ Create a DataFrame from the ExperimentConfig properties 
        """
        properties = [prop for prop in dir(self.__class__) if isinstance(getattr(self.__class__, prop), property)]
        exclude_properties = {'dataframe', 'parameters', 'json_path', "_cores", "meso_sequence", "pupil_sequence", "psychopy_path", "encoder"}
        data = {prop: getattr(self, prop) for prop in properties if prop not in exclude_properties}
        return pd.DataFrame(data.items(), columns=['Parameter', 'Value'])
                
    def save_wheel_encoder_data(self, data):
        """ Save the wheel encoder data to a CSV file 
        """
        if isinstance(data, list):
            data = pd.DataFrame(data)
           
        try:
            data.to_csv(self.encoder_file_path, index=False)
            print(f"Encoder data saved to {self.encoder_file_path}")
        except Exception as e:
            print(f"Error saving encoder data: {e}")
            
    def save_configuration(self):
        """ Save the configuration parameters to a CSV file 
        """
        params_path = self._generate_unique_file_path(suffix="configuration", extension="csv")
        
        # Save the configuration parameters to a CSV file
        try:
            params = self.list_parameters()
            params.to_csv(params_path, index=False)
            print(f"Configuration saved to {params_path}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
        
        # Save the notes to a text file
        try:
            with open(self.notes_file_path, 'w') as f:
                f.write('\n'.join(self.notes))
                print(f"Notes saved to {self.notes_file_path}")
        except Exception as e:
            print(f"Error saving notes: {e}")
                    


class HardwareManager:
    """ High-level class that initializes all hardware (cameras, encoder, etc.) from a yaml configuration file.
    
    #### Example Usage:
    ```python
    hardware = HardwareManager('path/to/config.yaml')
    encoder = hardware.encoder
    ```

    """

    def __init__(self, config_file: str):
        self.yaml = self._load_hardware_from_yaml(config_file)
        self._initialize_encoder()       
        

    def shutdown(self):
        self.encoder.stop()
    

    def _load_hardware_from_yaml(self, path):
        params = {}

        if not path:
            raise FileNotFoundError(f"Cannot find config file at: {path}")

        with open(path, "r", encoding="utf-8") as file:
            params = yaml.safe_load(file) or {}
            
        return params
            
            
    def _initialize_encoder(self):
        if self.yaml.get("encoder"):
            params = self.yaml.get("encoder")
            self.encoder = SerialWorker(
                serial_port=params.get('port'),
                baud_rate=params.get('baudrate'),
                sample_interval=params.get('sample_interval_ms'),
                wheel_diameter=params.get('diameter_mm'),
                cpr=params.get('cpr'),
                development_mode=params.get('development_mode')
            )
         

