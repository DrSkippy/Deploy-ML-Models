#!/usr/bin/env python3
"""
Time Series Model Service Client

A client to exercise the Time Series Model Service.
Based on the "Use the Service" section from Time Series Model Deploy Brownbag.ipynb
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


class TimeSeriesClient:
    """Client for interacting with the Time Series Model Service."""

    def __init__(self, base_url, timeout=120):
        """
        Initialize the client.

        Args:
            base_url: Base URL for the service (e.g., 'http://localhost:8085')
            timeout: Request timeout in seconds (default: 120)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def get_version(self):
        """Get the service version information."""
        print("Getting service version...")
        url = f"{self.base_url}/version"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        print(f"Service Version: {data}")
        return data

    def get_example_data(self):
        """Get example time series data from the service."""
        print("Fetching example data...")
        url = f"{self.base_url}/example"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        print(f"Received {len(data.get('data', []))} data points")
        return data

    def train_model(self, training_data):
        """
        Train a new model with the provided data.

        Args:
            training_data: Dictionary with 'header' and 'data' keys

        Returns:
            Dictionary with model_id and training metrics
        """
        print("Training model...")
        url = f"{self.base_url}/train"
        response = requests.post(url, json=training_data, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        print(f"Model trained successfully!")
        print(f"  Model ID: {result.get('model_id')}")
        print(f"  Training time: {result.get('training_time', 'N/A')} seconds")
        print(f"  Data size: {result.get('size', 'N/A')}")
        return result

    def validate_model(self, model_id):
        """
        Perform cross-validation on a trained model.

        Args:
            model_id: The ID of the model to validate

        Returns:
            Dictionary with validation metrics
        """
        print(f"Validating model {model_id}...")
        url = f"{self.base_url}/validation/{model_id}"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        print(f"Validation complete!")
        if 'metrics' in result:
            print(f"  Metrics available: {list(result['metrics'].keys())}")
        return result

    def predict(self, model_id, size=180, data=None):
        """
        Make predictions using a trained model.

        Args:
            model_id: The ID of the model to use
            size: Number of future periods to predict (default: 180)
            data: Optional historical data for prediction base

        Returns:
            Dictionary with prediction results
        """
        print(f"Making predictions with model {model_id}...")
        print(f"  Predicting {size} periods forward")
        url = f"{self.base_url}/predict"
        payload = {
            "model_id": model_id,
            "size": size,
            "data": data or []
        }
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        print(f"Predictions generated!")
        print(f"  Data points: {len(result.get('data', []))}")
        print(f"  Columns: {result.get('header', [])}")
        return result

    def run_full_workflow(self, output_dir=None):
        """
        Run a complete workflow: version, example, train, validate, predict.

        Args:
            output_dir: Optional directory to save results
        """
        results = {}

        # Step 1: Get version
        print("\n" + "=" * 60)
        print("STEP 1: Get Service Version")
        print("=" * 60)
        results['version'] = self.get_version()

        # Step 2: Get example data
        print("\n" + "=" * 60)
        print("STEP 2: Get Example Data")
        print("=" * 60)
        example_data = self.get_example_data()
        results['example_data'] = example_data

        # Step 3: Train model
        print("\n" + "=" * 60)
        print("STEP 3: Train Model")
        print("=" * 60)
        training_result = self.train_model(example_data)
        model_id = training_result['model_id']
        results['training'] = training_result

        # Step 4: Validate model
        print("\n" + "=" * 60)
        print("STEP 4: Validate Model")
        print("=" * 60)
        validation_result = self.validate_model(model_id)
        results['validation'] = validation_result

        # Step 5: Make predictions
        print("\n" + "=" * 60)
        print("STEP 5: Make Predictions")
        print("=" * 60)
        prediction_result = self.predict(model_id, size=180)
        results['predictions'] = prediction_result

        # Save results if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = output_path / f"results_{timestamp}.json"

            print(f"\nSaving results to {results_file}...")
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)

            # Save model_id separately for easy reference
            model_id_file = output_path / f"model_id_{timestamp}.txt"
            with open(model_id_file, 'w') as f:
                f.write(model_id)

            print(f"Model ID saved to {model_id_file}")

        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETE")
        print("=" * 60)
        print(f"Model ID: {model_id}")

        return results


def main():
    """Main entry point for the client."""
    parser = argparse.ArgumentParser(
        description='Time Series Model Service Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow with default URL (localhost)
  %(prog)s --workflow

  # Run full workflow with custom URL
  %(prog)s --url http://192.168.127.8/ts-model --workflow

  # Get version only
  %(prog)s --version

  # Train a model using example data
  %(prog)s --train

  # Make predictions with a specific model
  %(prog)s --predict --model-id 6702dd911e31c013c48dab4cf15baac1e3d2460e --periods 365

  # Validate a model
  %(prog)s --validate --model-id 6702dd911e31c013c48dab4cf15baac1e3d2460e
        """
    )

    parser.add_argument(
        '--url',
        default='http://localhost:8085',
        help='Base URL for the service (default: http://localhost:8085)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=120,
        help='Request timeout in seconds (default: 120)'
    )

    parser.add_argument(
        '--output-dir',
        help='Directory to save results (optional)'
    )

    # Actions
    action_group = parser.add_argument_group('actions')
    action_group.add_argument(
        '--workflow',
        action='store_true',
        help='Run complete workflow (version, example, train, validate, predict)'
    )
    action_group.add_argument(
        '--version',
        action='store_true',
        help='Get service version'
    )
    action_group.add_argument(
        '--example',
        action='store_true',
        help='Get example data'
    )
    action_group.add_argument(
        '--train',
        action='store_true',
        help='Train a model using example data'
    )
    action_group.add_argument(
        '--validate',
        action='store_true',
        help='Validate a model (requires --model-id)'
    )
    action_group.add_argument(
        '--predict',
        action='store_true',
        help='Make predictions (requires --model-id)'
    )

    # Parameters
    param_group = parser.add_argument_group('parameters')
    param_group.add_argument(
        '--model-id',
        help='Model ID for validate/predict actions'
    )
    param_group.add_argument(
        '--periods',
        type=int,
        default=180,
        help='Number of periods to predict (default: 180)'
    )

    args = parser.parse_args()

    # Create client
    client = TimeSeriesClient(args.url, args.timeout)

    try:
        # Execute requested action
        if args.workflow:
            client.run_full_workflow(args.output_dir)
        elif args.version:
            client.get_version()
        elif args.example:
            data = client.get_example_data()
            print(json.dumps(data, indent=2))
        elif args.train:
            example_data = client.get_example_data()
            result = client.train_model(example_data)
            print(f"\nModel ID: {result['model_id']}")
        elif args.validate:
            if not args.model_id:
                print("Error: --model-id is required for validation", file=sys.stderr)
                sys.exit(1)
            client.validate_model(args.model_id)
        elif args.predict:
            if not args.model_id:
                print("Error: --model-id is required for predictions", file=sys.stderr)
                sys.exit(1)
            result = client.predict(args.model_id, args.periods)
            if args.output_dir:
                output_path = Path(args.output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pred_file = output_path / f"predictions_{timestamp}.json"
                with open(pred_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\nPredictions saved to {pred_file}")
        else:
            parser.print_help()
            sys.exit(1)

    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to service at {args.url}", file=sys.stderr)
        print("Make sure the service is running and the URL is correct.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"\nError: Request timed out after {args.timeout} seconds", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
