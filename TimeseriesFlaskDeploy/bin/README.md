# Time Series Model Service Client

A command-line client to interact with the Time Series Model Service.

## Overview

This client exercises all endpoints of the Time Series Model Service:
- `/version` - Get service version information
- `/example` - Get example time series data
- `/train` - Train a new model
- `/validation/<model_id>` - Validate a trained model
- `/predict` - Make predictions with a trained model

## Requirements

The client requires the following Python packages:
- `requests`
- `pandas`

These are already included in the project's Poetry dependencies.

## Usage

### Basic Commands

```bash
# Run the complete workflow
./client.py --workflow

# Use a custom service URL
./client.py --url http://localhost:8085 --workflow

# Save results to a directory
./client.py --workflow --output-dir ./results
```

### Individual Actions

```bash
# Get service version
./client.py --version

# Get example data
./client.py --example

# Train a model using example data
./client.py --train

# Validate a specific model
./client.py --validate --model-id <model_id>

# Make predictions with a model
./client.py --predict --model-id <model_id> --periods 365
```

### Using with Docker Compose

If you've deployed the service with docker-compose:

```bash
# First, start the service
cd /home/scott/Working/Deploy-ML-Models/TimeseriesFlaskDeploy
docker-compose up -d

# Then run the client
./bin/client.py --url http://localhost:8085 --workflow
```

### Command-Line Options

- `--url URL` - Base URL for the service (default: http://localhost:8085)
- `--timeout SECONDS` - Request timeout in seconds (default: 120)
- `--output-dir DIR` - Directory to save results
- `--workflow` - Run complete workflow
- `--version` - Get service version only
- `--example` - Get example data only
- `--train` - Train a model using example data
- `--validate` - Validate a model (requires --model-id)
- `--predict` - Make predictions (requires --model-id)
- `--model-id ID` - Model ID for validate/predict actions
- `--periods N` - Number of periods to predict (default: 180)

## Workflow

The complete workflow performs these steps:

1. **Get Version** - Retrieves service version information
2. **Get Example Data** - Fetches example time series data from the service
3. **Train Model** - Trains a new Prophet model with the example data
4. **Validate Model** - Performs cross-validation on the trained model
5. **Make Predictions** - Generates predictions for 180 future periods

## Output

When using `--output-dir`, the client saves:
- `results_<timestamp>.json` - Complete results from all steps
- `model_id_<timestamp>.txt` - Model ID for future reference
- `predictions_<timestamp>.json` - Prediction results (when using --predict)

## Examples

### Complete Workflow

```bash
./client.py --workflow --output-dir ./test_results
```

Output:
```
============================================================
STEP 1: Get Service Version
============================================================
Getting service version...
Service Version: {'version': '0.2.1', 'date': '2022-06-14T21:48'}

============================================================
STEP 2: Get Example Data
============================================================
Fetching example data...
Received 2905 data points

============================================================
STEP 3: Train Model
============================================================
Training model...
Model trained successfully!
  Model ID: 6702dd911e31c013c48dab4cf15baac1e3d2460e
  Training time: 12.193 seconds
  Data size: [2905, 2]

============================================================
STEP 4: Validate Model
============================================================
Validating model 6702dd911e31c013c48dab4cf15baac1e3d2460e...
Validation complete!
  Metrics available: ['mse', 'rmse', 'mae', 'mape', 'mdape', 'smape', 'coverage']

============================================================
STEP 5: Make Predictions
============================================================
Making predictions with model 6702dd911e31c013c48dab4cf15baac1e3d2460e...
  Predicting 180 periods forward
Predictions generated!
  Data points: 180
  Columns: ['ds', 'yhat', 'yhat_lower', 'yhat_upper']

Saving results to ./test_results/results_20220615_143022.json...
Model ID saved to ./test_results/model_id_20220615_143022.txt

============================================================
WORKFLOW COMPLETE
============================================================
Model ID: 6702dd911e31c013c48dab4cf15baac1e3d2460e
```

### Train and Predict Separately

```bash
# Train a model and save the model ID
./client.py --train > model_output.txt

# Extract model ID from output
MODEL_ID=$(grep "Model ID:" model_output.txt | cut -d' ' -f3)

# Make predictions with the model
./client.py --predict --model-id $MODEL_ID --periods 365 --output-dir ./predictions
```

## Error Handling

The client provides clear error messages for common issues:
- Connection errors (service not running)
- Timeout errors (long-running operations)
- HTTP errors (invalid requests)
- Missing required parameters

## Integration

You can also import the `TimeSeriesClient` class in your own Python scripts:

```python
from client import TimeSeriesClient

# Create client
client = TimeSeriesClient('http://localhost:8085')

# Run workflow
results = client.run_full_workflow(output_dir='./my_results')

# Or use individual methods
version = client.get_version()
data = client.get_example_data()
training = client.train_model(data)
```
