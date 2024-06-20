Checkpoint Uploading/Downloading Automation
Introduction
When benchmarking machine learning (ML) models, it is often necessary to use pre-trained checkpoints to ensure that the model has already been trained to a certain level of performance. The benchmarking module provides functionality to automatically download the appropriate pre-trained checkpoints for the ML models being benchmarked from various sources such as wandb artifacts or AWS S3 buckets. It also provides functionality to upload the checkpoints to the same sources.

Prerequisites
The user should have access to pre-trained checkpoints either on wandb artifacts or on AWS S3 buckets.
The user should have authorization to upload the checkpoints to wandb artifacts or to the AWS S3 bucket.
Downloading Checkpoints
The user can use the following command to download the checkpoint from wandb artifacts.
Copy code
    from benchmarking_module import CheckpointDownloader

    downloader = CheckpointDownloader()
    downloader.download_from_wandb(run_id="run_id")
The user can use the following command to download the checkpoint from an AWS S3 bucket.
Copy code
    from benchmarking_module import CheckpointDownloader

    downloader = CheckpointDownloader()
    downloader.download_from_s3(bucket_name="bucket_name", checkpoint_path="path/to/checkpoint")
Uploading Checkpoints
The user can use the following command to upload the checkpoint to wandb artifacts.
Copy code
    from benchmarking_module import CheckpointUploader

    uploader = CheckpointUploader()
    uploader.upload_to_wandb(run_id="run_id", checkpoint_path="path/to/checkpoint")
The user can use the following command to upload the checkpoint to an AWS S3 bucket.
Copy code
    from benchmarking_module import CheckpointUploader

    uploader = CheckpointUploader()
    uploader.upload_to_s3(bucket_name="bucket_name", checkpoint_path="path/to/checkpoint")
Conclusion
The benchmarking module provides functionality for automatically downloading and uploading pre-trained checkpoints for ML models being benchmarked. This allows the user to easily access the necessary checkpoints without having to manually find and download them. It also enables the user to upload the checkpoints to the same sources they can download from which can be useful if they want to share the checkpoints with others.